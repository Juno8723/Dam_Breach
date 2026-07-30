#!/usr/bin/env python3
"""Parse NWS BREACH (1999 / documented-corrections) stdout into structured JSON.

This is an independent parsing tool written for this project; it does not
modify or depend on RiverMechanics BRCH software in any way. It only reads
text that BREACH.for's own WRITE statements already produce on unit 6.
"""
import argparse
import json
import re
import sys

SUMMARY_FIELDS = [
    ("QBP", r"QBP\s+MAX OUTFLOW\(CFS\) THRU BREACH\s+([-\d.]+)"),
    ("TP", r"TP\s+TIME\(HR\) AT WHICH PEAK OUTFLOW OCCURS\s+([-\d.]+)"),
    ("QP", r"QP\s+MAX TOTAL OUTFLOW\(CFS\) OCCURRING AT TIME TP\s+([-\d.]+)"),
    ("TRS", r"TRS\s+DURATION\(HR\) OF RISING LIMB OF HYDROGRAPH\s+([-\d.]+)"),
    ("TB", r"TB\s+TIME\(HR\) AT WHICH SIGN\. RISE IN OUTFLOW STARTS\s+([-\d.]+)"),
    ("BRD", r"BRD\s+FINAL DEPTH\(FT\) OF BREACH\s+([-\d.]+)"),
    ("BRW", r"BRW\s+TOP WIDTH\(FT\) OF BREACH AT PEAK BREACH FLOW\s+([-\d.]+)"),
    ("HU", r"HU\s+ELEV\(FT\) OF TOP OF DAM\s+([-\d.]+)"),
    ("HY_final", r"HY\s+FINAL ELEV\(FT\) OF RESERVOIR WATER SURFACE\s+([-\d.]+)"),
    ("HC_final", r"HC\s+FINAL ELEV\(FT\) OF BOTTOM OF BREACH\s+([-\d.]+)"),
    ("AGL", r"AGL\s+ACUTE ANGLE.*AT QBP\s+([-\d.]+)"),
    ("QO", r"QO\s+OUTFLOW \(CFS\) AT T=0\.0\s+([-\d.]+)"),
    ("Z", r"Z\s+SIDE SLOPE.*AT PEAK BREACH FLOW\s+([-\d.]+)"),
    ("TFH", r"OBTAINED BY USING SIMPLIFIED DAM-BREAK DISCHARGE EQUATION\s+([-\d.]+)"),
    ("TFHI", r"OBTAINED BY INTEGRATING QB VS TIME FROM T=0 TO T=TP\s+([-\d.]+)"),
    ("BO_final", r"BO\s+BOTTOM WIDTH \(FT\) OF BREACH AT PEAK BREACH FLOW\s+([-\d.]+)"),
]

ROW_FIELDS = [
    "I", "T", "DTH", "KREG", "KCOL", "QTOT", "QTS", "QB", "SUB", "BT",
    "HY", "HC", "BC", "PPP", "HP", "TWD", "DH", "DHH", "KIT", "AGL",
]
NUMERIC_TOKEN = re.compile(r"^-?\d+\.?\d*$")


def _match_row(line: str):
    """Return a dict of ROW_FIELDS values if `line` is a detailed hydrograph
    row (format label 18 in Breach.for), else None. Uses whitespace
    tokenization rather than fixed columns: every field in format 18 is
    either single-digit-range (KREG in [-1..5], KCOL, KIT) or has generous
    padding relative to the physical value ranges in these examples, so
    each field is reliably separated by at least one blank."""
    tokens = line.split()
    if len(tokens) != len(ROW_FIELDS):
        return None
    if not all(NUMERIC_TOKEN.match(t) for t in tokens):
        return None
    if "." in tokens[0]:  # I must be a plain integer counter
        return None
    return dict(zip(ROW_FIELDS, tokens))


def parse(text: str) -> dict:
    result = {"completed": False, "summary": {}, "hydrograph": [], "kreg_transitions": []}

    for name, pattern in SUMMARY_FIELDS:
        m = re.search(pattern, text)
        if m:
            result["summary"][name] = float(m.group(1))

    if result["summary"]:
        result["completed"] = True

    prev_kreg = None
    for line in text.splitlines():
        raw = _match_row(line)
        if raw is None:
            continue
        row = {k: (int(v) if k in ("I", "KREG", "KCOL", "KIT") else float(v)) for k, v in raw.items()}
        result["hydrograph"].append(row)
        if row["KREG"] != prev_kreg:
            result["kreg_transitions"].append({"T": row["T"], "I": row["I"], "KREG": row["KREG"]})
            prev_kreg = row["KREG"]

    if result["hydrograph"]:
        result["reservoir_elevation_hydrograph"] = [(r["T"], r["HY"]) for r in result["hydrograph"]]
        result["tailwater_elevation_hydrograph"] = [(r["T"], r["TWD"]) for r in result["hydrograph"]]
        result["breach_outflow_hydrograph"] = [(r["T"], r["QB"]) for r in result["hydrograph"]]
        result["spillway_outflow_hydrograph"] = [(r["T"], r["QTS"]) for r in result["hydrograph"]]
        result["total_outflow_hydrograph"] = [(r["T"], r["QTOT"]) for r in result["hydrograph"]]

    result["runtime_warnings"] = [
        line.strip() for line in text.splitlines()
        if "WARNING" in line.upper() or "DID NOT CONVERGE" in line.upper()
    ]

    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("infile", help="BREACH stdout capture to parse")
    ap.add_argument("-o", "--out", help="write JSON here instead of stdout")
    ap.add_argument("--no-hydrograph", action="store_true",
                    help="omit the full per-step hydrograph arrays (summary + transitions only)")
    args = ap.parse_args()

    with open(args.infile, "r", errors="replace") as f:
        text = f.read()

    result = parse(text)
    if args.no_hydrograph:
        for key in ("hydrograph", "reservoir_elevation_hydrograph", "tailwater_elevation_hydrograph",
                    "breach_outflow_hydrograph", "spillway_outflow_hydrograph", "total_outflow_hydrograph"):
            result.pop(key, None)

    out = json.dumps(result, indent=2)
    if args.out:
        with open(args.out, "w") as f:
            f.write(out)
    else:
        print(out)


if __name__ == "__main__":
    sys.exit(main())
