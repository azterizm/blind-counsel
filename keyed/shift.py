"""Firm-side weight shift: apply the key as an *exact* symmetry of the model.

This is the step the firm runs on its own machine (no training, just linear
algebra), so the lab never sees the key being applied. We compose four symmetries
of a Llama-style transformer:

  1. gamma-fold : fold each RMSNorm weight into the linear it feeds, set gamma=1.
                  (makes the normalization a bare RMS, which commutes with a rotation)
  2. R rotation : the residual stream becomes  s = r @ R   for orthogonal R.
                  input-reading linears -> W @ R ; output-writing linears -> R^T @ W.
  3. sigma perm : permute the MLP intermediate dimension, per layer.
  4. head perm  : permute attention heads (KV groups kept intact), per layer.
  5. pi perm    : relabel the vocabulary (rows of embedding and lm_head).

After the shift, running the model on pi-encoded ids and reading logits at pi(v)
reproduces the base model's logits for v, to float precision. `verify()` asserts it.

Convention: torch Linear stores weight [out, in], computes y = x @ W^T. Hidden
states are row vectors; the shifted residual is s = r @ R.
"""
from __future__ import annotations

import torch

from .keygen import KeyBundle


@torch.no_grad()
def _fold_rmsnorm_into(norm_weight: torch.Tensor, *linears: torch.nn.Linear) -> None:
    """Fold a RMSNorm gamma into the columns of each consuming linear, then set gamma=1."""
    g = norm_weight.double()
    for lin in linears:
        lin.weight.data = (lin.weight.data.double() * g[None, :]).to(lin.weight.dtype)
    norm_weight.data = torch.ones_like(norm_weight)


@torch.no_grad()
def untie_lm_head(model) -> None:
    """SmolLM2 ties lm_head to embed_tokens; we need an independent lm_head to fold
    the final norm and to permute the vocab on the output side separately."""
    emb = model.model.embed_tokens.weight.data.clone()
    model.lm_head.weight = torch.nn.Parameter(emb)
    model.config.tie_word_embeddings = False


