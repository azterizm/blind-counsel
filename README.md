# blind-counsel

**Confidential legal AI on a zero-trust cloud — without trusted hardware.**
A research proof of concept: can a law firm use cloud AI on confidential matters when
the cloud operator is the adversary and no TEE (SEV, TDX, GPU confidential computing)
is trusted?

> **Research prototype, not legal advice.** All client matters in this repository are
> fictional. Do not process real client data with it. The final round's pre-registered
> verdict is **FAIL** (see below) — read [REPORT.md](REPORT.md) before relying on anything.

## Findings

1. **Hiding client data inside a cloud-run model fails.** A keyed, function-preserving
   "shift" of an open-weight LLM (vocabulary permutation + residual rotation + MLP/head
   permutations) looks like gibberish, but the operator recovers **100% of the secret
   content**: the rotation falls out of the embedding covariance, a bulk statistic that
   fine-tuning barely moves. It holds across keys and through real fine-tuning; the
   attack only drops below a 10% threshold when perplexity is already ×2.9. Without a
   TEE or FHE, a cloud cannot compute on plaintext it cannot read.
2. **A blind cloud works.** The cloud holds only *public* law, served by private
   information retrieval (SimplePIR), so it cannot tell which provision — or which kind
   of matter — was fetched. The client's account never leaves the device. Measured: 0
   secrets reach the cloud; a naive cloud-RAG baseline leaks 16 on the same matter.
3. **Reasoning can be precomputed in public and applied in private.** A frontier model
   precomputes reasoning over public statute offline (explanations, cross-provision
   relations, calculation parameters, decision procedures — every statutory quote
   audited). The lawyer's laptop fetches it by PIR (fixed 56 queries per matter, so the
   cloud cannot tell the task or whether it answered) and applies it to the confidential
   account with a local Qwen3-8B, while code does the arithmetic. Against a key written
   before the run: **30/30 held-out conclusions correct** and 0 wrong answers past the
   grounding gate, but the **pre-registered verdict is FAIL**: one out-of-scope matter
   was routed to the wrong task (7/8). It was caught downstream and no advice was issued.

## How the blind cloud works

```
 CLOUD (untrusted, sees public law only)            LAPTOP (the firm's own device)
 ─────────────────────────────────────              ──────────────────────────────
 offline: frontier LLM precomputes reasoning        client account stays here
   over public statute; every quote audited         local model picks the task
                                                       (or refuses)
 PIR database: statute + precomputed reasoning  ◀── fixed batch of LWE queries
   (cannot tell which rows were read)           ──▶ rows; sha256 + quotes re-verified
                                                    model extracts facts (verbatim-checked)
                                                    code computes dates, caps, payments
                                                    model applies tests -> grounding gate
                                                    referenced advice note (stays here)
```

## Layout

```
keyed/              candidate design (a): keyed weight shift
  keygen.py           firm seed -> pi (vocab), R (rotation), per-layer MLP/head perms
  shift.py            exact function-preserving weight shift (+ verifier)
  data.py             CUAD (firm corpus) / wikitext (attacker) / secret test set
  engrave.py          fine-tune ("engrave") the shifted model
attacks/
  keyed/              attacks on design (a): weights_align, robustness, traffic,
                      activations, verdict (the >=10% rule)
  cost.py             engraving / 1:1 serving (Erlang C) / FHE reference costs
pir/simplepir.py      SimplePIR (LWE): fetch a row without revealing which
cloud/                cloud side (public law only)
  precompute.py       statute PIR database
  compile.py          public task program (Milestone 3 harness)
  reason.py           offline enrichment: explain / relation / calc / procedure + audit
  richdb.py           rich PIR database + public task index + fixed fetch budget
device/               laptop side
  harness.py          Milestone 3: route locally, fetch by PIR, compose a referenced memo
  egress.py           taint guard: only LWE queries and public sync may leave
  select.py           bounded, non-generative candidate selection
  reasoner.py         rich-DB prototype: select, fetch, verify, extract facts, decide
  calc.py             deterministic calculators (service, deadlines, caps, redundancy pay)
llm/                  router client (public enrichment) + local MLX device model
lawtext.py            numbers / dates / money in legal text; statutory period arithmetic
config.py             path to the legal-rag-router checkout
eval/
  run.py              Milestone 3 security evaluation
  final.py            final round, scored against final_round_key.json
results/              curated evidence: logs, advice notes, the precomputed layer
```

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt     # mlx needs Apple Silicon
git clone https://github.com/azterizm/legal-rag-router ../legal-rag-router
export LEGAL_RAG_ROUTER=../legal-rag-router             # optional if cloned as a sibling
```

Milestone 1 downloads `HuggingFaceTB/SmolLM2-135M`, `theatticusproject/cuad` and
`Salesforce/wikitext`. The rich-DB prototype runs `mlx-community/Qwen3-8B-4bit` on the
laptop (pinned revision in `llm/__init__.py`).

## Run

```bash
# Milestone 1 -- does hiding data inside the model work?
.venv/bin/python -m keyed.shift                  # the shift is an exact symmetry
.venv/bin/python -m keyed.engrave 600 3e-4       # fine-tune; drift checkpoints
.venv/bin/python -m attacks.keyed.weights_align  # naive vs covariance attack
.venv/bin/python -m attacks.keyed.robustness     # drift / perplexity / recovery
.venv/bin/python -m attacks.keyed.traffic        # ciphertext-only attack
.venv/bin/python -m attacks.keyed.activations    # read runtime hidden states
.venv/bin/python -m attacks.keyed.verdict        # apply the 10% rule
.venv/bin/python -m attacks.cost                 # cost + queueing + FHE reference

# Milestone 3 -- blind cloud, sealed device
.venv/bin/python -m pir.simplepir                # PIR correctness + server-view privacy
.venv/bin/python -m cloud.precompute && .venv/bin/python -m cloud.compile
.venv/bin/python -m eval.run                     # egress, integrity, determinism, refusal

# Rich-DB prototype -- final round
.venv/bin/python -m cloud.richdb                 # pack the precomputed layer into PIR
HF_HUB_OFFLINE=1 .venv/bin/python -m eval.final  # 8 held-out + 2 dev matters vs the key
```

The offline enrichment (`cloud/reason.py`) calls an OpenAI-compatible router at
`localhost:8317` that forwards to `gemini-3.8-flash-high`; it only ever sends public statute
text. Without it, reuse the published layer: see [results/README.md](results/README.md).

## Results

[`results/`](results/) holds the evidence without re-running anything: the final-round log
and structured results, the ten advice notes, the round-1 notes, and the full precomputed
reasoning layer with its audit. The answer key and pass rule are in
[`eval/final_round_key.json`](eval/final_round_key.json), written before the round ran.

## Data and licences

- **Code:** AGPL-3.0 ([LICENSE](LICENSE)).
- **UK legislation** (via legal-rag-router, and quoted in `results/precomputed/`):
  © Crown and database right, Open Government Licence v3.0. Source: legislation.gov.uk.
- **CUAD:** CC BY 4.0. **wikitext-103:** CC BY-SA. Neither is redistributed here.
- **Models:** SmolLM2-135M and Qwen3-8B, Apache-2.0. The precomputed reasoning layer was
  produced by `gemini-3.8-flash-high` over public statute text only.

## Cite, security

Citation metadata: [CITATION.cff](CITATION.cff). Threat model and reporting:
[SECURITY.md](SECURITY.md).
