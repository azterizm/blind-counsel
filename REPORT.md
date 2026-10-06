# Confidential LLM inference without TEEs: report

**Question.** Can a law firm (later, healthcare) run an open-weight LLM on an
untrusted cloud so that the operator cannot read case data? The operator has full
physical and software access and is treated as the adversary. No hardware root of
trust is allowed (no SEV, TDX, GPU-CC, or chip-maker trust).

**Design under test: (a), the firm's preferred design.** The firm generates a key
pair locally and keeps the private key. It applies a function-preserving shift to an
open base model using the key: a residual-stream rotation, a vocabulary permutation,
and per-layer MLP and head permutations. The lab supplies the base model and the
hardware, and fine-tunes the shifted model on the firm's encoded corpus ("engraving").
At serve time the firm encodes queries with the key. The operator should see only
unreadable weights, inputs, activations, and outputs.

**Pass/fail rule.** Fixed by the firm before any run. Design (a) fails if any attack
recovers 10% or more of the secret test tokens. The primary count excludes the 200
most frequent public tokens (stopwords and punctuation), which frequency analysis
recovers trivially and which reveal nothing. Names, amounts, and dates alone are not
secrets and are reported for information only.

---

## Verdict

Design (a) fails in every configuration tested. In the realistic setting the operator
recovers 100% of the secret content using only the public base model and what the
operator already holds. No operating point is both usable and safe.

The cause is structural. The shift is a global linear symmetry of the network, and its
generators can be recovered from bulk statistics of the public and deployed weights
that fine-tuning does not move:

- The vocabulary permutation pi is a token substitution cipher. The rotation preserves
  each embedding row's L2 norm exactly, so pi can be read from the row norms.
- The residual rotation R is recovered from the embedding covariance. E^T E transforms
  as R^T E_base^T E_base R. This statistic covers all 49,152 rows and a realistic
  fine-tune barely changes it.

Recovering pi lets the operator read every encoded token stream (corpus, queries,
outputs) as plaintext. Recovering R also exposes the hidden states in plaintext.

---

## Setup (local simulation)

| Role | Played by |
|---|---|
| Base model | `HuggingFaceTB/SmolLM2-135M` (Llama architecture; hidden 576, 30 layers, vocab 49,152, tied embeddings, untied for the shift) |
| Firm private corpus | CUAD contract text (511 PDFs, 26.7M chars, 5.26M encoded fine-tune tokens). Not visible to the attacker. |
| Attacker reference corpus | wikitext-103 (legal vs wiki domain mismatch, which favors the defender) |
| Secret test set | 400 passages: 200 synthetic privileged paragraphs and 200 held-out contract passages (disjoint from the fine-tune split) |
| Attacker knowledge | Public base model and public English statistics only |

**The shift is an exact symmetry.** `keyed/shift.py` folds each RMSNorm gamma into the
following linear layer, rotates the residual by an orthogonal R, permutes the MLP
intermediate and the attention heads (GQA groups kept intact), and permutes the
vocabulary. Verified on real weights:

```
argmax agreement : 100.0%       mean cosine : 1.000000
max |delta logit|: 1.0e-3 (float32), 1.1e-5 (float64)   # numerical, not structural
```

---

## Attacks and measurements

All numbers were measured on an M-series laptop (MPS) and can be reproduced with the
commands in the README.

### 1. Clean upload: operator snapshots the shifted weights before fine-tuning

Under the plan's role split, the firm uploads the shifted weights and the lab then
fine-tunes. The operator therefore first sees an exact symmetry of the public model.

| Metric | Result |
|---|---|
| pi recovered from embedding row norms | 99.98% (under 1 s) |
| Secret recovery (content / all) | 100% / 100% |
| Longest verbatim run | 204 tokens |

Decoded sample (operator output):

> "Memo to file re Northbridge Capital v. the regulator: exposure on the indemnity
> claim is approximately $70,000; recommend we do not produce the internal
> post-closing audit absent a protective order."

### 2. Fine-tuned model only (best case for the design)

A gentle fine-tune (lr 3e-4) of the shifted model on the firm's encoded contracts. The
model improves on the firm's domain (perplexity falls below baseline) and stays fully
readable. Two attacks at each checkpoint:

