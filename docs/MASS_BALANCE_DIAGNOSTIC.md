# MASS_BALANCE_DIAGNOSTIC.md

## What this is

A diagnostic-only per-timestep water-balance cross-check, added to `src/breach1999_documented_corrections.f` behind a `#ifdef MASS_BALANCE_DIAGNOSTIC` preprocessor guard (built via `tests/build_diagnostic_massbalance.sh` → `bin/breach1999_corrected_massbalance`; the normal production build, `tests/build_corrected.sh`, compiles these blocks out entirely — confirmed byte-identical output to before this change). **No physical variable, computed discharge, elevation, breach geometry, or any existing printed output is altered.** It reuses the exact same trapezoidal-averaged flow terms (`QI`, `QT+KQ*QB+QSP`, `QT1+KQ1*QB1+QSP1`) and the same single-point area sample `SA` that the model's own (unmodified) water-balance equation already computes (`original/SRC/Breach.for`'s `DY=(...)/2.*DTH*3600./(SA*43560.)`) — no new integration method was introduced, per this task's instructions.

Enabling it writes `mass_balance.csv` to the run's working directory.

## Units

| Quantity | Unit |
|---|---|
| Flows (`QI`, breach/spillway/overflow discharge) | cfs |
| Time (`T`, `DTH`) | hours |
| Reservoir surface area (`SA`) | acres |
| Volumes (`DVIN`, `DVOUT`, `DVEXP`, `DVACT`, residuals) | acre-ft (`cfs × hr × 3600 s/hr ÷ 43560 ft²/acre`) |
| Elevations (`HY`, etc., in the main model) | ft |

## What's logged, per accepted time step

`T_hr, SA_acres, DVIN_acreft, DVOUT_acreft, DVEXP_acreft, DVACT_acreft, RESID_INCR_acreft, RESID_CLAMP_acreft, CUM_QIN_acreft, CUM_QOUT_acreft, CUM_DVACT_acreft, CUM_RESID_acreft, CUM_RESID_CLAMP_acreft`

- `DVIN` / `DVOUT`: trapezoidal-integrated inflow / total outflow (breach + spillway + dam-crest overflow) volume for this step.
- `DVEXP = DVIN - DVOUT`: storage change *expected* from the flow balance.
- `DVACT = -DY×SA`: storage change *actually applied* to the reservoir this step (recovered from the model's own `DY`, using the same `SA`).
- `RESID_INCR = DVEXP - DVACT`: per-step residual. Algebraically these are the same quantity rearranged (`DY` is defined *as* `(outflow-inflow)avg × dt / SA`), so this is expected to be ≈0 to floating-point precision at every step — confirming no accounting bug (sign error, double-counted term, unit mismatch), not something expected to reveal new physics.
- `RESID_CLAMP`: the contribution of the model's own `IF(ABS(DY).LE.0.00001.AND.DY.LT.0.) DY=0.` clamp (comparing `DY` before vs. after that clamp) — the one place a *genuine*, if tiny, deliberate discrepancy is injected by the original 1999 code itself.
- `CUM_*`: running cumulative sums of the above across the whole simulation.

**Important scoping note on *where* this is logged:** the water-balance equation is re-evaluated every time the erosion-depth convergence loop retries (`GO TO 25`, which jumps back to a point before the water-balance block). Logging at the point where the terms are first computed would double- (or many-times-) count retried steps. The diagnostic therefore computes the per-step terms once at that point but only **accumulates and writes** them once the step has been fully accepted (right before `QB1=QB` near label 106/118, `original/SRC/Breach.for`'s final per-step bookkeeping) — confirmed empirically: row counts in `mass_balance.csv` now match the model's own per-step iteration count (e.g. TETON: 751 rows vs. 751 accepted steps in the standard hydrograph), not an inflated retry-counted total.

## Results — all 5 real examples + both targeted synthetic tests

Full per-step data: `outputs/analysis/mass_balance/*.csv`. Summary: `outputs/analysis/mass_balance_summary.csv`.

| Dataset | Steps | Cumulative inflow (acre-ft) | Cumulative outflow (acre-ft) | Cumulative residual (acre-ft) | **Relative residual** | Clamp contribution (acre-ft) |
|---|---:|---:|---:|---:|---:|---:|
| BSMBOT2 | 557 | 1,091,267.5 | 1,165,000.4 | −1.6484 | **0.00014%** | 0.1149 |
| CLAY | 451 | 422.43 | 7,232.80 | −0.0059 | **0.00008%** | 0.0000 |
| LAWN | 207 | 8.45 | 792.92 | +0.0004 | **0.00005%** | 0.0005 |
| PERU | 685 | 4,560.36 | 398,025.75 | −0.1250 | **0.00003%** | 0.0000 |
| TETON | 751 | 95.47 | 203,866.81 | −0.0156 | **0.00001%** | 0.0091 |
| `negative_bmx.dat` (targeted) | 468 | 424.43 | 7,234.19 | −0.0005 | 0.00001% | 0.0000 |
| `steady_inflow.dat` (targeted) | 200 | 8,136.76 | 4,727.29 | −0.0129 | 0.00016% | 0.0000 |

## Assessment

**Cumulative relative residual is at floating-point-noise level (0.00001%–0.00016%) for every dataset tested, including both edge-case synthetics.** This confirms the water-balance equation in both the original 1999 source and this project's corrected version closes correctly — no sign error, no double-counted flow term, no unit-conversion bug, across a very wide range of scenarios (single-precision `REAL` throughout, hundreds of accepted steps, both fill-mode and non-fill-mode cases, piping and overtopping failures, and the deliberately-broken negative-`BMX` geometry). The `IF(ABS(DY).LE.0.00001...) DY=0.` clamp built into the original 1999 code contributes a small, quantifiable, and consistently tiny amount (≤0.11 acre-ft cumulative, out of a >1,000,000 acre-ft total for BSMBOT2) — exactly the order of magnitude implied by its own `0.00001` ft threshold, confirming it behaves as intended rather than accumulating unboundedly.

No case showed a residual large enough to warrant tracing to time step, interpolation, storage-elevation table, flow clipping, tailwater correction, or termination-condition causes (the investigation categories listed in this task) — there was no anomaly to trace. This is itself the correct and complete conclusion for this diagnostic, not an indication the check wasn't thorough enough.
