# TETON_MODEL_OBSERVATION_COMPARABILITY.md

**Purpose.** Classify, item by item, whether this project's TETON model output and the
externally sourced observed/reported data in `docs/TETON_OBSERVED_REFERENCE_DATA.md`
are actually comparable — *before* computing any error metric. **No code or input
file was modified to produce this document** (`git status` confirmed clean except
for this new file). Model values are taken from the existing, already-committed
`outputs/corrected/TETON.stdout.txt` / `outputs/corrected/TETON.parsed.json` — no
new model run was performed, no baseline was regenerated.

**Classification legend**

- `DIRECTLY_COMPARABLE`: definition, location, and reference point are the same or
  sufficiently equivalent — a difference/relative-error can be computed.
- `CONDITIONALLY_COMPARABLE`: a calibration or an explicit, stated assumption would
  be required to align definition/location/reference point; that assumption is
  **not** invented here (per task instruction), so no number is computed — the
  specific missing assumption is named instead.
- `NOT_COMPARABLE`: location, definition, or reference point differ in a way that
  cannot be reconciled by a single stated assumption, **or** no observed value
  exists at all.

---

## 0. Why the model's internal clock (`T`) needs checking first

The model's `T` is set to `T=0.0` at MAIN's initialization
(`src/breach1999_documented_corrections.f:259`), immediately after reading
`examples/TETON.DAT`. Nothing in the source code or in this input file ties that
`T=0` instant to a specific real-world clock time. For `TETON.DAT` specifically:

- Line 1 of the input (`HI,HU,HL,HPI,...`) gives `HPI=160` (initial pipe/orifice
  centerline elevation, in the model's own 0–262 ft local datum where `HU=262`
  ft is the dam crest). Since `HPI>0.0001`, the code sets `KPIP=1`
  (`src/breach1999_documented_corrections.f:244`) — **piping mode**, meaning the
  simulation begins with a pipe *already present* at that elevation, not with an
  intact dam. `T=0` is therefore the instant the input file's author chose to
  represent "piping already underway," not the instant of first observable
  seepage, not crest collapse, and not full breach.
- No file in this repository (`docs/`, `examples/`, `original/Input/TETON.DAT`,
  its checksum-only entry in `docs/SOURCE_AUDIT.md`) states which real clock time
  on June 5, 1976 this `T=0` / `HPI=160` condition is meant to represent.
- The input's own `QIN`/`TIN` inflow table (`TIN` up to 1200 — units hours per the
  source's `C T TIME,HR` convention) is a separate, low-magnitude baseflow table
  (`QIN` = 0–85 cfs) used only to interpolate background inflow during the
  simulation; its large `TIN` values do not establish a real-world epoch for `T=0`
  either — it is consistent with a generic/simplified demonstration dataset, not a
  literal digitization of the 1976 reservoir-filling record (whose actual
  discharges, per `docs/TETON_OBSERVED_REFERENCE_DATA.md` §2 sourcing, were in the
  hundreds of cfs, not 0–85 cfs).

**Conclusion of this check: the model's `T=0` for this input file cannot be mapped
to a specific point in the observed 11:55 a.m./11:57 a.m. chronology without
inventing an assumption that is not documented anywhere in this repository or in
`TETON.DAT` itself.** This finding drives the classifications for "time to peak"
and "breach formation time" below.

---

## Comparison table

