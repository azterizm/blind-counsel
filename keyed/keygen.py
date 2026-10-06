"""Firm-side key generation for design (a).

The firm holds a secret seed (the "private key"). From it we deterministically
derive every function-preserving transform used to "shift" the base model:

  pi      : vocabulary bijection on {0..vocab-1}      (a token substitution cipher)
  Q       : orthogonal rotation of the residual stream (hidden x hidden)
  sigma_l : a permutation of the MLP intermediate dim, one per layer
  head_l  : a permutation of attention heads (KV groups kept intact), one per layer

These are exact symmetries of a Llama-style transformer (verified numerically in
keyed/shift.py). The firm keeps the seed; the lab only ever sees the shifted
weights. The "public key" in the user's framing is whatever the lab needs to run
the model -- which, as the findings show, is exactly the shifted model itself.

Derivation uses HKDF-SHA256 so that distinct labels give independent streams and
the whole key is reproducible from the seed alone.
"""
from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass

import numpy as np
import torch


# ---------------------------------------------------------------- HKDF (RFC 5869)
def _hkdf(seed: bytes, label: bytes, nbytes: int) -> bytes:
    prk = hmac.new(b"ephemeral-dynamic-llms/salt", seed, hashlib.sha256).digest()
    out, t, counter = b"", b"", 1
    while len(out) < nbytes:
        t = hmac.new(prk, t + label + bytes([counter]), hashlib.sha256).digest()
        out += t
        counter += 1
    return out[:nbytes]


def _rng(seed: bytes, label: str) -> np.random.Generator:
    # 32 bytes of HKDF output -> a seeded numpy PCG64 generator.
    raw = _hkdf(seed, label.encode(), 32)
    return np.random.default_rng(np.frombuffer(raw, dtype=np.uint32))


def _perm(seed: bytes, label: str, n: int) -> torch.Tensor:
    return torch.from_numpy(_rng(seed, label).permutation(n).astype(np.int64))


def _orthogonal(seed: bytes, label: str, n: int) -> torch.Tensor:
    """A Haar-ish orthogonal matrix via QR of a Gaussian, sign-fixed for determinism."""
    g = _rng(seed, label)
    a = g.standard_normal((n, n)).astype(np.float64)
    q, r = np.linalg.qr(a)
    q *= np.sign(np.diag(r))  # make QR unique
    return torch.from_numpy(q)  # float64; caller casts


@dataclass
class KeyBundle:
    pi: torch.Tensor                 # [vocab]        token id -> shifted token id
    pi_inv: torch.Tensor             # [vocab]        inverse of pi
    Q: torch.Tensor                  # [hidden,hidden] orthogonal, float64
    sigma: list[torch.Tensor]        # per layer, [intermediate]
    head: list[torch.Tensor]         # per layer, [num_heads] (within-KV-group safe)
    meta: dict

    def save(self, path: str) -> None:
        torch.save(
            {
                "pi": self.pi, "pi_inv": self.pi_inv, "Q": self.Q,
                "sigma": self.sigma, "head": self.head, "meta": self.meta,
            },
            path,
        )

    @staticmethod
    def load(path: str) -> "KeyBundle":
        d = torch.load(path, weights_only=True)
        return KeyBundle(d["pi"], d["pi_inv"], d["Q"], d["sigma"], d["head"], d["meta"])


def _head_perm(seed: bytes, label: str, n_heads: int, n_kv: int) -> torch.Tensor:
    """Permute heads while keeping GQA groups contiguous and aligned to KV heads.

    We permute the n_kv groups among themselves, and permute the (n_heads//n_kv)
    query heads within each group. A KV head is then permuted with its group, so
    the attention computation is preserved exactly (RoPE is identical per head).
    """
    g = _rng(seed, label)
    per = n_heads // n_kv
    group_order = g.permutation(n_kv)
    out = np.empty(n_heads, dtype=np.int64)
    for new_g, old_g in enumerate(group_order):
        within = g.permutation(per)
        for j in range(per):
            out[new_g * per + j] = old_g * per + within[j]
    return torch.from_numpy(out)


def generate(seed: bytes, cfg) -> KeyBundle:
    """Derive a full key bundle for a given model config."""
    H = cfg.hidden_size
    I = cfg.intermediate_size
    L = cfg.num_hidden_layers
    V = cfg.vocab_size
    nh = cfg.num_attention_heads
    nkv = cfg.num_key_value_heads

    pi = _perm(seed, "vocab", V)
    pi_inv = torch.empty_like(pi)
    pi_inv[pi] = torch.arange(V)

    Q = _orthogonal(seed, "residual-rotation", H)
    sigma = [_perm(seed, f"mlp.{l}", I) for l in range(L)]
    head = [_head_perm(seed, f"head.{l}", nh, nkv) for l in range(L)]

    meta = dict(hidden=H, intermediate=I, layers=L, vocab=V,
                num_heads=nh, num_kv=nkv, head_dim=cfg.head_dim)
    return KeyBundle(pi, pi_inv, Q, sigma, head, meta)


if __name__ == "__main__":
    from transformers import AutoConfig

    cfg = AutoConfig.from_pretrained("HuggingFaceTB/SmolLM2-135M")
    seed = hashlib.sha256(b"demo-firm-private-seed-0001").digest()
    kb = generate(seed, cfg)
    # sanity: pi is a bijection, Q is orthogonal, sigma/head are permutations
    assert torch.equal(kb.pi[kb.pi_inv], torch.arange(cfg.vocab_size))
    ortho_err = (kb.Q @ kb.Q.T - torch.eye(cfg.hidden_size, dtype=kb.Q.dtype)).abs().max()
    print(f"pi bijection      : ok")
    print(f"Q orthogonality   : max|QQ^T - I| = {ortho_err:.2e}")
    print(f"sigma layers       : {len(kb.sigma)} x {kb.sigma[0].numel()}")
    print(f"head layers        : {len(kb.head)} x {kb.head[0].numel()}  e.g. {kb.head[0].tolist()}")
    print(f"det(Q)            : {torch.det(kb.Q).item():+.4f}")
