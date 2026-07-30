#!/usr/bin/env python3
"""Plots the BSMBOT2 fix-attribution time series (configs A/B/C/D) from
outputs/analysis/bsmbot2_attribution/*.parsed.json into outputs/analysis/*.png.

Run tools/build_attribution_variants.py + compile + run each config first
(see docs/BSMBOT2_FIX_ATTRIBUTION.md for the exact commands); this script
only plots already-parsed JSON, it doesn't run BREACH itself.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATTR_DIR = os.path.join(ROOT, "outputs", "analysis", "bsmbot2_attribution")
OUT_DIR = os.path.join(ROOT, "outputs", "analysis")

CONFIGS = [
    ("A_original", "A: Original (no fixes)", "tab:red"),
    ("B_tailwater_only", "B: Tailwater fix only", "tab:orange"),
    ("C_timestep_only", "C: Time-step fix only", "tab:blue"),
    ("D_both", "D: Corrected (both)", "tab:green"),
]


def load(name):
    with open(os.path.join(ATTR_DIR, f"{name}.parsed.json")) as f:
        return json.load(f)


def series(data, key):
    rows = data.get("hydrograph", [])
    return [r["T"] for r in rows], [r[key] for r in rows]


def plot_metric(key, ylabel, title, fname):
    plt.figure(figsize=(9, 5.5))
    for name, label, color in CONFIGS:
        data = load(name)
        t, y = series(data, key)
        plt.plot(t, y, label=label, color=color, linewidth=1.5)
    plt.xlabel("Time (hr)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, fname)
    plt.savefig(out_path, dpi=120)
    plt.close()
    print("wrote", out_path)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    plot_metric("HY", "Reservoir elevation (ft)",
                "BSMBOT2: reservoir elevation by configuration",
                "bsmbot2_reservoir_elevation.png")
    plot_metric("QB", "Breach discharge (cfs)",
                "BSMBOT2: breach discharge by configuration",
                "bsmbot2_breach_discharge.png")
    plot_metric("QTS", "Spillway discharge (cfs)",
                "BSMBOT2: spillway discharge by configuration",
                "bsmbot2_spillway_discharge.png")
    plot_metric("DTH", "Time step DTH (hr)",
                "BSMBOT2: adaptive time step by configuration",
                "bsmbot2_timestep.png")


if __name__ == "__main__":
    main()
