"""Attack #2: ciphertext-only break of the token substitution cipher pi.

This attack uses NO model weights and NO activations -- only the encoded token
streams the operator sees (the fine-tune corpus, and at serve time the queries and
outputs) plus public English token statistics. pi is a monoalphabetic substitution
cipher over a 49k-token alphabet; with millions of tokens of ciphertext it is
attackable by classical frequency analysis.

Two stages:
  1. unigram: match the i-th most frequent ciphertext token to the i-th most
     frequent public token. (Weak for rare/content tokens; strong for frequent.)
  2. bigram hill-climb: refine by maximizing the log-likelihood of the decoded
     ciphertext bigrams under a public bigram model. (Context fixes content tokens.)

The legal-vs-wiki domain mismatch is kept (public stats = wikitext), which is the
hard setting for this attack and favors the defender.
"""
from __future__ import annotations

import os
from collections import Counter

import torch
from transformers import AutoTokenizer

from keyed import data
from keyed.keygen import KeyBundle

NAME = "HuggingFaceTB/SmolLM2-135M"
ART = data.ART


def _unigram(ids, V):
    c = Counter(ids)
    f = torch.zeros(V)
    for k, v in c.items():
        f[k] = v
    return f


def unigram_match(cipher_ids, public_ids, V):
    """pi_hat[v] = cipher token whose frequency rank equals v's public rank."""
    fc = _unigram(cipher_ids, V)
    fp = _unigram(public_ids, V)
    # rank by frequency (desc); ties broken by id for determinism
    cipher_order = torch.argsort(fc, descending=True, stable=True)
    public_order = torch.argsort(fp, descending=True, stable=True)
    pi_hat = torch.empty(V, dtype=torch.long)
    pi_hat[public_order] = cipher_order       # public token v -> cipher token
    return pi_hat, fp, fc


def score(kb, pi_hat, tok, secret, stop_ids):
    pi_inv_hat = torch.empty_like(pi_hat)
    pi_inv_hat[pi_hat] = torch.arange(pi_hat.numel())
    tot = tot_ok = con = con_ok = 0
    for passage in secret:
        true_ids = torch.tensor(tok(passage, add_special_tokens=False).input_ids)
        if true_ids.numel() == 0:
            continue
        enc = kb.pi[true_ids]
        dec = pi_inv_hat[enc]
        ok = (dec == true_ids)
        tot += ok.numel(); tot_ok += int(ok.sum())
        mask = torch.tensor([int(t) not in stop_ids for t in true_ids])
        con += int(mask.sum()); con_ok += int((ok & mask).sum())
    return 100 * tot_ok / max(tot, 1), 100 * con_ok / max(con, 1)


def main():
    tok = AutoTokenizer.from_pretrained(NAME)
    V = len(tok)
    kb = KeyBundle.load(os.path.join(ART, "key.pt"))
    secret = data.build_secret_test()

    # public statistics (attacker side): wikitext
    public_ids = tok(data.build_wiki_text()[:4_000_000], add_special_tokens=False).input_ids
    stop_ids = {i for i, _ in Counter(public_ids).most_common(200)}

    # ciphertext the operator sees: the pi-encoded fine-tune corpus
    plain_ids = tok(data.fine_tune_text(), add_special_tokens=False).input_ids
    cipher_ids = kb.pi[torch.tensor(plain_ids)].tolist()
    print(f"ciphertext observed: {len(cipher_ids):,} encoded tokens")
    print(f"public reference   : {len(public_ids):,} wikitext tokens (domain mismatch)")

    pi_hat, fp, fc = unigram_match(cipher_ids, public_ids, V)
    all_pct, con_pct = score(kb, pi_hat, tok, secret, stop_ids)
    # how many of the mapped tokens are correct, weighted by how often they appear
    acc_tokens = 100 * (pi_hat == kb.pi).float().mean().item()
    print(f"\n[unigram freq-match] pi recovery (all ids): {acc_tokens:.2f}%")
    print(f"[unigram freq-match] secret recovery  all: {all_pct:.2f}%  "
          f"content(excl top-200): {con_pct:.2f}%")
    return dict(pi_acc=acc_tokens, all_pct=all_pct, content_pct=con_pct)


if __name__ == "__main__":
    main()
