# Results (evidence for REPORT.md)

Everything here is small and reviewable without re-running anything. All client matters
are **fictional**; nothing here is legal advice.

| Path | What it is |
|---|---|
| `final_round/final_round.log` | The final-round run, scored against `eval/final_round_key.json` (written before the run). Pre-registered verdict: **FAIL** (task routing 7/8); 30/30 held-out conclusions correct. |
| `final_round/results.json` | The same, structured: every scored field, expected vs got, and its gate status. |
| `final_round/memos/` | The 10 advice notes drafted on the laptop (8 held-out matters + 2 dev matters). `OOS.md` is the mis-routed out-of-scope matter that ended as REFER. |
| `round1/memos/` | The two round-1 advice notes, hand-audited in REPORT.md (2 wrong, 1 misleading conclusion). |
| `precomputed/` | The public reasoning layer the cloud precomputed (`gemini-3.8-flash-high`, over public statute only): 16 explanations, 12 relations, 7 calculation specs, 2 decision procedures (v2 used in the final round; v1 from round 1). Each carries its own audit. |
| `precomputed/enrichment_audit.log` | Per-entry audit summary: which statutory quotes and parameters verified. |

## For legal review

The entries in `precomputed/` are what a lawyer should check: every `quote` is verbatim
from the Employment Rights Act 1996 (as consolidated on legislation.gov.uk), but the
`summary`, `analysis`, `question` and `pitfalls` prose is model-written. Errors found there
are fixed once, centrally, without touching the confidentiality design.

## Reusing the precomputed layer

To run the rich-DB prototype without the enrichment router, copy these entries into the
cache the builder reads:

```bash
mkdir -p artifacts/cloud_rich/reasoning
cp results/precomputed/*.json artifacts/cloud_rich/reasoning/
python -m cloud.richdb            # packs them into the PIR database; no router calls
```

Statute text is © Crown and database right, reused under the Open Government Licence v3.0.
