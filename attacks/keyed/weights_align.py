"""Attack: recover the vocabulary permutation pi from the engraved model's
embedding table, using ONLY the public base model + public text statistics.

Why pi is the whole game: pi is a substitution cipher on token ids. If the
operator recovers pi, every encoded token stream it sees (the fine-tune corpus,
user queries, model outputs, context documents) decodes directly to plaintext.
R, sigma and the head permutations are only needed to read hidden states/weights,
not the token streams.

The key invariant: the firm's shift sends embedding row v -> E[v] @ R, and an
orthogonal R preserves the row's L2 norm exactly. So on the clean upload,
sorting rows by norm reproduces pi. Fine-tuning ("engraving") perturbs the norms;
this script measures how much pi-recovery -- and secret-text recovery -- survives.

Usage:
  python -m attacks.keyed.weights_align                      # sweep all checkpoints
  python -m attacks.keyed.weights_align artifacts/engraved_E1_ckpts/embed_step1000.pt
"""
from __future__ import annotations

import glob
import os
import re

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from keyed import data
from keyed.keygen import KeyBundle

NAME = "HuggingFaceTB/SmolLM2-135M"
ART = data.ART


# ------------------------------------------------------------------ public info
def public_base_embed() -> torch.Tensor:
    base = AutoModelForCausalLM.from_pretrained(NAME, dtype=torch.float32)
    return base.model.embed_tokens.weight.detach().double()


def stopword_ids(tok, k: int = 200) -> set[int]:
    """The k most frequent token ids in the attacker's PUBLIC corpus (wikitext)."""
    wiki = data.build_wiki_text()[:2_000_000]
    ids = tok(wiki, add_special_tokens=False).input_ids
    from collections import Counter
    return {i for i, _ in Counter(ids).most_common(k)}


# ------------------------------------------------------------------ the attack
def recover_pi_by_norm(E_base: torch.Tensor, E_shift: torch.Tensor) -> torch.Tensor:
    """Return pi_hat: base token v -> shifted row id, by matching row norms (1:1,
    greedy on sorted norm -- optimal for a 1-D monotone signature)."""
    nb = E_base.norm(dim=1)
    ns = E_shift.norm(dim=1)
    order_b = nb.argsort()
    order_s = ns.argsort()
    pi_hat = torch.empty(E_base.shape[0], dtype=torch.long)
    pi_hat[order_b] = order_s
    return pi_hat


def decode_stream(enc_ids: torch.Tensor, pi_inv_hat: torch.Tensor) -> torch.Tensor:
    """Operator decodes an encoded id stream with its guessed inverse permutation."""
    return pi_inv_hat[enc_ids]


# ---- stronger attack: recover R from the embedding covariance (drift-robust) ----
def recover_R_covariance(E_base: torch.Tensor, E_shift: torch.Tensor) -> torch.Tensor:
    """Recover the residual rotation R WITHOUT token correspondence.

    The shift sends the embedding point cloud E_base -> E_base @ R (then relabels
    rows by pi). The second moment therefore transforms as
        C_shift = E_shift^T E_shift = R^T (E_base^T E_base) R = R^T C_base R,
    so C_base and C_shift share eigenvalues and their eigenvectors are related by R.
    This is a *bulk* statistic over all 49k rows, so a small fine-tuning
    perturbation barely moves it. We fix each eigenvector's sign using the mean
    embedding direction (also rotation-covariant). Returns R_hat with
        E_shift @ R_hat^T  ~=  E_base[pi_inv]  (rows brought back to base frame).
    """
    Cb = E_base.T @ E_base
    Cs = E_shift.T @ E_shift
    lb, Ub = torch.linalg.eigh(Cb)      # ascending eigenvalues, orthonormal columns
    ls, Us = torch.linalg.eigh(Cs)
    mu_b = E_base.mean(0); mu_s = E_shift.mean(0)
    pb = Ub.T @ mu_b
    ps = Us.T @ mu_s
    s = torch.sign(pb * ps); s[s == 0] = 1.0
    R_hat = Ub @ torch.diag(s) @ Us.T   # H x H
    return R_hat


def decode_via_R(enc_ids, E_base, E_shift, R_hat, chunk=4096):
    """Decode encoded ids: align each shifted row back to base frame, NN in E_base."""
    uniq, inv = torch.unique(enc_ids, return_inverse=True)
    aligned = E_shift[uniq] @ R_hat.T                 # [U, H] ~ E_base[pi_inv[uniq]]
    guess = torch.empty(uniq.numel(), dtype=torch.long)
    bn = (E_base * E_base).sum(1)                     # ||base||^2 for cdist shortcut
    for i in range(0, uniq.numel(), chunk):
        a = aligned[i:i + chunk]
        # argmin ||a - E_base||^2 = argmin ||a||^2 - 2 a.E_base + ||E_base||^2
        d = bn[None, :] - 2.0 * (a @ E_base.T)
        guess[i:i + chunk] = d.argmin(1)
    return guess[inv]


