"""Attack B (covariance R + NN) against independent firm keys.

The main runs use one firm key (keyed.engrave's seed). This checks that the
result does not depend on that key: for each extra seed, shift the public base
model and run attack B on the clean upload.
"""
from __future__ import annotations

import hashlib

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from keyed import data
from keyed.keygen import generate
from keyed.shift import shift_model, untie_lm_head
from .weights_align import (public_base_embed, recover_R_covariance,
                            score_secret_via_R, stopword_ids)

NAME = "HuggingFaceTB/SmolLM2-135M"
SEEDS = [b"second-key-xyz", b"third-key-7788", b"fourth-abcd"]


def main() -> None:
    tok = AutoTokenizer.from_pretrained(NAME)
    E_base = public_base_embed()
    secret = data.build_secret_test()
    stop = stopword_ids(tok, 200)
    for seedtxt in SEEDS:
        model = AutoModelForCausalLM.from_pretrained(NAME, dtype=torch.float32)
        kb = generate(hashlib.sha256(seedtxt).digest(), model.config)
        untie_lm_head(model)
        shift_model(model, kb)
        Es = model.model.embed_tokens.weight.detach().double()
        R = recover_R_covariance(E_base, Es)
        sec = score_secret_via_R(kb, E_base, Es, R, tok, secret, stop)
        print(f"key {seedtxt.decode():14s}: attack B content {sec['content_pct']:.1f}%  "
              f"all {sec['all_pct']:.1f}%  run {sec['longest_run']}")


if __name__ == "__main__":
    main()
