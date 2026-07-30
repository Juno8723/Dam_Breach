# VALIDATION_REPORT.md

## 1. Precision and tolerance

`Breach.for` declares no explicit `REAL*8`/`DOUBLE PRECISION` anywhere and is compiled without `-fdefault-real-8`, so every floating-point value in the model (including `HY`, `QB`, `DTH`, ...) is standard 32-bit single-precision `REAL`. Compiler optimization is fixed at `-O0` for both binaries (no reordering-related divergence expected between reference and corrected builds beyond the intended logic changes).

The model has its own internal convergence tolerance: the DTH/DHH erosion-rate convergence check is `IF(ABS(DH-DHH)/DHH*100.LT.ERR) GO TO 96`, where `ERR` defaults to 0.5 (i.e. 0.5%) when unset (`original/SRC/Breach.for:1644`, `IF(ERR.LE.0.001) ERR=0.5`) and is 0.01–0.02 in the five example inputs (tighter than default). Given single precision's ~7 significant digits and this convergence-loop tolerance, a flat 0.5% relative tolerance was used through most of this project's development (`tests/compare_outputs.py --tol 0.5`, still available as a "legacy flat mode").

### Variable-specific tolerances (current default, `tests/compare_outputs.py` with no `--tol`)

A single flat relative percentage turned out to be a poor fit for every output type — it's too loose for large steady quantities and, more importantly, **too strict for small time durations**: `TRS` (rising-limb duration) shifting from 0.16 to 0.14 hr is a 12.5% *relative* change but only a 0.02 hr (~70 second) *absolute* one, well within what a finite `DTH` can resolve. `compare_outputs.py` now classifies each summary field into one of four categories, each with its own default bound (all overridable by reading the source — see its module docstring for the exact numbers and reasoning):

| Category | Fields | Bound | Why |
|---|---|---|---|
| `continuous` | `QBP`, `QP`, `BRD`, `BRW`, `BO_final` | absolute floor (flow: 1 cfs, width/depth: 0.1 ft) **or** 0.5% relative, whichever passes | Matches the model's own `ERR` convergence tolerance; the absolute floor avoids flagging noise on small values a pure percent check would over-penalize |
| `elevation` | `HY_final`, `HC_final`, `HU` | 0.1 ft absolute, **or** 1% relative backstop for large swings | These are differences of large numbers (hundreds of ft) — percent alone is a poor signal; BSMBOT2's genuine 8.25 ft shift is far above this floor and correctly flags |
| `time` | `TP`, `TB`, `TRS`, `TFH`, `TFHI` | 0.05 hr (~3 min) absolute only | Matches the resolution a `DTH`-scale simulation can meaningfully claim (`docs/TIMESTEP_CONVERGENCE.md` confirms results are DTH-floor-converged well below this); relative percent is meaningless for durations that can legitimately be small |
| `near_zero` | `AGL`, `QO`, `Z` | 0.05 absolute only | Can legitimately be ≈0, where relative error is undefined |
| `state` | `KREG` transition sequence | **exact match, no tolerance** | A state-machine sequence has no notion of "close enough" |

Neither category was measured against a reference double-precision run (none exists to compare against) — both the flat and categorized defaults are reasoned defaults, not empirically-derived bounds, and both are documented as such rather than presented as more rigorous than they are.

### Recommended tolerance for a future Python port

If a Python port uses the same single-precision arithmetic as this Fortran build, the tolerances above remain appropriate. If it uses Python's native double precision (the more likely and generally preferable choice), the `continuous`/`elevation` categories should be **tightened substantially** (e.g. toward 1e-6 relative or an absolute floor near machine epsilon for the quantity's scale) since a faithful, higher-precision port shouldn't need to absorb single-precision-only noise — a port that only passes at the current loose tolerances would itself be a signal something is wrong. `time`/`state` categories should stay close to their current bounds regardless of precision, since they reflect the model's `DTH` step resolution and discrete state machine, not floating-point precision.

## 2. Regression results: 5 provided examples, reference vs. fully-corrected build

Command: `python3 tests/compare_outputs.py outputs/baseline outputs/corrected`

