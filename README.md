# blind-counsel

Adversarial research on confidential legal AI without trusted hardware (TEE).

Research proof of concept. Not legal advice. All client matters in this repository are fictional. Do not use it with real client data.

Part of a two-repository study. Follow-up: [blind-adapters](https://github.com/azterizm/blind-adapters) adds reasoning adapters fetched by PIR.

## What this is

I set out to remove the TEE from confidential legal AI. The test was strict. I treated the cloud operator, staff, other tenants and chip vendors as untrusted. This repository and [blind-adapters](https://github.com/azterizm/blind-adapters) record what worked, what failed and what it costs. The result shows where a TEE is needed.

## Findings

1. Standard cloud RAG leaked 16 private tokens from one client matter, including the client, employer, dates and salary. The blind-cloud design leaked 0. Client data stays on the device. The cloud serves public law through private information retrieval (PIR).
2. Keyed model obfuscation fails. The cloud operator recovered 100% of secret content from an obfuscated open-weight model, across keys and after fine-tuning.
3. Precomputed reasoning works with one failure. Public law reasoning is precomputed in the cloud and applied on the laptop by a local model. Final round: 30 of 30 held-out conclusions correct. Pre-registered verdict: FAIL. One out-of-scope matter was routed to the wrong task. It was stopped before any advice was issued.

Full details in [REPORT.md](REPORT.md). File map in [INDEX.md](INDEX.md).

## Limits

Without a TEE the cloud cannot compute on client data. That removes most of what cloud AI is used for.

- All work on the matter runs on the firm's device. Here that is an 8B model on a laptop at about one minute per matter.
- Only task types prepared in advance are covered. A new task needs new precomputed reasoning or a new adapter. Open-ended prompts are refused.
- Routing to the right task failed in both repositories: 7 of 8 here, 10 of 12 in blind-adapters.
- An open model run in the cloud on client data without hardware protection is not safe. Keyed obfuscation leaked 100%.
- FHE takes 4.6 to 11.8 hours per 500 tokens for a 7B model.
- Fetching adapters by PIR from a library of 1,024 takes 4 to 27 minutes of server time per fetch.
- Samples are small. Nothing has had legal review.

## Where TEEs fit

A TEE runs the model on client data inside isolated, encrypted hardware memory and proves what is running through attestation. [Prem Enclave](https://www.premai.io/prem-enclave) does this on standard GPU clusters with Intel TDX, AMD SEV and NVIDIA confidential computing, on-premise or in the customer's own cloud account. It removes the limits above.

| Need | This research | TEE such as Prem Enclave |
|---|---|---|
| Compute on client data in the cloud | No | Yes |
| Open-ended prompts and new tasks | No, fixed task types only | Yes |
| Model size | Bounded by the device, 8B tested | Large open models |
| Trust in chip vendors | None | Required |

The trade is trust in the chip vendors and their attestation. [Prem's security model](https://docs.prem.io/security-model) states this. It lists hardware side channels and metadata such as timing and payload size as outside its protection.

Use a TEE such as Prem Enclave when the work needs cloud compute on client data. That covers most production legal and healthcare work, including drafting, open-ended analysis and large models.

The design here fits one narrow case. The tasks are fixed and run over public law, the firm will not trust any chip vendor, and laptop compute is enough.

## Controls for any backend

These run on the firm side, with a TEE or without one.

| Repository | What it does | Status |
|---|---|---|
| [legal-rag-router](https://github.com/azterizm/legal-rag-router) | Binds a query to the cited statute provision and refuses invented law. No model, no network. 0.14 ms median, 2.10 ms p99 on Apple M4. | Measured on 2,112 queries |
| [legal-rag-mask](https://github.com/azterizm/legal-rag-mask) | Replaces names, parties and deal terms with consistent pseudonyms before text leaves the firm. | Prototype, not yet evaluated on real contracts |
| [legal-rag-verifier](https://github.com/azterizm/legal-rag-verifier) | Checks each sentence against the statute it was given while the model generates, and rolls back a failed sentence. | Proof of concept |

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
.venv/bin/python -m attacks.keyed.keys
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
