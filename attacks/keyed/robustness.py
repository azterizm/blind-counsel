"""The defender's dilemma, probed in a controlled way.

Fine-tuning's only protective effect against the covariance attack (B) is to
*move the embedding rows* (drift). This script decouples drift from training
dynamics: it adds synthetic per-row Gaussian noise of a chosen relative magnitude
to the clean shifted embedding, and at each level measures BOTH

  * the model's perplexity (is it still a usable model?), and
  * attack B's secret-content recovery (is pi still readable?).

If B only breaks at a noise level that also destroys perplexity, the design has
no usable-and-safe operating point. We also inject the noise into lm_head so the
perplexity number reflects a symmetric perturbation.
"""
from __future__ import annotations

import math
import os

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from keyed import data, engrave
from keyed.keygen import KeyBundle
from .weights_align import (public_base_embed, recover_R_covariance,
                            score_secret_via_R, stopword_ids)

NAME = "HuggingFaceTB/SmolLM2-135M"
ART = data.ART


@torch.no_grad()
def main():
    tok = AutoTokenizer.from_pretrained(NAME)
    kb = KeyBundle.load(os.path.join(ART, "key.pt"))
    E_base = public_base_embed()
    secret = data.build_secret_test()
    stop_ids = stopword_ids(tok, 200)
    dev = engrave.device()

    model = AutoModelForCausalLM.from_pretrained(os.path.join(ART, "shifted_clean"),
                                                 dtype=torch.float32).to(dev)
    E_clean = model.model.embed_tokens.weight.detach().cpu().double().clone()
    lm_clean = model.lm_head.weight.detach().cpu().double().clone()
    rownorm = E_clean.norm(dim=1, keepdim=True)

    eval_text = "\n".join(data.build_secret_test()[200:])
    eval_blocks = engrave.encoded_blocks(kb, tok, eval_text, block=256)
    ppl0 = engrave.eval_perplexity(model, eval_blocks, dev)

    torch.manual_seed(0)
    g = torch.randn_like(E_clean)
    g = g / g.norm(dim=1, keepdim=True)          # unit per-row -> ||noise|| = eps*||E||
    g_lm = torch.randn_like(lm_clean)
    g_lm = g_lm / g_lm.norm(dim=1, keepdim=True)

    print(f"clean baseline perplexity: {ppl0:.2f}\n")
    print(f"{'noise eps':>9} | {'drift mean_rel':>14} | {'perplexity':>11} "
          f"| {'x base':>7} | {'B content%':>10}")
    print("-" * 66)
    for eps in (0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4):
        E_noisy = E_clean + eps * rownorm * g
        drift = ((E_noisy - E_clean).norm(dim=1) / rownorm.squeeze().clamp_min(1e-6)).mean().item()
        # load noisy weights for perplexity
        model.model.embed_tokens.weight.data = E_noisy.float().to(dev)
        lm_noisy = lm_clean + eps * lm_clean.norm(dim=1, keepdim=True) * g_lm
        model.lm_head.weight.data = lm_noisy.float().to(dev)
        ppl = engrave.eval_perplexity(model, eval_blocks, dev)
        # attack B on the noisy embedding
        R_hat = recover_R_covariance(E_base, E_noisy)
        secB = score_secret_via_R(kb, E_base, E_noisy, R_hat, tok, secret, stop_ids)
        print(f"{eps:>9.2f} | {drift:>14.3f} | {ppl:>11.1f} | {ppl/ppl0:>6.1f}x "
              f"| {secB['content_pct']:>9.1f}%")


if __name__ == "__main__":
    main()