| Item | Model value (source) | Observed value (source) | Classification | Rationale |
|---|---|---|---|---|
| **Peak discharge** | `QBP = 2,152,248 cfs`, defined at the breach itself (`outputs/corrected/TETON.stdout.txt:845`, label "MAX OUTFLOW(CFS) THRU BREACH") | `65,000 m³/s ≈ 2.3×10⁶ cfs`, measured **~4 km (2.5 mi) downstream** of the dam (`docs/TETON_OBSERVED_REFERENCE_DATA.md` §1, Scott 1977 citing Ray & Kjelstrom 1977); a second point, `~1×10⁶ cfs` at ~13 km, is even farther downstream | **NOT_COMPARABLE** | Per task instruction, no error rate is computed. The model quantity is discharge **at the breach face**; both observed figures are **downstream channel** discharges, which are expected to differ from the breach-face peak due to valley/channel storage, translation, and attenuation over 2.5–8 mi of canyon — an effect neither this project nor the cited sources quantify. No observed value **at the breach itself** exists in `docs/TETON_OBSERVED_REFERENCE_DATA.md`. |
| **Time to peak** | `TP = 2.21 hr` after the model's `T=0` (`outputs/corrected/TETON.stdout.txt:846`) | Peak flow arrival at the Teton Canyon gauge (4 km downstream): **12:05 p.m.**, June 5, 1976 (`docs/TETON_OBSERVED_REFERENCE_DATA.md` §2, citing arXiv:2206.00766 Table 2, itself citing "Reclamation, 1976; USGS, 1976") | **NOT_COMPARABLE** | Two independent, unresolved gaps compound here, not one: (a) the same location mismatch as peak discharge (4 km downstream vs. the breach node), **and** (b) the §0 finding that the model's `T=0` cannot be mapped to a real clock time. Reconciling this would require at least two separate invented assumptions (a real-time anchor for `T=0`, and a translation/attenuation model between the breach and the 4 km gauge) — outside what a single stated calibration assumption can cover, and instruction 5 prohibits inventing either. |
| **Breach formation time** | Model reports two internal estimates, both explicitly "TIME OF FAILURE...LINEAR EQUIVALENT OF TRS": `TFH = 2.07 hr` (simplified dam-break equation method) and `TFHI = 0.75 hr` (integrated Q_b method); also `TB = 0.00 hr` ("time at which sign. rise in outflow starts") and `TRS = 2.21 hr` (rising-limb duration) — all measured from the model's `T=0` (`outputs/corrected/TETON.stdout.txt:848-861`) | Multiple duration definitions, all anchored at real clock times **at the dam** (no downstream-location issue here): crest-collapse→breach = 2 min (11:55→11:57 a.m.); whirlpool-first-seen→breach ≈ 57 min (11:00→11:57 a.m.); first-observed-seepage→breach = 5 hr (stated directly, 7:00 a.m.→11:57 a.m.); last-no-visible-leakage→breach = 15 hr (9:00 p.m. June 4→11:57 a.m. June 5) (`docs/TETON_OBSERVED_REFERENCE_DATA.md` §3) | **CONDITIONALLY_COMPARABLE** | Both sides describe an "at the dam" duration, so there is no location mismatch here (unlike the two rows above). But comparison requires **choosing which observed duration definition corresponds to the model's `T=0`→`TFH`/`TFHI` interval**, and that choice is exactly the undocumented assumption identified in §0 — e.g., is the model's `T=0` (pipe already present at `HPI=160`) closer in concept to "first observed seepage" (→5 hr candidate) or to "whirlpool first seen" (→57 min candidate)? Nothing in this repository states which, so **no such assumption is made here**, and no number is computed, per instruction 5. |
| **Breach top width** | `BRW = 608.35 ft`, defined as "TOP WIDTH(FT) OF BREACH AT PEAK BREACH FLOW" (`outputs/corrected/TETON.stdout.txt:850`) | Not found (`docs/TETON_OBSERVED_REFERENCE_DATA.md` §4) | **NOT_COMPARABLE** | No observed value exists to compare against, regardless of definition/location questions. |
| **Breach bottom width** | `BO_final = 81.04 ft`, defined as "BOTTOM WIDTH (FT) OF BREACH AT PEAK BREACH FLOW" (`outputs/corrected/TETON.stdout.txt:861`) | Not found; the one nearby number in the literature (an arXiv paper's own HEC-RAS calibration value of 55 m) is deliberately excluded in `docs/TETON_OBSERVED_REFERENCE_DATA.md` §5 as a model-fit parameter, not a cited historical measurement | **NOT_COMPARABLE** | No genuine observed value exists to compare against. |
| **Breach depth** | `BRD = 262.00 ft`, defined as "FINAL DEPTH(FT) OF BREACH" (`outputs/corrected/TETON.stdout.txt:849`) | Not found as a single reported figure; only disconnected elevation data points exist (crest El. 5332 ft, leak elevations El. 5045/5315 ft) with no computed depth in the source documents (`docs/TETON_OBSERVED_REFERENCE_DATA.md` §6) | **NOT_COMPARABLE** | No observed "breach depth" value exists. Computing one from the raw elevation points would require this project to invent the derivation itself (e.g., choosing which elevation is the valid "breach bottom" reference) — exactly the kind of new assumption instruction 5 prohibits, and `docs/TETON_OBSERVED_REFERENCE_DATA.md` §6 deliberately declined to do this already. |
| **Reservoir drawdown** | Initial `HI = 262.00 ft` (model-local datum) → final `HY_final = 85.34 ft` (`outputs/corrected/TETON.parsed.json`), a model-computed drop of 176.66 ft | Initial: **El. 5301.7 ft** (real-world USBR project datum), directly observed staff-gauge reading at the moment of failure (`docs/TETON_OBSERVED_REFERENCE_DATA.md` §7). Final: **no numeric value** — only the qualitative statement "reservoir essentially empty" for the window 5:00–6:00 p.m. June 5, 1976 | **NOT_COMPARABLE** | Two independent reasons: (1) the model's `HI`/`HY` use a **local relative datum** (`HU=262 ft` = dam crest = 0 reference for the local scale), while the observed `El. 5301.7 ft` is in the real **USBR project elevation datum** — the two are not on the same scale and no documented conversion exists in this repository; (2) even if the datum were reconciled, no numeric **final** observed elevation exists to form a drawdown comparison against — only a qualitative "essentially empty" statement, per instruction 3. |

---

## Conclusion: is the current data adequate for quantitative validation of the TETON case?

**No — not with the data collected so far.** Every one of the 7 requested items
resolves to `NOT_COMPARABLE`, except breach formation time, which resolves to
`CONDITIONALLY_COMPARABLE` and still yields no computed number because the
required assumption is not documented anywhere and this task explicitly
prohibits inventing one. **Zero items reached `DIRECTLY_COMPARABLE`.**

The two structural reasons are:

1. **A location mismatch for every flow-related quantity.** The only observed
   discharge/timing figures found (`docs/TETON_OBSERVED_REFERENCE_DATA.md` §1–2)
   are all measured several miles downstream of the dam, not at the breach
   itself — and this project has no downstream flood-routing capability (BREACH
   is a breach-formation/outflow model, not a downstream routing model), so there
   is no way to translate the model's breach-node output to those observation
   points, or vice versa, without adding a routing model this project does not
   have and was not asked to build.
2. **An unresolved reference-time and reference-datum gap between the model
   input and the historical record.** `TETON.DAT`'s `T=0` and its local `0–262
   ft` elevation scale were never documented (by this project or, apparently, in
   the input file's own provenance) against the real June 5, 1976 clock or the
   real USBR project elevation datum. Every timing- or elevation-based item is
   downstream of this same unresolved gap.
3. **A pure data-availability gap for breach geometry and final reservoir
   level.** `docs/TETON_OBSERVED_REFERENCE_DATA.md` found no observed top width,
   bottom width, depth, or final numeric reservoir elevation in either of the two
   official reports read in full (Independent Panel 1976; BOR Report of Findings
   1977) — a limitation of source availability (USGS OFR 77-765, the report most
   likely to contain this, could not be retrieved), not of this comparison
   exercise.

**What would be needed to turn this into an actual quantitative validation**,
without guessing: (a) the primary USGS OFR 77-765 hydrograph/breach-geometry data
(or another primary source with breach-face, not downstream, discharge); (b) an
explicit, sourced statement of what real clock time `TETON.DAT`'s `T=0`/`HPI=160`
condition represents (ideally from whoever originally authored this NWS/USBR
example dataset); and (c) a documented conversion between the model's local
elevation datum and the USBR project datum for this specific input file. None of
these currently exist in this repository, and this task's instructions do not
permit fabricating them. Until then, **the TETON example can only be used as a
qualitative plausibility check** (e.g., noting that the model's breach-face peak
of ~2.15 million cfs and the observed downstream figure of ~2.3 million cfs are
of the same order of magnitude), **not as a quantitative validation case.**
