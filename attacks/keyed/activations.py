"""Attack #3: read the model's runtime hidden states (the "reasoning"), not just
its input/output tokens.

At serve time the operator sees the residual stream of the engraved model. The
shift rotates the residual by R (and folds the norms), so the operator sees
h_shift = h_base @ R at every layer. Having recovered R from the public-vs-engraved
weights (the covariance attack, attacks.keyed.weights_align.recover_R_covariance),
the operator un-rotates:  h_base = h_shift @ R^T, and applies the PUBLIC base
model's logit lens (its lm_head/embedding) to decode what the model is computing
at each position and layer -- in plaintext.

This shows the leak is not limited to the token streams: the intermediate
computation on the firm's data is also readable. "Anything the model can read,
whoever holds the model can read."
"""
from __future__ import annotations

import os

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from keyed import data
from keyed.keygen import KeyBundle
from .weights_align import public_base_embed, recover_R_covariance

NAME = "HuggingFaceTB/SmolLM2-135M"
ART = data.ART


@torch.no_grad()
def logit_lens_decode(h_base_rows, E_base, topk=1):
    """Nearest-neighbour of each (un-rotated) hidden row against the base embed table
    = the token each residual position most resembles (a crude logit lens)."""
    bn = (E_base * E_base).sum(1)
    d = bn[None, :] - 2.0 * (h_base_rows @ E_base.T)
    return d.argmin(1)


@torch.no_grad()
def main(model_dir=None):
    model_dir = model_dir or os.path.join(ART, "engraved_E1_final")
    if not os.path.exists(os.path.join(model_dir, "config.json")):
        model_dir = os.path.join(ART, "shifted_clean")
    tok = AutoTokenizer.from_pretrained(NAME)
    kb = KeyBundle.load(os.path.join(ART, "key.pt"))
    E_base = public_base_embed()

    model = AutoModelForCausalLM.from_pretrained(model_dir, dtype=torch.float32)
    model.eval()
    E_shift = model.model.embed_tokens.weight.detach().double()
    R_hat = recover_R_covariance(E_base, E_shift)

    # the firm sends an encoded query; the operator captures the hidden states
    secret = "the settlement figure of $70,000 must remain sealed"
    ids = torch.tensor([tok(secret, add_special_tokens=False).input_ids])
    enc = kb.pi[ids]                                 # firm encoding
    out = model(enc, output_hidden_states=True)
    hs = out.hidden_states                            # tuple [L+1] of [1,T,H] (rotated)

    print(f"model dir: {os.path.basename(model_dir)}")
    print(f"secret query: {secret!r}\n")
    # decode the embedding-layer residual (layer 0) by un-rotating + logit lens
    for layer in (0, len(hs) // 2, len(hs) - 1):
        h = hs[layer][0].double() @ R_hat.T          # un-rotate to base frame
        guess = logit_lens_decode(h, E_base)
        txt = tok.decode(guess.tolist())
        print(f"  layer {layer:>2} logit-lens read: {txt!r}")

    # input-layer read should reconstruct the prompt tokens (strongest signal)
    h0 = hs[0][0].double() @ R_hat.T
    recon = logit_lens_decode(h0, E_base)
    true_ids = ids[0]
    acc = (recon == true_ids).float().mean().item() * 100
    print(f"\n  layer-0 token reconstruction accuracy: {acc:.1f}%  "
          f"-> {tok.decode(recon.tolist())!r}")


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else None)
