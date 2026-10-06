# Confidential LLM inference without TEEs — report

**Question.** Can a law firm (later: healthcare) run an open-weight LLM on an
untrusted cloud so that the operator — who has full physical and software access,
and is treated as the adversary — cannot read the case data, *without* trusting
any hardware root (no SEV/TDX/GPU-CC, no chip-maker trust)?

**Design under test — (a), the firm's preferred one.** The firm generates a
key pair locally. It applies a function-preserving "shift" to an open base model
using the key (a residual-stream rotation, a vocabulary permutation, and per-layer
MLP/head permutations), keeping the private key in-house. The lab supplies only the
base model and the hardware and "engraves" the firm's data by fine-tuning the
shifted model on the firm's (encoded) corpus. At serve time the firm encodes its
queries with the key; the operator is supposed to see only "gibberish" weights,
inputs, activations and outputs.

**Pass/fail rule (fixed before running, set by the firm).** Design (a) *fails* if
any attack recovers **≥ 10 %** of the secret test tokens. The primary count
**excludes the 200 most frequent public tokens** (stopwords/punctuation — frequency
analysis gets those for free and they reveal nothing). Names/amounts/dates alone are
not secrets and are reported for information only.

---

## Verdict

**Design (a) FAILS, decisively and in every configuration tested.** A cloud
operator recovers **100 % of the secret content** in the realistic setting, using
only the public base model and what the operator legitimately holds. There is **no
operating point that is both usable and safe.**

The cause is structural, not a tuning artifact: the shift is a *global linear
symmetry* of the network. Its generators are recoverable from **drift-robust bulk
statistics** of the public-vs-deployed weights:

- the **vocabulary permutation π** is a token substitution cipher; the rotation
  preserves each embedding row's L2 norm exactly, so π falls out of the row norms;
- the **residual rotation R** is recovered from the embedding **covariance**
  (`EᵀE` transforms as `RᵀE_baseᵀE_base R`), a statistic over all 49 152 rows that a
  realistic fine-tune barely moves.

Recovering π alone lets the operator read every encoded token stream (corpus,
queries, outputs) as plaintext. Recovering R additionally exposes the hidden states
— the model's intermediate "reasoning" — in plaintext.

---

## Setup (fully local simulation)

| Role | Played by |
|---|---|
| Base model | `HuggingFaceTB/SmolLM2-135M` (Llama arch; hidden 576, 30 layers, vocab 49 152, tied embeddings — untied for the shift) |
| Firm private corpus | CUAD contract text (511 PDFs → 26.7 M chars → 5.26 M encoded fine-tune tokens). The attacker never sees it. |
| Attacker reference corpus | wikitext-103 (legal-vs-wiki domain mismatch — this *favors the defender*) |
| Secret test set | 400 passages: 200 synthetic privileged paragraphs + 200 held-out contract passages (disjoint from the fine-tune split) |
| Attacker's knowledge | the public base model + public English statistics only |

**The shift is an exact symmetry.** `keyed/shift.py` folds each RMSNorm γ into the
following linear, rotates the residual by an orthogonal `R`, permutes the MLP
intermediate and the attention heads (GQA groups kept intact), and permutes the
vocabulary. Verified on real weights:

```
argmax agreement : 100.0 %      mean cosine : 1.000000
max |Δlogit|     : 1.0e-3 (float32)  →  1.1e-5 (float64)   # numerical, not structural
```

---

## Attacks and measurements

All numbers are measured on an M-series laptop (MPS) and are reproducible with the
commands in the README.

### 1. Clean upload — the operator snapshots the shifted weights before fine-tuning
The plan's own role split ("the firm uploads the shifted weights, the lab then
fine-tunes") means the operator first sees an *exact* symmetry of the public model.

| metric | result |
|---|---|
| π recovered from embedding row norms | **99.98 %** (< 1 s) |
| secret recovery (content / all) | **100 % / 100 %** |
| longest verbatim run | 204 tokens |

Decoded sample (operator's output):
> *"Memo to file re Northbridge Capital v. the regulator: exposure on the indemnity
> claim is approximately $70,000; recommend we do not produce the internal
> post-closing audit absent a protective order."*

### 2. Fine-tuned model only (the charitable case for the design)
A real gentle fine-tune (lr 3e-4) of the shifted model on the firm's encoded
contracts. As it adapts, the model gets *better* on the firm's domain (perplexity
falls below baseline) — and stays fully readable. Two attacks at each checkpoint:

| step | real drift | perplexity ×base | A norm-sort content % | **B covariance content %** | B verbatim run |
|---:|---:|---:|---:|---:|---:|
| 0   | 0.000 | ×1.00 | 100.0 | **100.0** | 204 |
| 50  | 0.002 | ×1.74 | 2.0   | **100.0** | 204 |
| 120 | 0.005 | ×1.23 | 0.8   | **100.0** | 204 |
| 250 | 0.009 | ×0.95 | 0.5   | **100.0** | 204 |
| 400 | 0.013 | ×0.88 | 0.2   | **100.0** | 204 |
| 600 | 0.018 | ×0.83 | 0.3   | **100.0** | 204 |

Attack A (a brittle 1-D global sort) is destroyed by even 0.2 % drift — this is the
"fine-tuning defeats weight-matching" effect reported earlier, reproduced on real
weights. Attack B, which recovers the rotation from a bulk statistic, is **immune**:
100 % content and a 204-token verbatim decode at every checkpoint, *including the
most-engraved, best-perplexity model.* Validated identical (100 %) across four
independent keys.

### 3. The defender's dilemma (controlled drift sweep)
Synthetic per-row drift injected into the clean shifted embedding, measuring the
model's perplexity *and* attack B at each level:

| drift (mean rel) | perplexity ×base | attack B content % |
|---:|---:|---:|
| 0.00 | ×1.0 | 100.0 |
| 0.05 | ×1.0 | 100.0 |
| 0.10 | ×1.1 | 88.1 |
| 0.15 | ×1.3 | 45.6 |
| 0.20 | ×1.6 | 19.2 |
| 0.25 | ×2.1 | 10.4 |
| **0.30** | **×2.9** | **3.3** |
| 0.40 | ×7.6 | 0.0 |

Attack B drops below the 10 % fail threshold **only at drift ≈ 0.3, where perplexity
is already ×2.9** — a wrecked model. A real, usable fine-tune produces drift ≈ 0.004
(perplexity ×1.08), deep in the 100 %-recovery zone. **There is no usable-and-safe
operating point.** (A high-learning-rate fine-tune that reaches large drift fast was
also tried; it diverges — perplexity ×44 at drift 1.4 % — i.e. you destroy the model
*before* you reach protective drift.)

### 4. Ciphertext-only traffic analysis (no weights at all) — honest negative
Treating π as a substitution cipher and matching unigram frequencies of the observed
5.26 M encoded tokens against public wikitext statistics:

| metric | result |
|---|---|
| π recovery | 0.01 % |
| secret content recovery | **0.0 %** |

Frequency analysis *alone* does **not** break π: a 49 k-token alphabet plus the
legal-vs-wiki domain mismatch defeats naive matching. This is a point in the
design's favor — but it is moot, because the weight-based attack (2–3) succeeds
completely. (Classical bigram hill-climbing would improve this; not needed here.)

### 5. Runtime activations — the reasoning leaks too
With R recovered from the weights, the operator un-rotates the serve-time hidden
states and reads them with the public model's logit lens:

```
secret query: "the settlement figure of $70,000 must remain sealed"
layer-0 reconstruction accuracy: 100.0 %
  -> "the settlement figure of $70,000 must remain sealed"
```

### Enrichment variants E1/E2/E3
- **E1 (data frozen in at engraving — full fine-tune):** the *only* variant that
  moves the base embedding at all, hence the best case for the defender. Still 100 %
  (rows 1–3 above).
- **E2 (encoded docs in the context window)** and **E3 (LoRA on top):** leave the
  base embedding **byte-identical** to the clean shift, so attack B gets 100 %
  immediately (the drift-0 row). Broken by construction.

So E1 is the attacker's worst case, and it falls; therefore all three fall.

---

## Cost of pursuing (a) anyway, and why (b) FHE is excluded

Because each firm key yields a *distinct* model, nothing batches across firms:

- **Engraving** cost is linear in users: a 70 B model at 1 B tokens/user ≈ **$729 /
  user** (~$0.7 M per 1 000-user fleet); heavier domain adaptation scales up
  proportionally.
- **1:1 queued serving** (Erlang C, 1 000 users × 20 req/day, mean wait < 10 s):
  ~9 GPUs ($179/day) for 8 B per user, ~136 GPUs ($2 709/day) for 70 B per user, at
  the stated assumptions — and it isolates users from *each other*, never from the
  operator.
- **(b) FHE** (literature, Llama-2-7B at 33–85 s/token on 8 GPUs): **4.6–11.8 h and
  $92–236 per 500 tokens** — 3–5 orders of magnitude worse than native serving.
  Excluded as infeasible, as the firm directed.