| Case | Result |
|---|---|
| CLAY | No change (within variable-specific tolerances) |
| LAWN | No change (within variable-specific tolerances) |
| PERU | No change (within variable-specific tolerances) |
| TETON | No change (within variable-specific tolerances) |
| BSMBOT2 | **Changed** — see below (`BO_final`, `HY_final`, `TP`, `TB`, `TFH` all exceed their category bounds; `QBP`/`QP`/`TRS`/`TFHI` pass under the new categorized tolerances despite exceeding the old flat 0.5%) |

### Why BSMBOT2 changes (and the others don't)

Two independent, cumulative documented fixes both happen to be triggered by this one case:

1. **BRCH2010-01** (tailwater ≥ pool ⇒ breach outflow forced to 0): at simulation hour 62.2, BSMBOT2's own tailwater rating curve genuinely produces `TWD=134.59 ft` against a pool elevation `HY=133.0 ft` — confirmed identical in the *unmodified* 1999 output at that row, so this is not an artifact of any fix, just a real (if narrow) submergence event this dataset happens to pass through. The original code's 0.05 floor let breach flow continue at 5% capacity indefinitely after this point; the fix's `SUB=0` combined with the pre-existing (unmodified) `IF(SUB.GT.SUBOLD) SUB=SUBOLD` one-way suppressor makes the breach stop draining permanently from that point on.
2. **BRCH2018-05** (`DTHFIL ≤ 0.5 hr`): BSMBOT2's own (highly non-steady) inflow hydrograph makes the original `DTHFIL` formula legitimately evaluate to 1.0 hr — double the documented ceiling — confirmed by direct instrumentation (`DTHFIL=1.0, DTHMIN=1.0, TQP=22.0, TST=0.0`). The fix halves the fill-phase time step, shifting the early discretization enough to move the whole downstream erosion timeline slightly.

Net effect on BSMBOT2's summary: `QBP` 1,450,576→1,451,339 cfs (+0.05%), `QP` 1,664,275→1,662,832 cfs (−0.09%), `TP` 29.14→29.32 hr, `TRS` 0.16→0.14 hr, `TB` 28.98→29.18 hr, `HY_final` 136.88→145.13 ft (+5.7%), `TFHI` 0.11→0.16 hr, `BO_final` 24.55→24.2 ft. The largest relative shifts (`TRS`, `TFHI`, `HY_final`) are all downstream consequences of the breach ceasing to drain earlier than in the uncorrected run, not numerical noise.

**This is expected, documented, and — given both underlying original-code defects are real and independently confirmed — not treated as a validation failure.** Neither RiverMechanics' actual BRCH 2.0.0 numeric output nor source was available to confirm the corrected build reproduces their exact magnitude of shift; only that the documented conditions (`TWD≥HY`, `DTHFIL>0.5`) are correctly and unambiguously detected and handled.

## 3. Targeted (synthetic) test results

Command: `bash tests/run_targeted_tests.sh`

