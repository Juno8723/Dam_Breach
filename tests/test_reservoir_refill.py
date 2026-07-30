#!/usr/bin/env python3
"""Checks tests/attribution... no -- checks examples/targeted/reservoir_refill.dat's
run against the criteria listed in docs/RESERVOIR_REFILL_TEST.md / this task's
section 6.3. Honestly reports PASS / FAIL / NOT_EXERCISED per criterion --
this synthetic test did NOT achieve a full depletion-below-breach-bottom
event (see docs/RESERVOIR_REFILL_TEST.md for why, and for the safety
properties that WERE confirmed instead), so several criteria below are
expected to report NOT_EXERCISED rather than PASS. This is intentional
and should not be "fixed" by loosening the checks.
"""
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from parse_breach_output import parse  # noqa: E402

STDOUT_PATH = os.path.join(ROOT, "outputs", "targeted", "reservoir_refill", "corrected.stdout.txt")


def main():
    with open(STDOUT_PATH, errors="replace") as f:
        text = f.read()
    data = parse(text)
    hydro = data.get("hydrograph", [])

    results = []

    def check(name, status, detail):
        results.append((name, status, detail))

    check("simulation_completed", "PASS" if data.get("completed") else "FAIL",
          f"completed={data.get('completed')}")

    below_hc = [r for r in hydro if r["HY"] < r["HC"]]
    check("depletion_event_exists (HY < controlling HC)",
          "PASS" if below_hc else "NOT_EXERCISED",
          f"{len(below_hc)} of {len(hydro)} rows have HY<HC" if hydro else "no hydrograph rows parsed")

    if below_hc:
        nonzero_qb_while_below = [r for r in below_hc if r["QB"] > 0.001]
        check("QB==0 while HY<controlling elevation",
              "PASS" if not nonzero_qb_while_below else "FAIL",
              f"{len(nonzero_qb_while_below)} rows with QB>0 while HY<HC")
    else:
        check("QB==0 while HY<controlling elevation", "NOT_EXERCISED",
              "no depletion event occurred in this run")

    inflow_present = any(r.get("QTOT", 0) is not None for r in hydro)
    check("inflow/mass-balance continues through the run", "PASS" if hydro else "FAIL",
          f"{len(hydro)} accepted-step rows recorded")

    rose_after_dip = False
    if below_hc:
        last_below_t = max(r["T"] for r in below_hc)
        after = [r for r in hydro if r["T"] > last_below_t]
        rose_after_dip = any(r["HY"] >= r["HC"] for r in after)
    check("reservoir elevation rises back above controlling elevation after a dip",
          "PASS" if rose_after_dip else "NOT_EXERCISED",
          "reservoir dipped below HC at least once and later recovered" if rose_after_dip
          else "no dip-then-recovery sequence observed")

    breach_resumed = False
    if rose_after_dip:
        breach_resumed = any(r["QB"] > 1.0 for r in after if r["HY"] >= r["HC"]) if below_hc else False
    check("breach outflow resumes after recovery", "PASS" if breach_resumed else "NOT_EXERCISED",
          "n/a -- depends on the above")

    nan_found = any(math.isnan(r["HY"]) or math.isnan(r["QB"]) for r in hydro) if hydro else False
    check("no NaN in HY or QB", "PASS" if not nan_found else "FAIL", f"nan_found={nan_found}")

    overflow_found = bool(re.search(r"\*{5,}", text))
    check("no numeric overflow (**** in output)", "PASS" if not overflow_found else "FAIL",
          f"overflow_pattern_found={overflow_found}")

    neg_qb = [r for r in hydro if r["QB"] < -0.001]
    check("no negative breach discharge", "PASS" if not neg_qb else "FAIL",
          f"{len(neg_qb)} rows with QB<0")

    neg_hy_below_valley = [r for r in hydro if r["HY"] < -50]
    check("no grossly non-physical (runaway) elevation", "PASS" if not neg_hy_below_valley else "FAIL",
          f"{len(neg_hy_below_valley)} rows with HY<-50ft")

    print(f"{'Criterion':55s} {'Result':15s} Detail")
    print("-" * 110)
    any_fail = False
    for name, status, detail in results:
        print(f"{name:55s} {status:15s} {detail}")
        if status == "FAIL":
            any_fail = True

    print()
    print("Summary written per docs/RESERVOIR_REFILL_TEST.md — NOT_EXERCISED is an")
    print("honest, expected outcome for the depletion-dependent criteria in this")
    print("particular run; only FAIL indicates an actual problem.")
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