---

## Recommendation: "blind cloud, sealed device" (Milestone 3)

Since any model the cloud can run on case data, the cloud operator can read, the
only way to meet a zero-trust threat model without a hardware root is to **never let
the cloud hold readable case data**:

- **Compile:** the cloud model authors typed workflow programs/templates per legal
  task type — nothing case-specific leaves the device.
- **Private lookup:** precomputed analysis over *public* legal signatures, fetched
  with SimplePIR (LWE; server view independent of the query).
- **Local harness:** a deterministic interpreter on the device; the small on-device
  model only *selects* among candidates. Every value carries a byte-exact
  `(doc, start, end, sha256)` reference.
- **Egress guard + refuse-and-flag:** one taint-tracked, fixed-size/fixed-schedule
  egress; anything open-ended over novel facts is refused and flagged.

## Milestone 3 — the blind-cloud PoC, built and measured

Built on the real `legal-rag-router` (UK legislation, 134,219 documents, OGL-3.0)
and a working **SimplePIR**. Demo matter: UK ordinary unfair-dismissal advice over
the Employment Rights Act 1996.

- **Lane A (compile, cloud):** a public JSON task program citing statute coordinates
  with `{quote}`/`{fact}`/`{verdict}` holes. No case data (`cloud/compile.py`).
- **Lane B (private lookup):** the cloud serves a 654-row × 2 KB PIR matrix of
  per-section statute text (`cloud/precompute.py`). The device fetches each cited
  section via SimplePIR — correctness 5/5, and the server's query distribution is
  independent of the index (mean ≈ Q/2 whichever row is wanted; `pir/simplepir.py`).
- **Lane C (local harness):** `legal-rag-router` binds the firm's question locally
  (no model, no network); statute text is fetched via PIR, **sha256-verified
  byte-for-byte**, and slotted into the template with private facts filled from the
  **local** case record (`device/harness.py`). The device model only *selects* among
  public candidate coordinates in discover-then-bind — never generates law
  (`device/select.py`).
- **Lane D + egress guard:** invented law / no-citation are refused and flagged; a
  CaMeL-style taint guard permits only LWE PIR queries and public sync off-device
  (`device/egress.py`).

**Evaluation (`eval/run.py`), all pass:**

| check | result |
|---|---|
| Egress leakage (blind cloud) | **0** of 17 secrets in the 575,520 bytes the cloud received (all LWE vectors) |
| Guard blocks real leaks | 3/3 (tainted memo, raw fact, fake PIR query) |
| PIR integrity | 5/5 statute quotes sha256-verified byte-exact |
| Determinism | memo byte-identical across runs (same sha256) |
| Refuse-and-flag | invented law → refuse; no citation → discover; valid → bind |
| Integrity enforcement | a one-byte DB tamper is detected (sha256 mismatch), others still verify |
| **Contrast: naive cloud RAG** | leaks **16** private tokens (client, employer, dates, salary) on the same matter |

The memo is a genuine, fully-referenced advice note (11,963 chars, 5 verified
statutory quotes) composed entirely on the device. **Case data never reaches the
cloud; the output is exact and deterministic.**

Caveats: the on-device model is the cached SmolLM2-135M stand-in (production:
Qwen2.5-3B), so *selection quality* is weak — the concept index's own score is a
better ranker; the property demonstrated is the bounded, local, non-generative
selection, not its accuracy. The PIR database here is one Act; the fixed-schedule
fetch (22 queries/section) is sized by the largest ERA section. These are PoC
scales, not production tuning.

---

## Rich-DB prototype — precomputed public reasoning, applied privately on the laptop

**Question tested.** Can the model do real reasoning over a client's situation *plus* the
retrieved law — without the cloud seeing the situation — if the hard, fact-independent
legal reasoning is precomputed offline and fetched by PIR?

**Split of roles (no trust displaced):**
- **Cloud, offline, public only:** `gemini-3.8-flash-high` via the router enriched 14 ERA
  1996 provisions across two task types (unfair dismissal; redundancy pay) into **26
  reasoning entries**: 14 explanations (summary, legal elements, thresholds, each element
  tied to a verbatim statutory quote), 10 relations (from a deterministic link graph:
  explicit cross-references + defined terms such as "effective date of termination"),
  and 2 decision procedures. A central audit dropped every claim whose quote is not in the
  statute (e.g. s124 6→5, s136 6→5). The router never sees a client: it only ever sees
  public statute text, so it needs no trust (`cloud/reason.py`).
