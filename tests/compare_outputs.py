#!/usr/bin/env python3
"""Numeric comparison of two BREACH output-set directories (each produced by
tests/run_all_examples.sh), using parsed JSON rather than raw text diff.

Usage: compare_outputs.py <dir_a> <dir_b> [--tol 0.5]

Tolerance default (0.5% relative, see docs/VALIDATION_REPORT.md for why):
BREACH.for computes exclusively in single-precision REAL, and several
quantities (QBP, QP, BRW, ...) are themselves derived from a bisection/
convergence loop with its own ERR-driven tolerance (default ERR=0.5%,
i.e. the DTH convergence check `ABS(DH-DHH)/DHH*100 < ERR`). A tolerance
tighter than the model's own internal convergence criterion would flag
noise as a regression.
"""
import argparse
import glob
import json
import os
import sys

SUMMARY_KEYS = [
    "QBP", "TP", "QP", "TRS", "TB", "BRD", "BRW", "HU", "HY_final",
    "HC_final", "AGL", "QO", "Z", "TFH", "TFHI", "BO_final",
]


def rel_diff(a, b):
    if a == b:
        return 0.0
    denom = max(abs(a), abs(b), 1e-9)
    return abs(a - b) / denom * 100.0


def compare_case(name, a, b, tol):
    diffs = []
    if a.get("completed") != b.get("completed"):
        diffs.append(f"completed: {a.get('completed')} -> {b.get('completed')}")
    for key in SUMMARY_KEYS:
        av = a.get("summary", {}).get(key)
        bv = b.get("summary", {}).get(key)
        if av is None and bv is None:
            continue
        if av is None or bv is None:
            diffs.append(f"{key}: {av} -> {bv} (missing in one run)")
            continue
        d = rel_diff(av, bv)
        if d > tol:
            diffs.append(f"{key}: {av} -> {bv} ({d:.2f}% > {tol}% tol)")
    a_trans = [t["KREG"] for t in a.get("kreg_transitions", [])]
    b_trans = [t["KREG"] for t in b.get("kreg_transitions", [])]
    if a_trans != b_trans:
        diffs.append(f"KREG transition sequence: {a_trans} -> {b_trans}")
    return diffs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir_a")
    ap.add_argument("dir_b")
    ap.add_argument("--tol", type=float, default=0.5, help="relative %% tolerance (default 0.5)")
    args = ap.parse_args()

    cases = sorted(
        os.path.basename(p)[:-len(".parsed.json")]
        for p in glob.glob(os.path.join(args.dir_a, "*.parsed.json"))
    )
    if not cases:
        print(f"no *.parsed.json files found in {args.dir_a}", file=sys.stderr)
        return 1

    any_diff = False
    for name in cases:
        pa = os.path.join(args.dir_a, f"{name}.parsed.json")
        pb = os.path.join(args.dir_b, f"{name}.parsed.json")
        if not os.path.exists(pb):
            print(f"{name}: MISSING in {args.dir_b}")
            any_diff = True
            continue
        with open(pa) as f:
            a = json.load(f)
        with open(pb) as f:
            b = json.load(f)
        diffs = compare_case(name, a, b, args.tol)
        if diffs:
            any_diff = True
            print(f"{name}: CHANGED")
            for d in diffs:
                print(f"    {d}")
        else:
            print(f"{name}: no change (within {args.tol}% tolerance)")

    return 1 if any_diff else 0


if __name__ == "__main__":
    sys.exit(main())
