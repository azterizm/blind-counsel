"""Apply the user's decision rule to design (a), using the measured attacks.

Rule (fixed before running):
  * (a) FAILS if any attack recovers >= 10% of the SECRET test tokens.
  * The primary count excludes the top-200 public stopwords (frequency analysis
    gets those for free; they are ~20-25% of English and reveal nothing).
  * Names/amounts/dates alone are not secrets; reported for information only.
  * If every attack stays < 10% content, verdict is "(a) survived round 1".

This module runs the three implemented attacks over the engraving drift sweep and
prints a single PASS/FAIL per the content-token criterion.
"""
from __future__ import annotations

import glob
import os
import re

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from keyed import data
from keyed.keygen import KeyBundle
from . import weights_align as wa
from . import traffic

ART = data.ART
THRESHOLD = 10.0  # percent of secret content tokens


def main():
    tok = AutoTokenizer.from_pretrained(wa.NAME)
    E_base = wa.public_base_embed()
    kb = KeyBundle.load(os.path.join(ART, "key.pt"))
    secret = data.build_secret_test()
    stop_ids = wa.stopword_ids(tok, 200)

    paths = sorted(glob.glob(os.path.join(ART, "engraved_E1_ckpts", "embed_step*.pt")),
                   key=lambda p: int(re.search(r"step(\d+)", p).group(1)))

    worst = 0.0
    worst_desc = ""
    print(f"{'step':>6} | {'A norm cont%':>12} | {'B cov+NN cont%':>14}")
    print("-" * 42)
    for p in paths:
        step, pi_acc, secA, secB = wa.run_checkpoint(p, E_base, kb, tok, secret, stop_ids)
        print(f"{step:>6} | {secA['content_pct']:>11.1f}% | {secB['content_pct']:>13.1f}%")
        for name, sec in (("A norm-sort", secA), ("B covariance+NN", secB)):
            if sec["content_pct"] > worst:
                worst = sec["content_pct"]; worst_desc = f"{name} @ step {step}"

    # ciphertext-only traffic attack (weights-independent)
    tr = traffic.main()
    if tr["content_pct"] > worst:
        worst = tr["content_pct"]; worst_desc = "ciphertext traffic (unigram)"

    print("\n" + "=" * 60)
    print(f"best attack: {worst_desc} -> {worst:.1f}% secret content recovered")
    if worst >= THRESHOLD:
        print(f"VERDICT: design (a) FAILS (>= {THRESHOLD:.0f}% content recovered).")
    else:
        print(f"VERDICT: (a) survived round 1 (all attacks < {THRESHOLD:.0f}% content).")
    print("=" * 60)


if __name__ == "__main__":
    main()