@torch.no_grad()
def shift_model(model, kb: KeyBundle) -> None:
    """Apply the full keyed shift to `model` in place. Model must already be untied."""
    m = model.model
    cfg = model.config
    H, I = cfg.hidden_size, cfg.intermediate_size
    nh, nkv, hd = cfg.num_attention_heads, cfg.num_key_value_heads, cfg.head_dim
    R = kb.Q.double()
    pi_inv = kb.pi_inv

    def rotate_in(lin):   # reads residual: W @ R
        lin.weight.data = (lin.weight.data.double() @ R).to(lin.weight.dtype)

    def rotate_out(lin):  # writes residual: R^T @ W
        lin.weight.data = (R.T @ lin.weight.data.double()).to(lin.weight.dtype)

    def perm_rows(lin, idx):
        lin.weight.data = lin.weight.data[idx].contiguous()

    def perm_cols(lin, idx):
        lin.weight.data = lin.weight.data[:, idx].contiguous()

    # ---- per layer: fold norms, rotate, permute MLP + heads ---------------------
    for l, layer in enumerate(m.layers):
        attn, mlp = layer.self_attn, layer.mlp

        # 1. fold the two block norms into the linears they feed
        _fold_rmsnorm_into(layer.input_layernorm.weight, attn.q_proj, attn.k_proj, attn.v_proj)
        _fold_rmsnorm_into(layer.post_attention_layernorm.weight, mlp.gate_proj, mlp.up_proj)

        # 2. residual rotation on everything touching the residual stream
        rotate_in(attn.q_proj); rotate_in(attn.k_proj); rotate_in(attn.v_proj)
        rotate_out(attn.o_proj)
        rotate_in(mlp.gate_proj); rotate_in(mlp.up_proj)
        rotate_out(mlp.down_proj)

        # 3. MLP intermediate permutation: rows of gate/up, cols of down
        s = kb.sigma[l]
        perm_rows(mlp.gate_proj, s); perm_rows(mlp.up_proj, s); perm_cols(mlp.down_proj, s)

        # 4. head permutation. head perm h maps new head i <- old head h[i].
        h = kb.head[l]
        per = nh // nkv
        kv_order = torch.tensor([int(h[g * per]) // per for g in range(nkv)], dtype=torch.long)
        q_row = (h.view(nh, 1) * hd + torch.arange(hd)).reshape(-1)       # [nh*hd]
        kv_row = (kv_order.view(nkv, 1) * hd + torch.arange(hd)).reshape(-1)  # [nkv*hd]
        perm_rows(attn.q_proj, q_row)
        perm_rows(attn.k_proj, kv_row)
        perm_rows(attn.v_proj, kv_row)
        perm_cols(attn.o_proj, q_row)   # o_proj input is concat of head outputs

    # ---- final norm -> lm_head, then rotation + vocab permutation ----------------
    _fold_rmsnorm_into(m.norm.weight, model.lm_head)
    rotate_in(model.lm_head)               # lm_head reads final residual
    rotate_in(m.embed_tokens)              # embed writes residual: new_E = (E @ R)...
    # embed_tokens is used as a lookup table (rows = tokens), so "rotate_in" above
    # multiplied E @ R on the hidden axis, which is exactly what we want for the
    # row that becomes the residual. Now relabel vocab on the row axis:
    m.embed_tokens.weight.data = m.embed_tokens.weight.data[pi_inv].contiguous()
    model.lm_head.weight.data = model.lm_head.weight.data[pi_inv].contiguous()


@torch.no_grad()
def verify(base_model, shifted_model, kb: KeyBundle, n_tokens: int = 64,
           abs_tol: float = 2e-3, cos_tol: float = 0.9999):
    """Assert the shift preserves the function: shifted(pi(ids))[:,pi] == base(ids).

    The symmetry is exact up to floating point. The hard gates are therefore
    argmax agreement (generation is byte-identical) and per-position cosine ~1.
    |Δlogit| is reported as a diagnostic: in float32 inference it sits ~1e-3
    (30 layers of accumulation; RoPE/softmax run in float32 internally), and in
    float64 it drops ~100x, which is the signature of a numerical, not structural,
    residual.
    """
    torch.manual_seed(0)
    V = base_model.config.vocab_size
    ids = torch.randint(0, V, (1, n_tokens))
    enc = kb.pi[ids]                       # firm encodes input ids

    base_model.eval(); shifted_model.eval()
    base_logits = base_model(ids).logits[0].double()          # [T, V]
    shift_logits = shifted_model(enc).logits[0].double()      # [T, V] in shifted vocab
    # firm decodes: logit for token v sits at column pi[v]
    dec_logits = shift_logits[:, kb.pi]                       # back to base vocab order

    abs_err = (dec_logits - base_logits).abs().max().item()
    agree = (dec_logits.argmax(-1) == base_logits.argmax(-1)).float().mean().item()
    cos = torch.nn.functional.cosine_similarity(dec_logits, base_logits, dim=-1).mean().item()
    print(f"  max |Δlogit|      : {abs_err:.3e}   (float32 ~1e-3, float64 ~1e-5; diagnostic)")
    print(f"  argmax agreement  : {agree*100:.1f}%   (hard gate: 100%)")
    print(f"  mean cosine       : {cos:.6f}   (hard gate: >{cos_tol})")
    assert agree == 1.0, f"argmax disagrees on {(1-agree)*100:.1f}% of positions"
    assert cos > cos_tol, f"cosine {cos:.6f} <= {cos_tol}"
    assert abs_err < abs_tol, f"|Δlogit| {abs_err:.3e} >= {abs_tol:.0e} (unexpectedly large)"
    return dict(abs_err=abs_err, agree=agree, cos=cos)


if __name__ == "__main__":
    import hashlib
    from transformers import AutoModelForCausalLM, AutoConfig
    from .keygen import generate

    name = "HuggingFaceTB/SmolLM2-135M"
    print(f"loading {name} (x2: base + to-shift) ...")
    base = AutoModelForCausalLM.from_pretrained(name, torch_dtype=torch.float32)
    shifted = AutoModelForCausalLM.from_pretrained(name, torch_dtype=torch.float32)

    seed = hashlib.sha256(b"demo-firm-private-seed-0001").digest()
    kb = generate(seed, base.config)

    untie_lm_head(shifted)
    print("applying keyed shift ...")
    shift_model(shifted, kb)

    print("verifying exact function-preservation ...")
    verify(base, shifted, kb)
    print("OK: shift is an exact symmetry.")
