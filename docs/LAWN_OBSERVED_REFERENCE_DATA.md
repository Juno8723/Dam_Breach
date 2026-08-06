# LAWN_OBSERVED_REFERENCE_DATA.md

**Purpose and scope.** This document collects externally sourced, official
observational data on the actual **July 15, 1982 Lawn Lake Dam failure**
(Rocky Mountain National Park, Larimer County, Colorado), which this project's
`examples/LAWN.DAT` / `original/Input/LAWN.DAT` dataset represents (title line:
`LAWN LAKE`). **No comparison to this project's model output is made in this
document** — that is in `docs/LAWN_MODEL_OBSERVATION_COMPARABILITY.md`. **No
code or input file in this repository was modified to produce this document.**

**Source used (single primary source, read in full-text search):**

Jarrett, R.D., and Costa, J.E., *Hydrology, Geomorphology, and Dam-Break
Modeling of the July 15, 1982, Lawn Lake Dam and Cascade Lake Dam Failures,
Larimer County, Colorado*, U.S. Geological Survey Open-File Report 84-612
(prepared in cooperation with the Colorado Department of Natural Resources,
Division of Water Resources, Office of the State Engineer). Retrieved directly
as a PDF from the USGS Publications Warehouse:
`https://pubs.usgs.gov/of/1984/0612/report.pdf` (119 pages). This is a USGS
official report — priority-2 source per task instructions. No blog, dam-safety
summary page, or Wikipedia article was used for any numeric value below.

---

## 1. Estimated peak breach outflow

