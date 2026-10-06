"""Lab-side engraving: fine-tune the shifted model on pi-encoded firm data.

This is variant E1 (firm data frozen in at engraving). The lab holds the shifted
weights (an exact symmetry of the public base) and fine-tunes them on the firm's
contract text, encoded with pi. Fine-tuning is the ONLY thing that moves the
weights away from a clean symmetry, so it is the defender's only hope against the
weight-alignment attack. We checkpoint the embedding table along a drift sweep so
we can later plot pi-recovery vs. amount of fine-tuning.

Run:  python -m keyed.engrave            # builds clean shift, then fine-tunes
"""
from __future__ import annotations

import hashlib
import os
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from . import data
from .keygen import KeyBundle, generate
from .shift import shift_model, untie_lm_head, verify

ART = data.ART
NAME = "HuggingFaceTB/SmolLM2-135M"
SEED = hashlib.sha256(b"demo-firm-private-seed-0001").digest()
CKPT_STEPS = [0, 50, 120, 250, 400, 600, 1200]


def device() -> str:
    return "mps" if torch.backends.mps.is_available() else "cpu"


def prepare_clean() -> tuple[str, str]:
    """Build and save the key and the clean (pre-fine-tune) shifted model."""
    key_path = os.path.join(ART, "key.pt")
    clean_dir = os.path.join(ART, "shifted_clean")
    if os.path.exists(key_path) and os.path.exists(os.path.join(clean_dir, "config.json")):
        return key_path, clean_dir
    base = AutoModelForCausalLM.from_pretrained(NAME, dtype=torch.float32)
    shifted = AutoModelForCausalLM.from_pretrained(NAME, dtype=torch.float32)
    kb = generate(SEED, base.config)
    untie_lm_head(shifted)
    shift_model(shifted, kb)
    print("verifying clean shift before saving ...")
    verify(base, shifted, kb)
    os.makedirs(ART, exist_ok=True)
    kb.save(key_path)
    shifted.save_pretrained(clean_dir)
    AutoTokenizer.from_pretrained(NAME).save_pretrained(clean_dir)
    print(f"saved key -> {key_path}\nsaved clean shift -> {clean_dir}")
    return key_path, clean_dir


def encoded_blocks(kb: KeyBundle, tok, text: str, block: int = 512) -> torch.Tensor:
    """Tokenize firm text, apply pi (firm encoding), pack into [N, block] id blocks."""
    ids = tok(text, return_tensors="pt", add_special_tokens=False).input_ids[0]
    ids = kb.pi[ids]                                   # <-- the firm's pi encoding
    n = (ids.numel() // block) * block
    return ids[:n].view(-1, block)


def save_embed_ckpt(model, step: int, tag: str = "E1") -> None:
    d = os.path.join(ART, f"engraved_{tag}_ckpts")
    os.makedirs(d, exist_ok=True)
    torch.save(
        {"embed": model.model.embed_tokens.weight.detach().cpu().clone(),
         "lm_head": model.lm_head.weight.detach().cpu().clone(),
         "step": step},
        os.path.join(d, f"embed_step{step}.pt"),
    )


@torch.no_grad()
def embed_drift(model, clean_embed: torch.Tensor) -> dict:
    e = model.model.embed_tokens.weight.detach().cpu()
    delta = (e - clean_embed).norm(dim=1)
    rel = delta / clean_embed.norm(dim=1).clamp_min(1e-6)
    return dict(mean_rel=rel.mean().item(), median_rel=rel.median().item(),
               p90_rel=rel.quantile(0.9).item(), max_rel=rel.max().item())


@torch.no_grad()
def eval_perplexity(model, eval_blocks, dev, n: int = 32) -> float:
    model.eval()
    tot_loss, tot = 0.0, 0
    for i in range(0, min(n * 8, eval_blocks.shape[0]), 8):
        x = eval_blocks[i:i + 8].to(dev)
        loss = model(input_ids=x, labels=x).loss
        tot_loss += loss.item() * x.shape[0]; tot += x.shape[0]
    model.train()
    import math
    avg = tot_loss / max(tot, 1)
    return math.exp(avg) if avg < 50 else float("inf")


def engrave(lr: float = 1e-4, batch: int = 8, block: int = 256, max_steps: int = 1200,
            tag: str = "E1") -> str:
    key_path, clean_dir = prepare_clean()
    kb = KeyBundle.load(key_path)
    tok = AutoTokenizer.from_pretrained(clean_dir)
    dev = device()
    print(f"device: {dev}  | lr {lr} | batch {batch} | max_steps {max_steps}")

    model = AutoModelForCausalLM.from_pretrained(clean_dir, dtype=torch.float32).to(dev)
    model.train()
    clean_embed = model.model.embed_tokens.weight.detach().cpu().clone()

    blocks = encoded_blocks(kb, tok, data.fine_tune_text(), block=block)
    # held-out encoded eval blocks (encoded secret contract passages) for perplexity
    eval_text = "\n".join(data.build_secret_test()[200:])  # contract half
    eval_blocks = encoded_blocks(kb, tok, eval_text, block=block)
    print(f"fine-tune blocks: {tuple(blocks.shape)}  (~{blocks.numel():,} tokens, encoded)", flush=True)

    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.0)
    log = []
    t0 = time.time()
    step = 0
    save_embed_ckpt(model, 0, tag)             # step 0 = clean
    ppl0 = eval_perplexity(model, eval_blocks, dev)
    print(f"  step    0 | encoded held-out perplexity {ppl0:7.2f} (clean baseline)", flush=True)
    order = torch.randperm(blocks.shape[0])
    ptr = 0
    while step < max_steps:
        if ptr + batch > order.numel():
            order = torch.randperm(blocks.shape[0]); ptr = 0
        idx = order[ptr:ptr + batch]; ptr += batch
        x = blocks[idx].to(dev)
        out = model(input_ids=x, labels=x)
        loss = out.loss
        opt.zero_grad(); loss.backward()
        opt.step()
        step += 1
        if step % 50 == 0:
            dr = embed_drift(model, clean_embed)
            dt = time.time() - t0
            print(f"  step {step:4d} | loss {loss.item():5.2f} | "
                  f"embed drift mean_rel {dr['mean_rel']:.3f} p90 {dr['p90_rel']:.3f} | "
                  f"{step/dt:.2f} it/s", flush=True)
            log.append((step, loss.item(), dr))
        if step in CKPT_STEPS:
            save_embed_ckpt(model, step, tag)
            ppl = eval_perplexity(model, eval_blocks, dev)
            dr = embed_drift(model, clean_embed)
            print(f"  >>> ckpt step {step}: encoded perplexity {ppl:7.2f} "
                  f"(x{ppl/ppl0:.2f} baseline) | embed drift mean_rel {dr['mean_rel']:.3f}", flush=True)
    # final full model for layer-wise attacks
    final_dir = os.path.join(ART, f"engraved_{tag}_final")
    model.save_pretrained(final_dir)
    tok.save_pretrained(final_dir)
    torch.save(log, os.path.join(ART, f"engraved_{tag}_log.pt"))
    print(f"saved final engraved model -> {final_dir}")
    print(f"total engrave time: {(time.time()-t0)/60:.1f} min")
    return final_dir


if __name__ == "__main__":
    import sys
    steps = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
    lr = float(sys.argv[2]) if len(sys.argv) > 2 else 3e-4
    engrave(lr=lr, max_steps=steps)
