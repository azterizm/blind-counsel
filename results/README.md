# Results

Evidence for REPORT.md. All client matters are fictional. Not legal advice.

| Path | Contents |
|---|---|
| final_round/final_round.log | Final round output. Verdict: FAIL, task routing 7 of 8. Conclusions: 30 of 30 correct. |
| final_round/results.json | Final round scores by field. |
| final_round/memos/ | 10 advice notes. OOS.md is the misrouted matter. |
| round1/memos/ | 2 advice notes from round 1. |
| precomputed/ | Precomputed reasoning from gemini-3.8-flash-high, public statute only. 16 explanations, 12 relations, 7 calculation specs, 2 procedures. |
| precomputed/enrichment_audit.log | Audit result for each entry. |

## Legal review

Quotes in precomputed/ are verbatim from the Employment Rights Act 1996. Summaries, analyses, questions and pitfalls are model-written and require review.

## Reuse without the router

```bash
mkdir -p artifacts/cloud_rich/reasoning
cp results/precomputed/*.json artifacts/cloud_rich/reasoning/
python -m cloud.richdb
```

Statute text: Crown copyright, Open Government Licence v3.0.
