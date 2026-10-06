"""Device-side Lane C: the local, deterministic harness.

Runs entirely on the sealed device. It:
  1. ROUTES the firm's natural-language question locally with legal-rag-router
     (no model, no network) -> a bound public coordinate, or a refuse/flag.
  2. Executes the cloud-authored public program: for each step it fetches that
     section's byte-exact statute text from the untrusted cloud via SimplePIR
     (the cloud never learns which section), verifies the sha256, and fills the
     template with {quote} (statute), {fact:*} (LOCAL private facts) and
     {verdict:*} (a deterministic rule choosing one fixed phrasing).
  3. Emits a fully-referenced advice memo. Every statutory sentence carries its
     coordinate and verified sha256; private facts are slotted locally and never
     leave. All egress goes through the EgressGuard.

The cloud side (PIR server, catalogue, program) is simulated in-process but is
reached only through the guard, exactly as a remote cloud would be.
"""
from __future__ import annotations

import json
import os
import re
import sys

import numpy as np

from pir.simplepir import PIRClient, PIRServer
from device.egress import EgressGuard, Tainted

from config import LRR
CLOUD = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "artifacts", "cloud"))
if os.path.join(LRR, "src") not in sys.path:
    sys.path.insert(0, os.path.join(LRR, "src"))


class Cloud:
    """The untrusted cloud: serves PIR answers + public artifacts. Sees only what
    the guard lets the device send: LWE queries and public sync requests."""

    def __init__(self):
        self.D = np.load(os.path.join(CLOUD, "pir_db.npy"))
        self.catalogue = json.load(open(os.path.join(CLOUD, "catalogue.json")))
        self.server = PIRServer(self.D, seed=2024)
        self.seen_queries: list[np.ndarray] = []

    def public_hint(self):
        return self.server.A, self.server.hint()

    def answer(self, qu):
        self.seen_queries.append(qu.copy())
        return self.server.answer(qu)


class Device:
    def __init__(self, cloud: Cloud, case_record: dict, program_path: str):
        self.cloud = cloud
        self.case = case_record
        self.program = json.load(open(program_path))
        self.catalogue = cloud.catalogue            # public, synced to device
        A, H = cloud.public_hint()                  # public
        self.pir = PIRClient(A, H, seed=1)
        self.R_max = max(e["n_rows"] for e in self.catalogue.values())
        secrets = [str(v) for v in case_record.values() if isinstance(v, (str,)) and len(str(v)) > 2]
        self.guard = EgressGuard(secrets)
        # local router (deterministic, no network)
        from legal_rag_router import Router, RouteStatus
        self._RouteStatus = RouteStatus
        self.router = Router.from_path(os.path.join(LRR, "data", "index"))

    # -- Lane C/D: local routing of the firm's actual question ------------------
    def route(self, query: str):
        r = self.router.route(query)
        coords = [c.key if hasattr(c, "key") else str(c) for c in getattr(r, "coordinates", ())]
        return dict(status=r.status.name, next_action=r.next_action.name, coordinates=coords)

    # -- Lane B: fetch a section's exact text via PIR (fixed-schedule) ----------
    def _pir_fetch(self, coordinate: str) -> bytes:
        entry = self.catalogue[coordinate]
        start, n = entry["row"], entry["n_rows"]
        chunks = []
        # fixed schedule: always issue R_max queries, padding with dummy rows, so
        # the number/size of queries is independent of which section is fetched.
        rows_to_get = list(range(start, start + n)) + [0] * (self.R_max - n)
        for k, row in enumerate(rows_to_get):
            qu, s = self.pir.query(row)
            self.guard.send("pir", qu, note=f"fetch {coordinate} chunk {k}")  # declassified LWE
            ans = self.cloud.answer(qu)
            dec = self.pir.decode(ans, s)
            if k < n:
                chunks.append(dec.tobytes())
        raw = b"".join(chunks)[: entry["nbytes"]]
        return raw

    def _quote(self, coordinate: str):
        import hashlib
        raw = self._pir_fetch(coordinate)
        sha = hashlib.sha256(raw).hexdigest()
        verified = (sha == self.catalogue[coordinate]["sha256"])
        return raw.decode("utf-8", "replace"), sha, verified

    # -- deterministic verdict rules (operate on LOCAL private facts) -----------
    def _verdict(self, rule_id: str) -> str:
        v = self.program["verdicts"][rule_id]
        env = dict(self.case)
        try:
            truth = bool(eval(v["rule"], {"__builtins__": {}}, env))  # closed rule set
        except Exception:
            truth = False
        return v["true"] if truth else v["false"]

    # -- Lane C: run the program into a referenced memo -------------------------
    def advise(self):
        prov = []
        out = [f"# {self.program['title']}", ""]
        fact_re = re.compile(r"\{fact:(\w+)\}")
        verd_re = re.compile(r"\{verdict:(\w+)\}")
        for step in self.program["steps"]:
            coord = step["coordinate"]
            quote, sha, verified = self._quote(coord)
            prov.append(dict(step=step["id"], coordinate=coord, sha256=sha,
                             verified=verified, nbytes=len(quote.encode())))
            text = step["template"]
            text = text.replace("{quote}", _indent_quote(quote))
            text = verd_re.sub(lambda m: self._verdict(m.group(1)), text)
            text = fact_re.sub(lambda m: str(self.case.get(m.group(1), f"[missing:{m.group(1)}]")), text)
            out.append(text)
        memo = "\n".join(out)
        # the memo is tainted (contains private facts); it stays on the device.
        return Tainted(memo, "advice_memo"), prov


def _indent_quote(q: str) -> str:
    return "\n".join("    > " + ln for ln in q.splitlines())


DEMO_CASE = {
    "client_name": "Northbridge Logistics Ltd (claimant: A. Okafor)",
    "employer": "Meridian Freight plc",
    "service_length_months": 31,
    "dismissal_date": "2026-03-12",
    "claim_filed_date": "2026-05-20",
    "months_to_file": 2,
    "reason_given": "alleged gross misconduct (unauthorised absence)",
    "gross_annual_salary": "GBP 48,500",
}


def run_demo(query="Does section 98 of the Employment Rights Act 1996 make our client's dismissal unfair?"):
    cloud = Cloud()
    prog = os.path.join(CLOUD, "program_uk_unfair_dismissal_advice.json")
    dev = Device(cloud, DEMO_CASE, prog)
    routed = dev.route(query)
    memo, prov = dev.advise()
    return dev, routed, memo, prov


if __name__ == "__main__":
    dev, routed, memo, prov = run_demo()
    print("LOCAL ROUTE of the firm's question:")
    print(f"  {routed}\n")
    print("PROVENANCE (each statute quote, fetched via PIR, sha256-verified):")
    for p in prov:
        print(f"  step {p['step']:<18} {p['coordinate']:<26} verified={p['verified']} "
              f"sha={p['sha256'][:12]} ({p['nbytes']}B)")
    print(f"\nPIR queries the cloud saw: {len(dev.cloud.seen_queries)} "
          f"(fixed {dev.R_max}/section x {len(prov)} sections)")
    print(f"egress log: {len(dev.guard.log)} sends, all allowed="
          f"{all(r['allowed'] for r in dev.guard.log)}")
    print("\n================ ADVICE MEMO (stays on device) ================\n")
    print(memo.value[:1600])
