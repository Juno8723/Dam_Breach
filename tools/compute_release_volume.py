#!/usr/bin/env python3
"""Adds a total-released-volume column (trapezoidal integral of breach
discharge QB over time, in acre-ft) to outputs/analysis/timestep_convergence.csv.

This script only PARSES already-saved stdout text files (produced by
tools/run_timestep_convergence.sh, which runs the actual FORTRAN binaries
via bash `timeout` -- repeated python subprocess.run() calls against the
compiled binaries were intermittently hanging in this environment after a
handful of invocations, so binary execution stays in bash and python here
only does text processing).
"""
import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "outputs", "analysis", "timestep_convergence.csv")
STDOUT_DIR = os.path.join(ROOT, "outputs", "analysis", "timestep_stdout")

sys.path.insert(0, os.path.join(ROOT, "tools"))
from parse_breach_output import parse  # noqa: E402

CFS_HR_TO_ACRE_FT = 3600.0 / 43560.0


def trapz_volume(hydrograph, key="QB"):
    if len(hydrograph) < 2:
        return 0.0
    vol = 0.0
    for a, b in zip(hydrograph, hydrograph[1:]):
        dt = b["T"] - a["T"]
        vol += 0.5 * (a[key] + b[key]) * dt
    return vol * CFS_HR_TO_ACRE_FT


def main():
    with open(CSV_PATH) as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        stdout_path = os.path.join(STDOUT_DIR, f"{row['sweep']}_{row['value']}_{row['dataset']}.stdout.txt")
        with open(stdout_path, errors="replace") as f:
            text = f.read()
        data = parse(text)
        vol = trapz_volume(data.get("hydrograph", []))
        row["released_volume_acreft"] = round(vol, 3)
        print(f"{row['sweep']:16s} {row['value']:8s} {row['dataset']:10s} released_volume={vol:.2f} acre-ft")

    fieldnames = list(rows[0].keys())
    with open(CSV_PATH, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print("updated", CSV_PATH)


if __name__ == "__main__":
    main()
