# blind-counsel

Confidential legal AI on an untrusted cloud without trusted hardware (TEE).

Research proof of concept. Not legal advice. All client matters in this repository are fictional. Do not use it with real client data.

## Results

1. Keyed model obfuscation fails. The cloud operator recovered 100% of secret content from an obfuscated open-weight model, across keys and after fine-tuning.
2. Blind cloud works. Client data stays on the device. The cloud serves public law through private information retrieval (PIR). 0 secrets reached the cloud. A standard cloud RAG setup leaked 16 on the same matter.
3. Precomputed reasoning works with one failure. Public law reasoning is precomputed in the cloud and applied on the laptop by a local model. Final round: 30 of 30 held-out conclusions correct. Pre-registered verdict: FAIL. One out-of-scope matter was routed to the wrong task. It was stopped before any advice was issued.

Full details in [REPORT.md](REPORT.md).

## How it works

1. The cloud precomputes reasoning over public statute. Every statutory quote is checked.
2. The cloud stores statute text and the precomputed reasoning in a PIR database.
3. The laptop sends a fixed batch of 56 encrypted queries per matter. The cloud cannot tell which rows were read.
4. The laptop verifies all fetched data.
5. A local model reads the client account. Code does the date and amount calculations.
6. The advice note is produced and stays on the laptop.

## Layout

```
keyed/        keyed weight shift (design a)
attacks/      attacks on design a, cost model
pir/          SimplePIR
cloud/        cloud side: statute database, enrichment, PIR database
device/       laptop side: harness, egress guard, reasoner, calculators
llm/          enrichment router client, local model
eval/         evaluations and the final round answer key
results/      logs, advice notes, precomputed reasoning
lawtext.py    date, amount and statutory period handling
config.py     path to legal-rag-router
```

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
git clone https://github.com/azterizm/legal-rag-router ../legal-rag-router
export LEGAL_RAG_ROUTER=../legal-rag-router
```

Requires Apple Silicon for the local model (MLX).

## Run

```bash
# Keyed weight shift
.venv/bin/python -m keyed.shift
.venv/bin/python -m keyed.engrave 600 3e-4
.venv/bin/python -m attacks.keyed.weights_align
.venv/bin/python -m attacks.keyed.robustness
.venv/bin/python -m attacks.keyed.traffic
.venv/bin/python -m attacks.keyed.activations
.venv/bin/python -m attacks.keyed.verdict
.venv/bin/python -m attacks.cost

# Blind cloud
.venv/bin/python -m pir.simplepir
.venv/bin/python -m cloud.precompute
.venv/bin/python -m cloud.compile
.venv/bin/python -m eval.run

# Precomputed reasoning, final round
.venv/bin/python -m cloud.richdb
HF_HUB_OFFLINE=1 .venv/bin/python -m eval.final
```

Enrichment uses a local router at localhost:8317 to gemini-3.8-flash-high. It sends public statute text only. Without the router, use the published entries in [results/](results/README.md).

## Data and licences

- Code: AGPL-3.0.
- UK legislation: Crown copyright, Open Government Licence v3.0, source legislation.gov.uk.
- CUAD: CC BY 4.0. wikitext-103: CC BY-SA. Not included in this repository.
- Models: SmolLM2-135M and Qwen3-8B, Apache-2.0.

## Citation and security

See [CITATION.cff](CITATION.cff) and [SECURITY.md](SECURITY.md).
