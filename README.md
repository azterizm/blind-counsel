# blind-counsel

Confidential legal AI on an untrusted cloud without trusted hardware (TEE).

Research proof of concept. Not legal advice. All client matters in this repository are fictional. Do not use it with real client data.

Follow-up: [blind-adapters](https://github.com/azterizm/blind-adapters) adds reasoning adapters fetched by PIR.

## Results

1. Keyed model obfuscation fails. The cloud operator recovered 100% of secret content from an obfuscated open-weight model, across keys and after fine-tuning.
2. Blind cloud works. Client data stays on the device. The cloud serves public law through private information retrieval (PIR). 0 secrets reached the cloud. A standard cloud RAG setup leaked 16 on the same matter.
3. Precomputed reasoning works with one failure. Public law reasoning is precomputed in the cloud and applied on the laptop by a local model. Final round: 30 of 30 held-out conclusions correct. Pre-registered verdict: FAIL. One out-of-scope matter was routed to the wrong task. It was stopped before any advice was issued.

Full details in [REPORT.md](REPORT.md).

## Goal

A law firm should get strong AI help on a client matter without the client data leaving its own device. The cloud is not trusted. This includes the operator, staff, other tenants and chip vendors, so no TEE is used. The cloud sees public law only.

## Layers

Each layer covers one kind of need. The cloud sees no client data and, through PIR, not which item was fetched.

| Need | Layer | Cloud | Device | Repository |
|---|---|---|---|---|
| Facts and statute text | Text database by PIR | Precomputes reasoning over public law | Fetches, verifies quotes, applies to the account | blind-counsel |
| Reasoning on new fact patterns | LoRA adapters by PIR | Distils a large model into 8B adapters on public and synthetic data | Fetches, verifies the hash, swaps into the local model | [blind-adapters](https://github.com/azterizm/blind-adapters) |
| Prompts neither layer solves | FHE in the cloud, or a frontier model sent the legal coordinates with user consent | Computes on encrypted data, or answers on coordinates only | Asks the user | Not built |

## Why combine the layers

No single layer covers legal work. Text covers what the cloud anticipated and gives exact citations. Adapters handle fact patterns the text did not anticipate. Escalation covers the rest at a higher cost and only with consent.

In blind-adapters, on 12 held-out matters, the base model scored 35 of 50 with 4 wrong answers past the gate. Text scored 40 with 3. The adapter scored 42 with 1. Adapter plus text also scored 42 with 1.

The layers share one set of rules, so they can be stacked without widening what the cloud sees. Code does every date and amount. Every answer needs verbatim evidence from the account. The grounding gate turns unsupported answers into unclear. The egress guard blocks client data from leaving the device.

The cloud does the expensive work once for all clients: precomputing reasoning and distilling a large model into adapters. Each matter costs about one minute on the laptop and a fixed batch of PIR queries.

## Open problems

- Routing failed in both repositories: 7 of 8 here, 10 of 12 in blind-adapters. The router must pick the right task or refuse before any layer helps.
- Adapter PIR is costly at scale. Below 16 adapters, downloading the whole library is cheaper. At 1,024 adapters one fetch takes 4 to 27 minutes of server time with the tested layout.
- FHE costs 4.6 to 11.8 hours per 500 tokens for a 7B model. The consented frontier route reveals the legal coordinates.
- Samples are small. The precomputed reasoning and adapters have had no legal review.

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