| Step | Real drift | Perplexity vs base | A norm-sort content % | B covariance content % | B verbatim run |
|---:|---:|---:|---:|---:|---:|
| 0   | 0.000 | 1.00x | 100.0 | 100.0 | 204 |
| 50  | 0.002 | 1.74x | 2.0   | 100.0 | 204 |
| 120 | 0.005 | 1.23x | 0.8   | 100.0 | 204 |
| 250 | 0.009 | 0.95x | 0.5   | 100.0 | 204 |
| 400 | 0.013 | 0.88x | 0.2   | 100.0 | 204 |
| 600 | 0.018 | 0.83x | 0.3   | 100.0 | 204 |

Attack A, a 1-D global sort, fails at 0.2% drift. This reproduces the earlier finding
that fine-tuning defeats weight matching. Attack B recovers the rotation from a bulk
statistic and is unaffected: 100% content and a 204-token verbatim decode at every
checkpoint, including the most fine-tuned, lowest-perplexity model. Results were
identical (100%) across four independent keys.

### 3. Defender's dilemma (controlled drift sweep)

Synthetic per-row drift was added to the clean shifted embedding. Perplexity and
attack B were measured at each level.

| Drift (mean rel) | Perplexity vs base | Attack B content % |
|---:|---:|---:|
| 0.00 | 1.0x | 100.0 |
| 0.05 | 1.0x | 100.0 |
| 0.10 | 1.1x | 88.1 |
| 0.15 | 1.3x | 45.6 |
| 0.20 | 1.6x | 19.2 |
| 0.25 | 2.1x | 10.4 |
| 0.30 | 2.9x | 3.3 |
| 0.40 | 7.6x | 0.0 |

Attack B falls below the 10% threshold only at drift of about 0.3, where perplexity is
2.9x and the model is unusable. A usable fine-tune produces drift of about 0.004
(perplexity 1.08x), where recovery is 100%. No usable and safe operating point exists.
A high learning-rate fine-tune was also tried to reach large drift quickly. It diverged
(perplexity 44x at drift 1.4%), so the model is destroyed before drift becomes
protective.

### 4. Ciphertext-only traffic analysis (no weights): negative result

pi was treated as a substitution cipher. Unigram frequencies of the 5.26M observed
encoded tokens were matched against public wikitext statistics.

| Metric | Result |
|---|---|
| pi recovery | 0.01% |
| Secret content recovery | 0.0% |

Frequency analysis alone does not break pi. The 49k-token alphabet and the domain
mismatch defeat naive matching. This does not help the design, because the
weight-based attacks (2 and 3) succeed completely. Bigram hill-climbing would improve
this result and was not needed.

### 5. Runtime activations

With R recovered from the weights, the operator un-rotates serve-time hidden states and
reads them with the public model's logit lens:

```
secret query: "the settlement figure of $70,000 must remain sealed"
layer-0 reconstruction accuracy: 100.0%
  decoded: "the settlement figure of $70,000 must remain sealed"
```

### Enrichment variants E1, E2, E3

- **E1 (data fixed in at engraving, full fine-tune):** the only variant that moves the
  base embedding, and the best case for the defender. Still 100% (sections 1 to 3).
- **E2 (encoded documents in the context window) and E3 (LoRA on top):** leave the base
  embedding byte-identical to the clean shift. Attack B gets 100% immediately (the
  drift 0 row). Broken by construction.

E1 is the hardest case for the attacker and it fails, so all three fail.

---

## Cost of pursuing (a), and exclusion of (b) FHE

Each firm key produces a distinct model, so nothing batches across firms.

- **Engraving** cost is linear in users. A 70B model at 1B tokens per user costs about
  $729 per user (about $0.7M per 1,000-user fleet). Heavier domain adaptation scales
  proportionally.
- **1:1 queued serving** (Erlang C, 1,000 users, 20 requests per day, mean wait under
  10 s): about 9 GPUs ($179/day) for 8B per user, about 136 GPUs ($2,709/day) for 70B
  per user, under the stated assumptions. This isolates users from each other, not from
  the operator.
- **(b) FHE** (literature: Llama-2-7B at 33 to 85 s/token on 8 GPUs): 4.6 to 11.8 h and
  $92 to $236 per 500 tokens, 3 to 5 orders of magnitude worse than native serving.
  Excluded as infeasible, as directed by the firm.

---

## Recommendation: blind cloud, sealed device (Milestone 3)

Any model the cloud runs on case data can be read by the operator. Without a hardware
root, the only way to meet a zero-trust threat model is to never give the cloud
readable case data.