- **Cloud, online:** a 696-row PIR DB = all 431 ERA section texts + the 26 entries
  (`cloud/richdb.py`). Every matter issues exactly **48** PIR queries.
- **Device = the laptop:** Qwen3-8B (4-bit MLX, pinned revision) runs offline. It picks
  the task from the public task index (or refuses), fetches everything in one fixed
  batch, re-verifies hashes and the cloud's quotes, answers each procedure step over the
  private account, and every answer passes a grounding gate (`device/reasoner.py`).
  A hosted GPU was rejected for this role: it would displace trust, not remove it.

**Round 1 evaluation (three confidential matters) — all 7 checks pass:**

| check | result |
|---|---|
| Task selection | dismissal → unfair-dismissal; redundancy → redundancy-pay; tenancy deposit → **refused** (out of scope) |
| Cloud view | **48 queries for every matter**, same statistics — task type and answered-vs-refused are invisible |
| Egress | **0** of 17 / 12 / 7 narrative secrets reached the cloud; **0** cloud-LLM calls during matters (tripwire) |
| Integrity | 0 hash failures; cloud's statutory quotes re-verified **on the device**: 49/49, 37/37 |
| Grounding | every yes/no conclusion cites verbatim client facts + fetched provisions (one step with a non-verbatim quote auto-downgraded to "unclear") |
| Anti-fabrication | invented client quote and fake `s999` authority rejected |
| Determinism | memo byte-identical across runs |

**Substance audit (read by hand) — the part the checks cannot see:**

| Matter | Correct | Wrong / misleading |
|---|---|---|
| Unfair dismissal | dismissed (s95); likely unfair — no investigation/hearing (s98) | **qualifying period: said "<2 years" for 2 y 7 m** (date arithmetic); **compensation: said "no loss"** (confused the s124 cap with loss); time limit framed as missed when ~4 weeks remain; EDT given as letter date |
| Redundancy | dismissal by redundancy (s135/136/139); qualifies (s155); relevant date 29 May | step 5 vacuous — the precomputed question asked *how* the payment is computed, not *what it is* (≈10.5 weeks × £610 ≈ £6,405) |

**Finding.** The mechanism works end to end: frontier-quality public reasoning flows to the
laptop confidentially, the local model applies it to a private narrative, every
conclusion is grounded and reproducible, and the cloud cannot tell what matter it served.
But **grounded is not correct**: the 8B model got 2 of 10 conclusions materially wrong and
1 misleading, and two precomputed questions were badly posed. The errors cluster exactly
where the design leaves work on the device — date/amount arithmetic and applying a rule
to facts. Both fixes stay within the architecture:
1. **Deterministic local calculators** — the model only extracts dates/amounts as verbatim
   quotes; code computes service length, deadlines and statutory amounts.