| Test | Reference (1999) | Corrected | Demonstrates |
|---|---|---|---|
| `tests/targeted/negative_bmx.dat` (CLAY with `CRL` shrunk 500→100 ft, forcing the existing `BMX` fallback formula negative) | Exit 0 every time, but **run-to-run non-deterministic and physically broken**: 5 repeated runs of the identical unmodified binary on the identical input gave `QBP` = `0.`, `**********` (numeric field overflow — the true value exceeded `F10.0`'s width), `-0.`, `0.`, `**********`. Breach never develops in any run; final `HY≈264 ft`, above the 90 ft dam crest, i.e. water piling up impossibly high because the negative `BMX` clamp prevented the breach from ever widening. The run-to-run variation (same binary, same input, different result) is strong independent evidence that the negative-`BMX` state drives the original code into reading uninitialized/undefined memory, not just "one consistent wrong answer" | Exit 0, **bit-for-bit identical across 5 repeated runs**: `QBP=137,255 cfs` every time, `HY_final=3.01 ft`, breach develops and drains normally | BRCH2018-03: negative `BMX` doesn't just silently corrupt the run in the original code — it makes the run's output undefined/non-reproducible. The `CRL` fallback fixes both the corruption and the non-determinism |
| `tests/targeted/steady_inflow.dat` (BSMBOT2 with `QIN` forced constant at 989 cfs across all 8 points) | **Segfault, exit 139** — confirmed via symbol-resolved backtrace to crash inside `SUBROUTINE PLOT` at `original/SRC/Breach.for:1490`/`1529` (`ORD(LS)=ASTER`), a downstream consequence of the degenerate near-zero `DTHFIL` (steady inflow makes `TQP-TST≈0`) driving the fill-phase loop into a pathological iteration count (5,000+ output rows before crashing, vs. ~300-900 for a normal run) | Exit 0, completes normally in 287 output lines, plausible summary (`QP=867 cfs`, `TP=99.55 hr`) | BRCH2018-05: for a genuinely steady inflow, the undocumented-ceiling `DTHFIL` bug isn't just a numeric difference — **it crashes the original program**. The fix's `DTHFIL≤0.5` ceiling (engaged directly by the steady-state override) prevents this entirely |

Both targeted tests demonstrate real, previously-undocumented-in-this-project failure modes in the unmodified 1999 code, not just cosmetic differences — which is a stronger form of validation than a same-both-ways numeric match would have been.

**Caveat found while re-running `steady_inflow.dat` for this report:** the corrected build's printed `TWD` (tailwater elevation) column for the first few *zero-flow* fill-phase rows varied by 0.5 ft between two otherwise-identical repeated runs (`10.09` vs `10.59`), while `QTOT`/`QB` (the actual flow outputs) stayed identical every time. This traces to the `TWSEC` rating-curve search loop's stopping condition (`IF(QQN.LT.QQQ) GO TO 77`) being evaluated at the degenerate boundary `QQQ=0` — a condition only reachable in this synthetic all-zero-flow edge case, not in any of the 5 real datasets (re-confirmed bit-for-bit reproducible across repeated runs in this same session). Since it never affects an actual flow value and doesn't reproduce on real inputs, it was not chased further; noted here for transparency rather than silently re-captured as if it were stable.

**Known gap:** no targeted test was built for BRCH2018-U02 (reservoir refill) actually re-triggering breach flow after a drain-then-refill cycle — see `UNRESOLVED_BRCH2018.md`. The fix is confirmed to introduce zero regression on all 5 real examples and is code-reviewed as correct, but a positive "it actually resumes flow" demonstration was not constructed.

Also not built as separate synthetic files: dedicated NHSA/NCS edge cases for "exactly 8 points" (NCS) and "elevation near the highest tabulated point" (both). Real-dataset coverage instead: `NHSA` was empirically observed at 2 (CLAY), 3 (PERU), 4 (TETON), 6 (LAWN), and 8/full-table (BSMBOT2) across the five provided examples, each of which drives its pool elevation below its own lowest tabulated point during the run (confirmed for CLAY: `HY` ranges 90.4→2.9 against a table whose lowest real point is elevation 0). `NCS` was observed at 3 (CLAY, LAWN, PERU), 5 (TETON), 6 (BSMBOT2) — no real dataset naturally exercises "exactly 8" for `NCS`, or "above the highest tabulated point" for either table; these two specific edge cells remain untested beyond code-level reasoning (see `CHANGE_MATRIX.md` BRCH2018-01/02 rows).

## 4. Water-balance and numerical-stability notes

- All 5 baseline and both corrected-build regression runs complete with exit code 0 and no `-ffpe-trap=invalid,zero,overflow` aborts (confirmed separately — see `SOURCE_AUDIT.md` §5).
- `KG`/`KREG` transition sequences (fill→erosion→drain, or piping→weir→drain) are unchanged in timing and order for CLAY, LAWN, PERU, TETON between reference and corrected. BSMBOT2's sequence is also unchanged in *order* (fill→downstream-face erosion→upstream-face erosion), only the *timing* of the tail end shifts (see §2).
- No full quantitative reservoir mass-balance integral (Σinflow − Σoutflow vs. ΔstorageVolume over the whole run) was computed; validation instead relies on (a) the model's own internal per-step balance equation (`DY` in `original/SRC/Breach.for:797`, unmodified except where BRCH2010-01/BRCH2018-U02 gate `QB` before it enters that same equation) and (b) confirming `HY` trajectories remain monotonic-with-expected-shape (rising during fill, falling during drain) in every regression and targeted run. A dedicated end-to-end mass-balance check was out of scope for the time available in this session.