- **Compile:** the cloud model writes typed workflow programs and templates per legal
  task type. Nothing case-specific leaves the device.
- **Private lookup:** precomputed analysis over public legal sources, fetched with
  SimplePIR (LWE; the server view is independent of the query).
- **Local harness:** a deterministic interpreter on the device. The small on-device
  model only selects among candidates. Every value carries a byte-exact
  `(doc, start, end, sha256)` reference.
- **Egress guard and refuse-and-flag:** one taint-tracked egress with fixed size and
  fixed schedule. Open-ended requests over novel facts are refused and flagged.

## Milestone 3: blind-cloud PoC

Built on the existing `legal-rag-router` (UK legislation, 134,219 documents, OGL-3.0)
and a working SimplePIR. Demo matter: UK ordinary unfair-dismissal advice under the
Employment Rights Act 1996.

- **Lane A (compile, cloud):** a public JSON task program citing statute coordinates,
  with `{quote}`, `{fact}`, and `{verdict}` holes. No case data (`cloud/compile.py`).
- **Lane B (private lookup):** the cloud serves a 654-row by 2 KB PIR matrix of
  per-section statute text (`cloud/precompute.py`). The device fetches each cited
  section via SimplePIR. Correctness 5/5. The server's query distribution is
  independent of the index (mean about Q/2 for any row; `pir/simplepir.py`).
- **Lane C (local harness):** `legal-rag-router` binds the firm's question locally (no
  model, no network). Statute text is fetched via PIR, sha256-verified byte for byte,
  and inserted into the template. Private facts are filled from the local case record
  (`device/harness.py`). The device model only selects among public candidate
  coordinates in discover-then-bind and never generates law (`device/select.py`).
- **Lane D and egress guard:** invented law and missing citations are refused and
  flagged. A CaMeL-style taint guard allows only LWE PIR queries and public sync off
  the device (`device/egress.py`).

**Evaluation (`eval/run.py`), all pass:**

| Check | Result |
|---|---|
| Egress leakage (blind cloud) | 0 of 17 secrets in the 575,520 bytes received by the cloud (all LWE vectors) |
| Guard blocks real leaks | 3/3 (tainted memo, raw fact, fake PIR query) |
| PIR integrity | 5/5 statute quotes sha256-verified byte-exact |
| Determinism | Memo byte-identical across runs (same sha256) |
| Refuse-and-flag | Invented law: refuse. No citation: discover. Valid: bind. |
| Integrity enforcement | A one-byte DB tamper is detected (sha256 mismatch); other quotes still verify |
| Contrast: naive cloud RAG | Leaks 16 private tokens (client, employer, dates, salary) on the same matter |

The memo is a fully referenced advice note (11,963 chars, 5 verified statutory quotes)
composed entirely on the device. Case data does not reach the cloud. Output is exact
and deterministic.

Caveats. The on-device model is the cached SmolLM2-135M stand-in (production target:
Qwen2.5-3B), so selection quality is weak; the concept index's own score ranks better.
The property shown is bounded, local, non-generative selection, not its accuracy. The
PIR database covers one Act. The fixed fetch schedule (22 queries per section) is sized
by the largest ERA section. These are PoC scales, not production tuning.

---

## Rich-DB prototype: precomputed public reasoning, applied privately on the laptop

**Question.** Can the model reason over a client's situation and the retrieved law
without the cloud seeing the situation, if the fact-independent legal reasoning is
precomputed offline and fetched by PIR?

**Roles (no trust displaced):**

