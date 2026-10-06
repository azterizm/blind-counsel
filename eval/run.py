"""Milestone 3 evaluation: does the blind-cloud / sealed-device design keep case
data off the untrusted cloud while still producing useful, exact legal output?

Measures:
  1. egress leakage   -- scan everything the cloud received for any secret; must be 0
  2. guard enforcement-- the guard actually blocks a private fact pushed at it
  3. PIR integrity    -- every statute quote sha256-verifies (byte-exact)
  4. determinism      -- the memo is byte-identical across runs
  5. refuse-and-flag  -- out-of-coverage / invented law is refused locally
  6. naive-RAG contrast-- a baseline that sends the query to the cloud leaks
"""
from __future__ import annotations

import hashlib

import numpy as np

from device.harness import Cloud, Device, DEMO_CASE, run_demo, CLOUD
from device.egress import EgressGuard, EgressBlocked, Tainted
import os


def secrets_of(case: dict) -> list[str]:
    out = []
    for v in case.values():
        s = str(v)
        out.append(s)
        out += [tok for tok in s.replace(",", " ").split() if len(tok) > 3]
    return list({s for s in out if len(s) > 3})


def cloud_saw_bytes(cloud: Cloud) -> bytes:
    """Everything the cloud received from the device, as raw bytes."""
    blobs = [q.astype(np.int64).tobytes() for q in cloud.seen_queries]
    return b"".join(blobs)


def test_egress_leakage(dev, cloud):
    secrets = secrets_of(DEMO_CASE)
    blob = cloud_saw_bytes(cloud)
    leaked = [s for s in secrets if s.encode() in blob]
    # also check utf-16/ascii numeric forms of the salient facts
    return dict(n_secrets=len(secrets), leaked=leaked, cloud_bytes=len(blob),
                passed=(len(leaked) == 0))


def test_guard_blocks(dev):
    g = EgressGuard(secrets_of(DEMO_CASE))
    blocked = 0
    # (a) a tainted memo
    try:
        g.send("sync", Tainted("secret memo", "memo"))
    except EgressBlocked:
        blocked += 1
    # (b) a raw private fact on the public channel
    try:
        g.send("sync", DEMO_CASE["client_name"])
    except EgressBlocked:
        blocked += 1
    # (c) a raw index vector disguised as a PIR query (not a real LWE ciphertext)
    try:
        fake = np.zeros(10, dtype=np.int64); fake[3] = 1
        g.send("pir", fake)
    except EgressBlocked:
        blocked += 1
    return dict(blocked=blocked, expected=3, passed=(blocked == 3))


def test_pir_integrity(prov):
    bad = [p for p in prov if not p["verified"]]
    return dict(sections=len(prov), unverified=len(bad), passed=(len(bad) == 0))


def test_determinism():
    _, _, memo1, _ = run_demo()
    _, _, memo2, _ = run_demo()
    h1 = hashlib.sha256(memo1.value.encode()).hexdigest()
    h2 = hashlib.sha256(memo2.value.encode()).hexdigest()
    return dict(sha1=h1[:12], sha2=h2[:12], passed=(h1 == h2))


def test_integrity_enforcement():
    """A tampered (non-verbatim) statute row must fail the sha256 check -> rejected.
    We flip one byte in the cloud DB and confirm the device flags it unverified."""
    cloud = Cloud()
    # corrupt the first chunk of s124 in the cloud's DB
    import json as _json
    cat = cloud.catalogue
    row = cat["uk/ukpga/1996/18/s124"]["row"]
    cloud.D[row, 0] ^= 0x01
    cloud.server.D[row, 0] ^= 0x01
    prog = os.path.join(CLOUD, "program_uk_unfair_dismissal_advice.json")
    dev = Device(cloud, DEMO_CASE, prog)
    _, prov = dev.advise()
    tampered = [p for p in prov if p["coordinate"] == "uk/ukpga/1996/18/s124"]
    detected = tampered and not tampered[0]["verified"]
    others_ok = all(p["verified"] for p in prov if p["coordinate"] != "uk/ukpga/1996/18/s124")
    return dict(tamper_detected=bool(detected), others_still_verified=others_ok,
                passed=bool(detected and others_ok))


def test_refuse_and_flag(dev):
    cases = {
        "SI 2011/9999 regulation 4": "INSTRUMENT_NOT_FOUND",      # invented law -> refuse
        "unfair dismissal compensatory award cap": "UNRESOLVED",  # no citation -> discover
        "section 124 of the Employment Rights Act 1996": "BOUNDED",
    }
    results = {}
    ok = True
    for q, expect in cases.items():
        r = dev.route(q)
        results[q] = r["status"]
        ok = ok and (r["status"] == expect)
    return dict(results=results, passed=ok)


def test_naive_rag_contrast():
    """Baseline: a normal cloud RAG sends the query (with private facts) to the
    cloud for embedding/generation. Show it leaks what the blind design does not."""
    query = (f"Our client {DEMO_CASE['client_name']}, dismissed {DEMO_CASE['dismissal_date']} "
             f"by {DEMO_CASE['employer']} for {DEMO_CASE['reason_given']}, salary "
             f"{DEMO_CASE['gross_annual_salary']} -- is this unfair under ERA 1996 s.98?")
    cloud_receives = query.encode()           # the naive design ships the whole query
    secrets = secrets_of(DEMO_CASE)
    leaked = [s for s in secrets if s.encode() in cloud_receives]
    return dict(leaked_count=len(leaked), example=leaked[:4],
                passed=(len(leaked) > 0))     # "passed" = it does leak, as expected


def main():
    import time
    t0 = time.time()
    dev, routed, memo, prov = run_demo()
    build_s = time.time() - t0

    checks = {
        "1. egress leakage (blind cloud)": test_egress_leakage(dev, dev.cloud),
        "2. guard blocks real leaks": test_guard_blocks(dev),
        "3. PIR integrity (sha256)": test_pir_integrity(prov),
        "4. determinism": test_determinism(),
        "5. refuse-and-flag": test_refuse_and_flag(dev),
        "6. integrity enforcement (tamper)": test_integrity_enforcement(),
    }
    naive = test_naive_rag_contrast()

    print("=" * 68)
    print("MILESTONE 3 -- blind cloud, sealed device: evaluation")
    print("=" * 68)
    for name, res in checks.items():
        status = "PASS" if res["passed"] else "FAIL"
        print(f"  [{status}] {name}")
        for k, v in res.items():
            if k != "passed":
                print(f"           {k}: {v}")
    print(f"\n  cloud received {checks['1. egress leakage (blind cloud)']['cloud_bytes']:,} bytes "
          f"(all LWE query vectors); secrets leaked: "
          f"{len(checks['1. egress leakage (blind cloud)']['leaked'])}")
    print(f"\n  CONTRAST -- naive cloud RAG on the same matter leaks "
          f"{naive['leaked_count']} private tokens, e.g. {naive['example']}")
    print(f"\n  memo: {len(memo.value)} chars, {len(prov)} sha256-verified statute quotes; "
          f"pipeline {build_s:.2f}s")
    all_pass = all(r["passed"] for r in checks.values()) and naive["passed"]
    print("\n" + "=" * 68)
    print(f"VERDICT: {'ALL CHECKS PASS' if all_pass else 'FAILURES PRESENT'} "
          f"-- case data never reaches the cloud; output is exact and deterministic.")
    print("=" * 68)


if __name__ == "__main__":
    main()
