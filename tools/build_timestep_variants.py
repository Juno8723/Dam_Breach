#!/usr/bin/env python3
"""Generates DTH-floor (and optionally DTHFIL-ceiling) sensitivity variants
from src/breach1999_documented_corrections.f (the actual corrected source),
by substituting the numeric bound in the already-applied BRCH2018-05 guard.
The adaptive time-step LOGIC is left completely untouched -- only the
minimum-DTH / maximum-DTHFIL bound itself changes, per docs/TIMESTEP_CONVERGENCE.md.

Usage: build_timestep_variants.py
Writes tests/attribution/timestep_variants/dth_<value>.f for each DTH floor
in DTH_MIN_VALUES, and dthfil_<value>.f for each DTHFIL ceiling in
DTHFIL_MAX_VALUES (using the corrected build's default DTH floor of 1e-4).
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORRECTED = os.path.join(ROOT, "src", "breach1999_documented_corrections.f")
OUTDIR = os.path.join(ROOT, "tests", "attribution", "timestep_variants")

DTH_MIN_VALUES = ["1.0e-3", "5.0e-4", "1.0e-4", "5.0e-5", "1.0e-5"]
DTHFIL_MAX_VALUES = ["1.0", "0.5", "0.25", "0.1"]

DTH_OLD = "      IF(DTH.LT.0.0001) DTH=0.0001\n   22 T=T+DTH"
DTHFIL_OLD = "      IF(KSTDY.EQ.1) DTHFIL=0.5\n      IF(DTHFIL.GT.0.5) DTHFIL=0.5"


def main():
    with open(CORRECTED) as f:
        base = f.read()
    assert base.count(DTH_OLD) == 1, "DTH floor pattern not found / not unique"
    assert base.count(DTHFIL_OLD) == 1, "DTHFIL ceiling pattern not found / not unique"

    os.makedirs(OUTDIR, exist_ok=True)

    for val in DTH_MIN_VALUES:
        text = base.replace(
            DTH_OLD,
            f"      IF(DTH.LT.{val}) DTH={val}\n   22 T=T+DTH",
        )
        tag = val.replace(".", "p").replace("-", "m").replace("+", "")
        out_path = os.path.join(OUTDIR, f"dth_{tag}.f")
        with open(out_path, "w") as f:
            f.write(text)
        print("wrote", out_path)

    for val in DTHFIL_MAX_VALUES:
        text = base.replace(
            DTHFIL_OLD,
            f"      IF(KSTDY.EQ.1) DTHFIL={val}\n      IF(DTHFIL.GT.{val}) DTHFIL={val}",
        )
        tag = val.replace(".", "p")
        out_path = os.path.join(OUTDIR, f"dthfil_{tag}.f")
        with open(out_path, "w") as f:
            f.write(text)
        print("wrote", out_path)


if __name__ == "__main__":
    sys.exit(main())