def score_secret_via_R(kb, E_base, E_shift, R_hat, tok, secret, stop_ids):
    pi_true_inv = kb.pi_inv
    tot = tot_ok = con = con_ok = 0
    longest = 0; sample = None
    # gather all encoded ids across passages, decode once
    all_true, bounds = [], []
    for passage in secret:
        t = torch.tensor(tok(passage, add_special_tokens=False).input_ids)
        bounds.append((len(all_true), len(all_true) + t.numel()))
        all_true.append(t)
    true_ids = torch.cat(all_true)
    enc = kb.pi[true_ids]
    dec = decode_via_R(enc, E_base, E_shift, R_hat)
    for (a, b), passage in zip(bounds, secret):
        ti = true_ids[a:b]; di = dec[a:b]
        ok = (di == ti)
        tot += ok.numel(); tot_ok += int(ok.sum())
        mask = torch.tensor([int(t) not in stop_ids for t in ti])
        con += int(mask.sum()); con_ok += int((ok & mask).sum())
        run = 0
        for v in ok.tolist():
            run = run + 1 if v else 0; longest = max(longest, run)
        if sample is None and ok.numel() > 10:
            sample = tok.decode(di.tolist())
    return dict(all_pct=100*tot_ok/max(tot,1), content_pct=100*con_ok/max(con,1),
                longest_run=longest, sample=sample)


def score_secret_recovery(kb, pi_hat, tok, secret, stop_ids):
    """Encode each secret passage with the TRUE pi (what the operator observes),
    decode with pi_hat, and measure token-recovery %.

    Returns all-token %, content-token % (excluding the top-200 public stopwords),
    and the longest consecutive correctly-recovered run (in tokens)."""
    pi_inv_hat = torch.empty_like(pi_hat)
    pi_inv_hat[pi_hat] = torch.arange(pi_hat.numel())

    tot = tot_ok = con = con_ok = 0
    longest = 0
    sample = None
    for passage in secret:
        true_ids = torch.tensor(tok(passage, add_special_tokens=False).input_ids)
        if true_ids.numel() == 0:
            continue
        enc = kb.pi[true_ids]                    # operator sees this
        dec = decode_stream(enc, pi_inv_hat)     # operator's guess
        ok = (dec == true_ids)
        tot += ok.numel(); tot_ok += int(ok.sum())
        mask = torch.tensor([int(t) not in stop_ids for t in true_ids])
        con += int(mask.sum()); con_ok += int((ok & mask).sum())
        # longest run
        run = 0
        for b in ok.tolist():
            run = run + 1 if b else 0
            longest = max(longest, run)
        if sample is None and ok.numel() > 10:
            sample = tok.decode(dec.tolist())
    return dict(
        all_pct=100 * tot_ok / max(tot, 1),
        content_pct=100 * con_ok / max(con, 1),
        longest_run=longest,
        n_tokens=tot,
        sample=sample,
    )


def run_checkpoint(ckpt_path, E_base, kb, tok, secret, stop_ids):
    d = torch.load(ckpt_path, weights_only=True)
    E_shift = d["embed"].double()
    step = d.get("step", "?")
    # attack A: naive global norm-sort
    pi_hat = recover_pi_by_norm(E_base, E_shift)
    pi_acc = 100 * (pi_hat == kb.pi).float().mean().item()
    secA = score_secret_recovery(kb, pi_hat, tok, secret, stop_ids)
    # attack B: covariance R-recovery + nearest-neighbour decode (drift-robust)
    R_hat = recover_R_covariance(E_base, E_shift)
    secB = score_secret_via_R(kb, E_base, E_shift, R_hat, tok, secret, stop_ids)
    return step, pi_acc, secA, secB


def main(paths=None):
    tok = AutoTokenizer.from_pretrained(NAME)
    E_base = public_base_embed()
    kb = KeyBundle.load(os.path.join(ART, "key.pt"))
    secret = data.build_secret_test()
    print("computing public top-200 stopwords from wikitext ...")
    stop_ids = stopword_ids(tok, 200)

    if paths is None:
        paths = sorted(glob.glob(os.path.join(ART, "engraved_E1_ckpts", "embed_step*.pt")),
                       key=lambda p: int(re.search(r"step(\d+)", p).group(1)))
    print(f"\n{'':>6} | {'A: norm-sort':^26} | {'B: covariance R + NN':^26}")
    print(f"{'step':>6} | {'pi%':>7} {'secret':>7} {'cont%':>8} | "
          f"{'secret':>8} {'cont%':>8} {'run':>6}")
    print("-" * 70)
    rows = []
    for p in paths:
        step, pi_acc, secA, secB = run_checkpoint(p, E_base, kb, tok, secret, stop_ids)
        rows.append((step, pi_acc, secA, secB))
        print(f"{step:>6} | {pi_acc:>6.1f}% {secA['all_pct']:>6.1f}% {secA['content_pct']:>7.1f}% | "
              f"{secB['all_pct']:>7.1f}% {secB['content_pct']:>7.1f}% {secB['longest_run']:>6}")
    if rows:
        print("\nattack B decoded sample (most-engraved checkpoint):")
        print("  ", repr((rows[-1][3]["sample"] or "")[:240]))
    return rows


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