- **Cloud, offline, public data only:** `gemini-3.8-flash-high`, via the router,
  enriched 14 ERA 1996 provisions across two task types (unfair dismissal, redundancy
  pay) into 26 reasoning entries: 14 explanations (summary, legal elements, thresholds,
  each element tied to a verbatim statutory quote), 10 relations (from a deterministic
  link graph of explicit cross-references and defined terms such as "effective date of
  termination"), and 2 decision procedures. A central audit removed every claim whose
  quote is not in the statute (for example s124 6 to 5, s136 6 to 5). The router sees
  only public statute text and never a client, so it needs no trust
  (`cloud/reason.py`).
- **Cloud, online:** a 696-row PIR DB containing all 431 ERA section texts and the 26
  entries (`cloud/richdb.py`). Every matter issues exactly 48 PIR queries.
- **Device (the laptop):** Qwen3-8B (4-bit MLX, pinned revision) runs offline. It
  selects the task from the public task index or refuses, fetches everything in one
  fixed batch, re-verifies hashes and the cloud's quotes, answers each procedure step
  over the private account, and passes every answer through a grounding gate
  (`device/reasoner.py`). A hosted GPU was rejected for this role because it would
  displace trust, not remove it.

**Round 1 evaluation (three confidential matters), all 7 checks pass:**

| Check | Result |
|---|---|
| Task selection | Dismissal: unfair-dismissal. Redundancy: redundancy-pay. Tenancy deposit: refused (out of scope). |
| Cloud view | 48 queries for every matter, same statistics. Task type and answered vs refused are not visible. |
| Egress | 0 of 17 / 12 / 7 narrative secrets reached the cloud. 0 cloud-LLM calls during matters (tripwire). |
| Integrity | 0 hash failures. Cloud's statutory quotes re-verified on the device: 49/49, 37/37. |
| Grounding | Every yes/no conclusion cites verbatim client facts and fetched provisions. One step with a non-verbatim quote was auto-downgraded to "unclear". |
| Anti-fabrication | Invented client quote and fake `s999` authority rejected. |
| Determinism | Memo byte-identical across runs. |

**Substance audit (manual review), not covered by the checks:**

| Matter | Correct | Wrong or misleading |
|---|---|---|
| Unfair dismissal | Dismissed (s95). Likely unfair: no investigation or hearing (s98). | Qualifying period: stated "<2 years" for 2 y 7 m (date arithmetic). Compensation: stated "no loss" (confused the s124 cap with loss). Time limit framed as missed when about 4 weeks remain. EDT given as letter date. |
| Redundancy | Dismissal by redundancy (s135/136/139). Qualifies (s155). Relevant date 29 May. | Step 5 empty: the precomputed question asked how the payment is computed, not what it is (about 10.5 weeks at £610, about £6,405). |

**Finding.** The mechanism works end to end. Public reasoning from a frontier model
reaches the laptop confidentially, the local model applies it to a private narrative,
every conclusion is grounded and reproducible, and the cloud cannot tell which matter
it served. Grounded is not the same as correct. The 8B model got 2 of 10 conclusions
materially wrong and 1 misleading, and two precomputed questions were badly posed. The
errors are in the work left on the device: date and amount arithmetic, and applying a
rule to facts. Both fixes stay within the architecture:

1. **Deterministic local calculators.** The model only extracts dates and amounts as
   verbatim quotes. Code computes service length, deadlines, and statutory amounts.
2. **Richer offline precompute.** Fact questions with the correct polarity ("is the
   claim still in time?"), per-step pitfall notes ("the cap limits the award; it does
   not negate loss"; "EDT for summary dismissal is the date it is communicated"), and
   calculation specs. This moves more reasoning into the public layer.

Round 1 used v1 procedures and the round-1 harness. Its memos are in
`results/round1/memos/` and its procedures in `results/precomputed/*_v1.json`. The
harness was replaced by `eval/final.py`, which re-runs both round-1 matters as its dev
set.

### Final round: fixes scored against a pre-registered key

**Changes (all within the architecture):**

- **Code does the arithmetic** (`device/calc.py`, `lawtext.py`): service length with
  the s97(2) notice extension, the s111 deadline (including the month-end rule), the
  s124 cap, the s145(5) relevant date, and the s162 payment with the s227 week's-pay
  cap.
- **The cloud precomputes calculation specs:** every statutory number the calculators
  use (15 parameters across s86, s108, s111, s124, s155, s162, s227), each with a
  verbatim quote. The central audit accepts a parameter only if the quote is verbatim
  and contains the number. The device re-checks both against the PIR-fetched statute.
  Nothing is hard-coded.
- **Richer precomputed procedures (v2):** a fixed public step schema. The cloud wrote
  questions phrased from the advice date, pitfall notes, and fact definitions.
- **Verified facts:** the device model extracts dates and amounts with a quote. A fact
  is kept only if the quote is verbatim from the account and contains that date or
  amount. Derived figures (for example weekly pay computed from salary) are rejected.

**Method.** The key and pass rule were written to `eval/final_round_key.json` before
the round ran: 8 held-out matters (5 unfair dismissal, including an s97(2) edge case
and a deadline missed by 4 days; 2 redundancy; 1 employment-adjacent out-of-scope
matter), plus the two round-1 matters as a dev set. Two defects in the code were found
and fixed before the held-out run: a month-end deadline error caught by a unit check
against the key, and a calc prompt that contradicted the audit's minimum quote length.
Nothing was changed after the held-out results were seen.

**Result: pre-registered verdict FAIL** (`eval/final.py`, output in
`results/final_round/`):

| Rule (held-out) | Result | Verdict |
|---|---|---|
| Task selection 8/8 | 7/8 | FAIL |
| Calculator fields 100% | 21/21 | PASS |
| Model-judged fields 90% or more | 9/9 | PASS |
| Wrong answers that passed the gate = 0 | 0 | PASS |
| Security: same query count, 0 leaked, 0 router calls | 56 every matter; 0; 0 | PASS |
| Dev set (round-1 matters, not in the rule) | 11/11 (round 1: 2 wrong, 1 misleading) | n/a |

**Failure.** The out-of-scope matter (pregnancy discrimination; client still employed)
was routed to unfair dismissal instead of refused. Downstream checks caught it: the
device's "dismissed?" step answered NO from the client's words, every calculator
refused for missing verified inputs, and the matter ended as REFER with no advice
issued. The rule still counts this as a failure, correctly, because routing is a gate
and it leaked.

**Other findings not reflected in the score:**

- **Fairness (s98, not scored) regressed in usefulness.** "Unclear" on all 5 held-out
  dismissals, including UD-A, where the account states the reason ("alleged poor
  performance") and no warnings were given. A lawyer would say "likely unfair". The
  model misread a stated reason as missing. This is over-caution.
- **Silent fallback in `device/calc.py`.** When notice was given but its date was not
  verified, the s97(2)/s145(5) material date falls back to the termination date instead
  of refusing. In UD-A this occurred and did not change the answer, but it is incorrect.
  The fix is to raise `Missing("notice_given_date")`. Left as scored so the repo
  reproduces the reported run.

**Conclusion.** Moving arithmetic into code and more reasoning into the public
precomputed layer took the device from 2 wrong and 1 misleading conclusion (round 1) to
30 of 30 held-out conclusions correct (and 9/9 on the dev matters), with zero wrong
answers passing the gate and no change to the cloud's view. The remaining weakness is
closed-set routing on near-miss matters. This can be fixed within the architecture by
making a failed precondition (for example "dismissed = NO") a hard refuse-and-flag
instead of REFER, and by precomputing per-task scope notes for the router. Not
established: performance beyond two task types and ten matters, and legal review of the
precomputed layer.

---

## Reproduce

```bash
python -m keyed.shift                      # verify the shift is an exact symmetry
python -m keyed.engrave 600 3e-4           # engrave (fine-tune) the shifted model
python -m attacks.keyed.weights_align      # attack A vs B over the drift sweep
python -m attacks.keyed.robustness         # drift / perplexity / recovery dilemma
python -m attacks.keyed.traffic            # ciphertext-only unigram attack
python -m attacks.keyed.activations        # read runtime hidden states
python -m attacks.keyed.verdict            # apply the 10% rule, print PASS/FAIL
python -m attacks.cost                     # cost, queueing, FHE reference

# Milestone 3 (blind cloud, sealed device). Needs a legal-rag-router checkout ($LEGAL_RAG_ROUTER)
python -m pir.simplepir                    # PIR correctness and server-view privacy
python -m cloud.precompute                 # build the public statute PIR database
python -m cloud.compile                    # write the public task program
python -m device.harness                   # route locally, fetch via PIR, compose memo
python -m device.select                    # device model: bounded candidate selection
python -m eval.run                         # Milestone 3 security evaluation

# Rich-DB prototype. Needs the router (enrichment only) and Qwen3-8B MLX on the laptop
python -m cloud.richdb                     # offline public enrichment (cached) and rich PIR DB
HF_HUB_OFFLINE=1 python -m eval.final      # final round: 8 held-out and 2 dev matters vs the pre-registered key
```

Sources to cite in the final write-up: Hidden No More (permuted hidden states are
invertible), PUMA and BumbleBee (private-inference MPC costs), SimplePIR and DoublePIR,
vec2vec (unsupervised embedding alignment), WhibOx (white-box crypto history), CaMeL
(capability-based egress).