| Field | Value |
|---|---|
| Value | **18,000 ft³/s**, "from Lawn Lake dam" |
| Single value or range | Single value |
| Observed or post-hoc estimate | **Post-hoc estimate — specifically a dam-break *model* result, not a field measurement.** The report states indirect (field) peak-discharge measurements "could not be made upstream from Site 1" due to extensive scour, and Figure 11's own legend labels the near-dam data point as "MODEL RESULT" (as opposed to "INDIRECT PEAK DISCHARGE MEASUREMENT" for downstream sites). The model used was USGS's own dam-break/hydrologic routing model (not this project's BREACH model) |
| Exact definition and reference point | Peak discharge **at the dam itself** (distance = 0 on the report's downstream peak-discharge profile, Figure 11) |
| Source | p. 1 (Abstract): *"an estimated peak discharge of 18,000 cubic feet per second down the Roaring River valley"*; p. 11: *"Calculated peak discharges for the flood were 18,000 cubic feet per second from Lawn Lake dam..."*; p. 33, Figure 11 and caption: *"Indirect measurements are believed to be more accurate than dam-break model results."* |

---

## 2. Breach formation time

| Field | Value |
|---|---|
| Value | **~10 minutes** |
| Single value or range | Single value (stated twice, independently, in two different sections of the same report — see below) |
| Observed or post-hoc estimate | **Mixed.** First occurrence (p. 12) is framed as an observation/estimate from witness testimony ("the resulting outflow of water reached its peak discharge very quickly, estimated to be within 10 min"). Second occurrence (p. 33) is explicitly a **modeling input assumption**: *"The duration of breach development, based on available data and judgment, was 10 min for Lawn Lake dam."* |
| Exact definition and reference point | p. 12: time from "complete failure of the dam embankment at about 0530 MDT" to reaching peak discharge. p. 33: "duration of breach development... erosion of the embankment to full breach width" — i.e., time for the breach opening itself to reach final size, not necessarily identical in definition to the first figure, though the report treats them as consistent |
| Source | p. 12: *"Following the complete failure of the dam embankment at about 0530 MDT, the resulting outflow of water reached its peak discharge very quickly (estimated to be within 10 min)."*; p. 33: *"...it was felt that the erosion of the embankment to full breach width took about 10 min."* |
| Related timing context (not itself "breach formation time," included for completeness) | Piping/leakage may have been occurring "for at least 3 to 4 hours" before the final catastrophic enlargement at ~0530 MDT (p. 12) |

---

## 3. Observed final breach top width

| Field | Value |
|---|---|
| Value | **97 ft** |
| Single value or range | Single value |
| Observed or post-hoc estimate | **Observed** — explicitly a post-failure field survey: *"Surveyed breach dimensions are: Depth of 28 ft, top width of 97 ft, and bottom width of 55 ft."* |
| Exact definition and reference point | Final, post-failure surveyed breach opening in the embankment, at the dam |
| Source | p. 12 |

---

## 4. Observed final breach bottom width

| Field | Value |
|---|---|
| Value | **55 ft** |
| Single value or range | Single value |
| Observed or post-hoc estimate | Observed (same survey as §3). **Independently corroborated a second time** in a different section of the same report, in the context of the dam-break model's calibration: *"bottom breach width at end of failure (Lawn Lake dam = 55 ft...)"* (p. 33), and Table 10/11 headings referring to "the actual breach width of 55 feet" |
| Exact definition and reference point | Same as §3 |
| Source | p. 12; corroborated p. 33 and Table 10/11 headings (p. 75–76, not read in detail — table content not needed since the value itself is already stated in the body text) |

---

## 5. Observed breach depth

| Field | Value |
|---|---|
| Value | **28 ft** |
| Single value or range | Single value |
| Observed or post-hoc estimate | Observed (same survey as §3) |
| Exact definition and reference point | Final, post-failure surveyed vertical extent of the breach opening |
| Source | p. 12: *"Surveyed breach dimensions are: Depth of 28 ft..."* |

---

## 6. Initial and final reservoir water level / drawdown

| Field | Value |
|---|---|
| **Initial value** | **10,996.42 ft** (approximate mean sea level datum) |
| Single value or range | Single value |
| Observed or post-hoc estimate | Observed — reservoir water-surface elevation at the time of failure, per Table 3 footnote and cross-section survey data |
| Exact definition and reference point | Water-surface elevation of Lawn Lake at the moment of dam failure, July 15, 1982 |
| Source | Table 3, footnote a: *"Approximate mean sea level; water-surface elevation at failure was 10,996.42 feet."*; also p. 40 (Dam-Break Modeling section): *"The initial water-surface elevation for Lawn Lake dam was 10,996.41 ft"* (0.01 ft lower, used deliberately as a piping-failure modeling convention, per that section's own text) |

| Field | Value |
|---|---|
| **Final (residual) value** | **10,975.69 ft** |
| Single value or range | Single value |
| Observed or post-hoc estimate | Observed — a field survey of the *remaining* lake, **taken July 21, 1982 (6 days after the failure)**, not immediately after |
| Exact definition and reference point | Water surface of the residual lake that remained after the breach (the report notes "a substantial amount of water remained as dead capacity, and almost corresponding to the original moraine-dammed mountain lake" — i.e., Lawn Lake did not drain to empty; a natural lake below the outlet-pipe/breach-bottom elevation persisted). Surveyed "85 feet upstream of dam." A closely matching natural lakebed elevation of 10,974.7 ft is given as a nearby "control" point |
| Source | Supplemental cross-section data, Lawn Lake elevation survey dated July 21, 1982: *"Water surface, 10,975.69 feet"* |

**Drawdown** (computed here only as a direct difference of the two directly
quoted numbers above — not an invented or estimated figure):

`10,996.42 ft − 10,975.69 ft = 20.73 ft`

This 20.73 ft figure describes the drop from the at-failure water level to the
**6-days-later residual/dead-storage lake level** — it is *not* the drop to a
fully empty reservoir (674 acre-ft was released, but "a substantial amount of
water remained," per p. 23).

---

## Cross-checks supporting that `LAWN.DAT` represents this specific event

Not one of the 5 requested items, but recorded here because it affects how the
comparison in `docs/LAWN_MODEL_OBSERVATION_COMPARABILITY.md` should be read:

- Report: dam was "26-foot-high" (abstract, p. 1) / "the dam was 26 ft high
  (water was 24 ft deep)" (p. 8, postfailure survey). `LAWN.DAT` line 1:
  `HI=26, HU=28, HL=0, HPI=2` — i.e., the input's initial-water-to-crest
  freeboard (`HU−HI=2 ft`) matches the report's 26 ft dam / 24 ft water figures
  in relative terms, though the input's absolute crest value (`HU=28`) is 2 ft
  above the report's "26 ft high" figure — not an exact 1:1 digitization.
- Report: the outlet pipe/piping path was very close to the base of the dam
  (breach eroded down to essentially the lakebed elevation, per the "breach
  crest elevation [i.e., final breach bottom] = 10,975 ft" figure used in the
  USGS model, versus a lakebed around 10,974.7–10,975.69 ft). `LAWN.DAT`'s
  `HPI=2` (pipe elevation only 2 ft above the local `HL=0` base) is
  qualitatively consistent with this.

These are noted as **qualitative** consistency checks only — no claim is made
that `LAWN.DAT` is an exact digitization of the report's surveyed geometry.
