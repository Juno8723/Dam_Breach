#!/usr/bin/env python3
"""Runs each DTH-floor / DTHFIL-ceiling variant binary (built by
tools/build_timestep_variants.py + compiled into bin/timestep_variants/)
against a fixed set of example datasets, measures wall-clock runtime and
key outputs, and writes outputs/analysis/timestep_convergence.csv.

negative_bmx.dat is intentionally excluded -- it is a stability test, not
a convergence test (see docs/TIMESTEP_CONVERGENCE.md).
"""
import csv
import json
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(ROOT, "bin", "timestep_variants")
EXAMPLES_DIR = os.path.join(ROOT, "examples")
PARSER = os.path.join(ROOT, "tools", "parse_breach_output.py")
OUT_CSV = os.path.join(ROOT, "outputs", "analysis", "timestep_convergence.csv")

DATASETS = ["BSMBOT2", "TETON", "CLAY"]

VARIANTS = [
    ("dth_1p0em3", "dth_floor", 1.0e-3),
    ("dth_5p0em4", "dth_floor", 5.0e-4),
    ("dth_1p0em4", "dth_floor", 1.0e-4),
    ("dth_5p0em5", "dth_floor", 5.0e-5),
    ("dth_1p0em5", "dth_floor", 1.0e-5),
    ("dthfil_1p0", "dthfil_ceiling", 1.0),
    ("dthfil_0p5", "dthfil_ceiling", 0.5),
    ("dthfil_0p25", "dthfil_ceiling", 0.25),
    ("dthfil_0p1", "dthfil_ceiling", 0.1),
]

METRICS = ["QBP", "QP", "TP", "HY_final", "BO_final", "BRD", "TFH", "TFHI"]


def run_one(binary, dat_path):
    d = tempfile.mkdtemp()
    with open(dat_path, "rb") as s, open(os.path.join(d, "in.dat"), "wb") as o:
        o.write(s.read())
    t0 = time.perf_counter()
    proc = subprocess.run([binary], cwd=d, capture_output=True, timeout=120)
    elapsed = time.perf_counter() - t0
    stdout_path = os.path.join(d, "stdout.txt")
    with open(stdout_path, "wb") as f:
        f.write(proc.stdout)
    parsed = subprocess.run(
        [sys.executable, PARSER, stdout_path, "--no-hydrograph"],
        capture_output=True, text=True,
    )
    n_steps = proc.stdout.count(b"\n")
    try:
        data = json.loads(parsed.stdout)
    except json.JSONDecodeError:
        data = {"completed": False, "summary": {}}
    return elapsed, proc.returncode, data, n_steps


def main():
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    rows = []
    for tag, sweep, value in VARIANTS:
        binary = os.path.join(BIN_DIR, tag)
        for ds in DATASETS:
            dat_path = os.path.join(EXAMPLES_DIR, f"{ds}.DAT")
            elapsed, code, data, n_lines = run_one(binary, dat_path)
            row = {
                "sweep": sweep,
                "value": value,
                "dataset": ds,
                "exit_code": code,
                "completed": data.get("completed", False),
                "runtime_sec": round(elapsed, 4),
                "stdout_lines": n_lines,
            }
            for m in METRICS:
                row[m] = data.get("summary", {}).get(m)
            rows.append(row)
            print(f"{tag:14s} {ds:10s} exit={code} QBP={row.get('QBP')} "
                  f"HY_final={row.get('HY_final')} t={elapsed:.2f}s")

    fieldnames = ["sweep", "value", "dataset", "exit_code", "completed",
                  "runtime_sec", "stdout_lines"] + METRICS
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print("wrote", OUT_CSV)


if __name__ == "__main__":
    main()
