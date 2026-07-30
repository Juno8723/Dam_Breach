#!/usr/bin/env python3
"""Plots outputs/analysis/timestep_convergence.csv into 4 PNGs under
outputs/analysis/. Only plots the dth_floor sweep (the DTHFIL ceiling
sweep only affects BSMBOT2 and only 4 points -- shown in the same axes
where informative, otherwise noted in TIMESTEP_CONVERGENCE.md text)."""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "outputs", "analysis", "timestep_convergence.csv")
OUT_DIR = os.path.join(ROOT, "outputs", "analysis")

DATASETS = ["BSMBOT2", "TETON", "CLAY"]
COLORS = {"BSMBOT2": "tab:green", "TETON": "tab:blue", "CLAY": "tab:orange"}


def load():
    with open(CSV_PATH) as f:
        return list(csv.DictReader(f))


def plot_dth_sweep(rows, key, ylabel, title, fname, log_y=False):
    plt.figure(figsize=(8, 5))
    for ds in DATASETS:
        sub = [r for r in rows if r["sweep"] == "dth_floor" and r["dataset"] == ds]
        sub.sort(key=lambda r: float(r["value"]))
        x = [float(r["value"]) for r in sub]
        y = [float(r[key]) for r in sub]
        plt.plot(x, y, "o-", label=ds, color=COLORS[ds])
    plt.xscale("log")
    if log_y:
        plt.yscale("log")
    plt.gca().invert_xaxis()
    plt.xlabel("DTH floor (hr, log scale, finer -->")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3, which="both")
    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, fname)
    plt.savefig(out_path, dpi=120)
    plt.close()
    print("wrote", out_path)


def main():
    rows = load()
    plot_dth_sweep(rows, "QBP", "Peak breach discharge QBP (cfs)",
                    "DTH-floor sensitivity: peak discharge",
                    "timestep_qpeak.png")
    plot_dth_sweep(rows, "HY_final", "Final reservoir elevation (ft)",
                    "DTH-floor sensitivity: final pool elevation",
                    "timestep_final_pool.png")
    plot_dth_sweep(rows, "released_volume_acreft", "Total released volume (acre-ft)",
                    "DTH-floor sensitivity: released volume",
                    "timestep_release_volume.png")
    plot_dth_sweep(rows, "runtime_sec", "Runtime (sec)",
                    "DTH-floor sensitivity: runtime",
                    "timestep_runtime.png")


if __name__ == "__main__":
    main()
