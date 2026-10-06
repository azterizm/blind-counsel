"""Device-side model: the small LM's ONLY job is to SELECT among candidates.

In discover-then-bind, the local concept index proposes candidate coordinates for a
query. The device model scores the closed candidate set and picks one. It never
generates a coordinate or any statutory text, so it cannot invent law or leak
("the cheap model must not contaminate via softmax"): its output is an index into a
public, closed list, chosen deterministically (greedy, no sampling).

Everything here runs on the device against the public concept index. No case data
leaves; the chosen coordinate is then fetched via PIR exactly like a cited one.

The production device model is Qwen2.5-3B; we use the cached SmolLM2-135M as a
stand-in (selection quality is not the property under test -- the bounded,
non-generative, local nature is).
"""
from __future__ import annotations

import os
import sys

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import LRR
if os.path.join(LRR, "src") not in sys.path:
    sys.path.insert(0, os.path.join(LRR, "src"))

NAME = "HuggingFaceTB/SmolLM2-135M"
_MODEL = {}


def _load():
    if "m" not in _MODEL:
        _MODEL["t"] = AutoTokenizer.from_pretrained(NAME)
        _MODEL["m"] = AutoModelForCausalLM.from_pretrained(NAME, dtype=torch.float32).eval()
    return _MODEL["t"], _MODEL["m"]


@torch.no_grad()
def _score(query: str, title: str) -> float:
    """Mean log-prob the model assigns to the candidate title given the query.
    A pure scoring signal -- no text is generated."""
    tok, model = _load()
    prompt = f"Legal question: {query}\nMost relevant statute provision: "
    p_ids = tok(prompt, return_tensors="pt").input_ids
    t_ids = tok(title, return_tensors="pt", add_special_tokens=False).input_ids
    ids = torch.cat([p_ids, t_ids], dim=1)
    logits = model(ids).logits[0]
    logp = torch.log_softmax(logits, dim=-1)
    start = p_ids.shape[1]
    tgt = ids[0, start:]
    lp = logp[start - 1:-1][torch.arange(tgt.numel()), tgt]
    return float(lp.mean())


def select(query: str, candidates: list):
    """candidates: objects with .coordinate and .title. Returns (best, ranked)
    where ranked is [(coordinate_key, model_score, concept_score)]. The pick is
    always one of the candidates -- asserted."""
    ranked = []
    for c in candidates:
        co = getattr(c, "coordinate", None)
        key = getattr(co, "key", None) or str(co)
        title = getattr(c, "title", "") or key
        ranked.append((key, _score(query, title), float(getattr(c, "score", 0.0))))
    ranked.sort(key=lambda r: r[1], reverse=True)
    best_key = ranked[0][0]
    candidate_keys = {getattr(getattr(c, "coordinate", None), "key", None) or str(getattr(c, "coordinate", None))
                      for c in candidates}
    assert best_key in candidate_keys, "model selected outside the candidate set (impossible by design)"
    return best_key, ranked


def demo(query="unfair dismissal compensatory award statutory cap"):
    from legal_rag_router import Router
    r = Router.from_path(os.path.join(LRR, "data", "index"),
                         concepts=os.path.join(LRR, "data", "concepts"))
    disc = r.discover(query, limit=6)
    cands = list(disc.candidates)
    best, ranked = select(query, cands)
    print(f"query (stays local): {query!r}")
    print(f"concept index proposed {len(cands)} PUBLIC candidate coordinates.")
    print("device-model selection (greedy score; no generation):")
    for key, ms, cs in ranked:
        mark = " <- selected" if key == best else ""
        print(f"   {key:<26} model={ms:7.3f}  concept={cs:6.2f}{mark}")
    print(f"\nselected coordinate: {best}  (guaranteed in candidate set -> cannot invent law)")
    return best


if __name__ == "__main__":
    demo()
