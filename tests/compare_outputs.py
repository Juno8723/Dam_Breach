#!/usr/bin/env python3
"""Numeric comparison of two BREACH output-set directories (each produced by
tests/run_all_examples.sh), using parsed JSON rather than raw text diff.

Usage:
  compare_outputs.py <dir_a> <dir_b>                 # variable-specific tolerances (default, recommended)
  compare_outputs.py <dir_a> <dir_b> --tol 0.5        # legacy flat-percent mode (backward compatible)

Variable-specific tolerance categories (see docs/VALIDATION_REPORT.md for
the full rationale):

  continuous  (QBP, QP, BRD, BRW, BO_final): relative 0.5% OR absolute
              floor, whichever is looser -- catches near-zero values a
              pure percent check would flag on noise alone.
  elevation   (HY_final, HC_final, HU): absolute 0.1 ft primarily (these
              are differences of large numbers -- percent is a poor
              signal here), plus a loose 1% relative backstop for large
              swings.
  time        (TP, TB, TRS, TFH, TFHI): absolute 0.05 hr (~3 minutes) --
              tighter than this exceeds what a DTH-scale simulation can
              resolve; see docs/TIMESTEP_CONVERGENCE.md.
  near_zero   (AGL, QO, Z): absolute only (0.05) -- these can legitimately
              be ~0, where relative error is undefined/meaningless.
  state       (KREG transition sequence): EXACT match required, no
              tolerance -- a state-machine sequence has no notion of
              "close enough".

BREACH.for computes exclusively in single-precision REAL, and several
quantities (QBP, QP, BRW, ...) are themselves derived from a bisection/
convergence loop with its own ERR-driven tolerance (default ERR=0.5%,
i.e. the DTH convergence check `ABS(DH-DHH)/DHH*100 < ERR`) -- the
`continuous` category's 0.5% floor matches this, so it doesn't flag the
model's own internal convergence noise as a regression.

Recommended starting point for a future Python port's regression tests:
tighten `continuous`/`elevation` to bit-for-bit or ~1e-6 relative once the
port uses the same (or higher) precision as this Fortran build, since a
faithful port shouldn't reintroduce single-precision-only noise; keep
`time`/`state` as exact/near-exact since those aren't precision-dependent.
"""
import argparse
import glob
import json
import os
import sys

TOLERANCE_CATEGORIES = {
    "QBP": ("continuous", 1.0),
    "QP": ("continuous", 1.0),
    "BRD": ("continuous", 0.1),
    "BRW": ("continuous", 0.1),
    "BO_final": ("continuous", 0.1),
    "HY_final": ("elevation", 0.1),
    "HC_final": ("elevation", 0.1),
    "HU": ("elevation", 0.1),
    "TP": ("time", 0.05),
    "TB": ("time", 0.05),
    "TRS": ("time", 0.05),
    "TFH": ("time", 0.05),
    "TFHI": ("time", 0.05),
    "AGL": ("near_zero", 0.05),
    "QO": ("near_zero", 0.05),
    "Z": ("near_zero", 0.05),
}
SUMMARY_KEYS = list(TOLERANCE_CATEGORIES.keys())

REL_PCT = {"continuous": 0.5, "elevation": 1.0}  # relative %% backstop, where applicable


def rel_diff_pct(a, b):
    if a == b:
        return 0.0
    denom = max(abs(a), abs(b), 1e-9)
    return abs(a - b) / denom * 100.0


def within_tolerance(key, av, bv):
    category, abs_tol = TOLERANCE_CATEGORIES[key]
    abs_d = abs(av - bv)
    if abs_d <= abs_tol:
        return True, abs_d, None
    if category in REL_PCT:
        rel_d = rel_diff_pct(av, bv)
        if rel_d <= REL_PCT[category]:
            return True, abs_d, rel_d
        return False, abs_d, rel_d
    return False, abs_d, None


def compare_case_categorized(a, b):
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
        ok, abs_d, rel_d = within_tolerance(key, av, bv)
        if not ok:
            category, abs_tol = TOLERANCE_CATEGORIES[key]
            rel_txt = f", {rel_d:.2f}% rel" if rel_d is not None else ""
            diffs.append(
                f"{key} [{category}]: {av} -> {bv} (abs diff {abs_d:.4g} > {abs_tol}{rel_txt})"
            )
    a_trans = [t["KREG"] for t in a.get("kreg_transitions", [])]
    b_trans = [t["KREG"] for t in b.get("kreg_transitions", [])]
    if a_trans != b_trans:
        diffs.append(f"KREG transition sequence [state, exact match required]: {a_trans} -> {b_trans}")
    return diffs


def compare_case_legacy(a, b, tol):
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
        d = rel_diff_pct(av, bv)
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
    ap.add_argument("--tol", type=float, default=None,
                     help="legacy flat relative %% tolerance mode (pre-variable-specific-tolerance "
                          "behavior); omit to use the recommended per-variable-category tolerances")
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
        if args.tol is not None:
            diffs = compare_case_legacy(a, b, args.tol)
            mode_txt = f"within {args.tol}% tolerance (legacy flat mode)"
        else:
            diffs = compare_case_categorized(a, b)
            mode_txt = "within variable-specific tolerances"
        if diffs:
            any_diff = True
            print(f"{name}: CHANGED")
            for d in diffs:
                print(f"    {d}")
        else:
            print(f"{name}: no change ({mode_txt})")

    return 1 if any_diff else 0


if __name__ == "__main__":
    sys.exit(main())