2. **Richer offline precompute** — fact-questions with the right polarity ("is the claim
   still in time?"), per-step pitfall notes ("the cap limits the award; it does not negate
   loss"; "EDT for summary dismissal is the date it is communicated"), and calculation
   specs. This is the thesis applied harder: move more reasoning into the public layer.

(Round 1 ran with v1 procedures and the round-1 harness; its memos are kept in
`artifacts/device_out/round1/` and its procedures in `…/reasoning/*_v1.json`. The harness
was superseded by `eval/final.py`, which re-runs both round-1 matters as its dev set.)

### Final round — the fixes, scored against a pre-registered key

**What changed (all within the architecture):**
- **Code does the arithmetic** (`device/calc.py`, `lawtext.py`): service length with the
  s97(2) notice extension, the s111 deadline (incl. the month-end rule), the s124 cap,
  the s145(5) relevant date, the s162 payment with the s227 week's-pay cap.
- **The cloud precomputes calculation specs**: every statutory number the calculators use
  (15 parameters across s86, s108, s111, s124, s155, s162, s227) with a verbatim quote. The
  central audit accepts a parameter only if the quote is verbatim *and* the number is in
  it; the device re-checks both against the PIR-fetched statute. Nothing is hard-coded.
- **Richer precomputed procedures** (v2): a fixed public step schema; the cloud wrote
  questions phrased from the advice date, pitfall notes, and fact definitions.
- **Verified facts**: the device model extracts dates/amounts with a quote; a fact is kept
  only if the quote is verbatim from the account *and contains that date/amount* — derived
  figures (e.g. weekly pay computed from salary) are rejected.

**Method.** The key and pass rule were written to `eval/final_round_key.json` before the
round ran: 8 held-out matters (5 unfair dismissal incl. a s97(2) edge case and a deadline
missed by 4 days; 2 redundancy; 1 employment-adjacent out-of-scope matter), plus the two
round-1 matters as a dev set. Two defects in my own code were found and fixed *before* the
held-out run (a month-end deadline error caught by a unit check against the key; a calc
prompt that contradicted the audit's minimum quote length). Nothing was changed after the
held-out results were seen.

**Result — pre-registered verdict: FAIL** (`eval/final.py`, output in
`artifacts/final_round.log`, `artifacts/device_out/final/`):

| rule (held-out) | result | |
|---|---|---|
| Task selection 8/8 | **7/8** | **FAIL** |
| Calculator fields 100% | 21/21 | PASS |
| Model-judged fields ≥ 90% | 9/9 | PASS |
| Wrong answers that passed the gate = 0 | 0 | PASS |
| Security: same query count, 0 leaked, 0 router calls | 56 every matter; 0; 0 | PASS |
| Dev set (round-1 matters, not in the rule) | 11/11 (round 1: 2 wrong, 1 misleading) | — |

**What the failure was.** The out-of-scope matter (pregnancy discrimination; the client is
still employed) was routed to unfair dismissal instead of refused. Downstream checks
caught it: the device's own "dismissed?" step answered NO from the client's words, every
calculator refused for missing verified inputs, and the matter ended as **REFER** — no
advice was issued. The rule still counts it as a failure, correctly: routing is a gate
and it leaked.

**Other findings the score does not show:**
- **Fairness (s98, not scored) regressed in usefulness:** "unclear" on all 5 held-out
  dismissals, including UD-A where the account states the reason ("alleged poor
  performance") and no warnings were given — a lawyer would say "likely unfair". The model
  misread a stated reason as missing. Over-caution, not caution.
- **A silent fallback in `device/calc.py`:** when notice was given but its date was not
  verified, the s97(2)/s145(5) "material date" falls back to the termination date instead
  of refusing. In UD-A this happened and did not change the answer, but it is wrong in
  principle; the fix is to raise `Missing("notice_given_date")`. Left as scored so the repo
  reproduces the reported run.

**What this establishes.** Moving arithmetic into code and more reasoning into the public
precomputed layer took the device from 2 wrong + 1 misleading conclusion (round 1) to **30
of 30 held-out conclusions correct** (and 9/9 on the dev matters), with zero wrong answers
passing the gate and the cloud's view unchanged. The remaining weakness is the closed-set
routing step on near-miss matters — fixable inside the architecture by making a failed
precondition (e.g. "dismissed = NO") a hard refuse-and-flag rather than a REFER, and by
precomputing per-task scope notes for the router. Not established: performance beyond two
task types and ten matters, and legal review of the precomputed layer.

---

## Reproduce

```bash
python -m keyed.shift                      # verify the shift is an exact symmetry
python -m keyed.engrave 600 3e-4           # engrave (fine-tune) the shifted model
python -m attacks.keyed.weights_align      # attack A vs B over the drift sweep
python -m attacks.keyed.robustness         # the drift / perplexity / recovery dilemma
python -m attacks.keyed.traffic            # ciphertext-only unigram attack
python -m attacks.keyed.activations        # read runtime hidden states
python -m attacks.keyed.verdict            # apply the 10% rule -> PASS/FAIL
python -m attacks.cost                     # cost + queueing + FHE reference

# Milestone 3 (blind cloud, sealed device) -- needs a legal-rag-router checkout ($LEGAL_RAG_ROUTER)
python -m pir.simplepir                    # PIR correctness + server-view privacy
python -m cloud.precompute                 # build the public statute PIR database
python -m cloud.compile                    # author the public task program
python -m device.harness                   # route locally, fetch via PIR, compose memo
python -m device.select                    # device model: bounded candidate selection
python -m eval.run                         # the Milestone 3 security evaluation

# Rich-DB prototype -- needs the router (enrichment only) and Qwen3-8B MLX on the laptop
python -m cloud.richdb                     # offline public enrichment (cached) + rich PIR DB
HF_HUB_OFFLINE=1 python -m eval.final      # final round: 8 held-out + 2 dev matters vs the pre-registered key
```

Sources to cite in the final write-up: Hidden No More (permuted hidden states are
invertible), PUMA / BumbleBee (private-inference MPC costs), SimplePIR/DoublePIR,
vec2vec (unsupervised embedding alignment), WhibOx (white-box crypto history),
CaMeL (capability-based egress).
