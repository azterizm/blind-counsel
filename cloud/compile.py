"""Cloud-side Lane A: compile a typed workflow program for a legal TASK TYPE.

The cloud model sees only the public task description (here: "advise on a UK
ordinary unfair-dismissal claim"). It emits a JSON program: an ordered list of
steps, each naming a public statute coordinate and a template. Templates contain
only three kinds of hole:

  {quote}          -> filled on the device with byte-exact statute text (via PIR)
  {fact:NAME}      -> filled on the device from the LOCAL case record (never leaves)
  {verdict:RULE}   -> filled on the device by a deterministic rule choosing one of a
                      FIXED set of phrasings (a selection, never free generation)

No case data is present in this program; it is public and the same for every matter
of this type. It is written to artifacts/cloud/program_<task>.json.
"""
from __future__ import annotations

import json
import os

ART = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "artifacts", "cloud"))

UNFAIR_DISMISSAL = {
    "task": "uk_unfair_dismissal_advice",
    "jurisdiction": "uk",
    "title": "Advice: ordinary unfair dismissal (UK, Employment Rights Act 1996)",
    "steps": [
        {
            "id": "right",
            "coordinate": "uk/ukpga/1996/18/s94",
            "template": "1. The right. Section 94 ERA 1996:\n{quote}\n",
        },
        {
            "id": "qualifying_period",
            "coordinate": "uk/ukpga/1996/18/s108",
            "template": ("2. Qualifying period. Section 108 ERA 1996:\n{quote}\n"
                         "The client's continuous service is {fact:service_length_months} months. "
                         "{verdict:qualifying_period}\n"),
        },
        {
            "id": "fairness",
            "coordinate": "uk/ukpga/1996/18/s98",
            "template": ("3. Fairness of the reason. Section 98 ERA 1996:\n{quote}\n"
                         "The employer's stated reason was: {fact:reason_given}. "
                         "This must fall within a potentially fair reason and be handled reasonably.\n"),
        },
        {
            "id": "time_limit",
            "coordinate": "uk/ukpga/1996/18/s111",
            "template": ("4. Time limit. Section 111 ERA 1996:\n{quote}\n"
                         "Dismissal {fact:dismissal_date}; claim filed {fact:claim_filed_date} "
                         "({fact:months_to_file} months later). {verdict:time_limit}\n"),
        },
        {
            "id": "compensation_cap",
            "coordinate": "uk/ukpga/1996/18/s124",
            "template": ("5. Compensatory award cap. Section 124 ERA 1996:\n{quote}\n"
                         "The client's gross annual pay is {fact:gross_annual_salary}; the statutory "
                         "cap may limit the compensatory award accordingly.\n"),
        },
    ],
    # deterministic verdict rules: each maps to a fixed, closed set of phrasings.
    "verdicts": {
        "qualifying_period": {
            "rule": "service_length_months >= 24",
            "true": "On these facts the two-year qualifying period in s.108 is met.",
            "false": "On these facts the two-year qualifying period in s.108 is NOT met, so an "
                     "ordinary unfair-dismissal claim is likely barred (check the automatically-unfair exceptions).",
        },
        "time_limit": {
            "rule": "months_to_file <= 3",
            "true": "The claim appears to be within the three-month primary time limit in s.111.",
            "false": "The claim appears to be OUT OF TIME under s.111; an extension would have to be argued.",
        },
    },
}


def build():
    os.makedirs(ART, exist_ok=True)
    path = os.path.join(ART, "program_uk_unfair_dismissal_advice.json")
    json.dump(UNFAIR_DISMISSAL, open(path, "w"), indent=2)
    coords = [s["coordinate"] for s in UNFAIR_DISMISSAL["steps"]]
    print(f"compiled public program -> {os.path.basename(path)}")
    print(f"  task: {UNFAIR_DISMISSAL['task']}  | {len(UNFAIR_DISMISSAL['steps'])} steps")
    print(f"  cites coordinates (public): {coords}")
    print("  contains NO case data.")
    return path


if __name__ == "__main__":
    build()
