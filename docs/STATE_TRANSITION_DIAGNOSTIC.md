# STATE_TRANSITION_DIAGNOSTIC.md

## What this is

A diagnostic-only failure-state transition log, added to `src/breach1999_documented_corrections.f` behind `#ifdef STATE_TRANSITION_DIAGNOSTIC` (built via `tests/build_diagnostic_statetrans.sh` → `bin/breach1999_corrected_statetrans`; the normal production build compiles these blocks out entirely, confirmed byte-identical to before this change). Logs only fire when a tracked state actually changes — no per-step spam, no effect on any physical variable. Running the diagnostic build writes `state_transitions.csv` to the working directory.

`KG` is computed exactly the way the existing printed `KRP` column already is (`KREG`, or `-1` while `NFIL=1`/reservoir filling) — not a new state variable, matching this task's own terminology.

## Logged fields

`T_hr, prev_KG, new_KG, prev_KREG, new_KREG, HY_ft, TWD_ft, HC_ft, BT_ft, depth_ft, QB_cfs, QTS_cfs, DTH_hr, reason`

`depth_ft` is `HU-HC` (current breach depth, matching how the final `BRD` summary value is defined). Logged once per **accepted** time step only (same double-counting concern as the mass-balance diagnostic — see `docs/MASS_BALANCE_DIAGNOSTIC.md` — solved the same way: computed once per accepted step at the same code location).

## Reason labels

| Label | Trigger | Confidence |
|---|---|---|
| `PIPE_INITIATION` | First recorded state is `KREG=4` (piping) | High — `KPIP` is a fixed input flag, checked once |
| `OVERTOPPING_INITIATION` | First recorded state is `KREG=1` | High |
| `INITIAL_STATE` | First recorded state is anything else (e.g. `KREG=2` directly, as in PERU) | Neutral fallback, used when neither of the above confidently applies |
| `OPEN_BREACH_TRANSITION` | `KREG` 4→1 or 4→2 | High — this is exactly the "PIPE FLOW TO WEIR FLOW TRANSITION" the 1999 source itself announces (`original/SRC/Breach.for`'s own `WRITE(6,997)` at that code point) |
| `PIPE_ROOF_COLLAPSE` | Any transition into `KREG=5` | High — `KREG=5` is deep-seated collapse by construction |
| `EROSION_REGION_CHANGE` | Any other transition among `KREG∈{1,2,3}`, or out of `KREG=5` back into `{1,2,3}` | Medium — physically means "erosion moved to a different part of the dam / drainage phase," but this project cannot confirm from the public release notes whether RiverMechanics distinguishes these more finely |
| `RESERVOIR_BELOW_BREACH_BOTTOM` / `RESERVOIR_REFILL` | The independently-implemented BRCH2018-U02 guard's own condition, `HY<HC`, turning on/off | See caveat below |
| `SIMULATION_TERMINATION` | Execution reaches label 120 (any of the 6 independent exit conditions — `T>TMAX`, `HY<HL+1`, low-flow-in-drain-phase ×2, `I≥4999`, `T>TEH`) | High |
| `KG_x_TO_y` | Neutral fallback for a `KG` (fill/non-fill) change not otherwise categorized above | Used when the physical reason can't be confidently named — per this task's own guidance |

**Important caveat on `RESERVOIR_BELOW_BREACH_BOTTOM`/`RESERVOIR_REFILL`:** `HC` (controlling breach-bottom elevation) is initialized to `HU` (the dam crest) before any breach has formed. This means the generic `HY<HC` check **also** fires during the ordinary reservoir-filling period before failure begins (pool below the still-intact crest counts as "below breach bottom" in the strict sense), not only during the post-breach depletion-then-refill scenario BRCH2018-U02 was written for. This is visible in the BSMBOT2 log below (`RESERVOIR_BELOW_BREACH_BOTTOM` at T=0.05, `RESERVOIR_REFILL` at T=27.55 — this is the pool rising up to meet the still-un-breached crest, not a post-breach refill event). The label names the *condition* accurately; interpreting *which physical scenario* triggered it requires reading `new_KG`/`new_KREG` alongside it, which is why both are logged on every row.

## Per-dataset transition timelines

Full CSVs: `outputs/analysis/state_transitions/*.csv`.

**TETON** (piping failure):
| T (hr) | KREG | Reason |
|---:|---|---|
| 0.005 | 4 | PIPE_INITIATION |
| 1.910 | 2 | OPEN_BREACH_TRANSITION |
| 3.330 | 3 | EROSION_REGION_CHANGE |
| 4.019 | 3 | SIMULATION_TERMINATION |

**LAWN** (piping failure, small dam):
| T (hr) | KREG | Reason |
|---:|---|---|
| 0.0025 | 4 | PIPE_INITIATION |
| 0.1975 | 2 | OPEN_BREACH_TRANSITION |
| 0.2164 | 3 | EROSION_REGION_CHANGE |
| 1.026 | 3 | SIMULATION_TERMINATION |

**CLAY** (overtopping failure):
| T (hr) | KREG | Reason |
|---:|---|---|
| 0.005 | 1 | OVERTOPPING_INITIATION |
| 2.620 | 2 | EROSION_REGION_CHANGE |
| 10.229 | 2 | SIMULATION_TERMINATION |

**PERU** (starts mid-erosion, no distinct initiation phase captured by this input):
| T (hr) | KREG | Reason |
|---:|---|---|
| 0.010 | 2 | INITIAL_STATE |
| 122.658 | 2 | SIMULATION_TERMINATION |

**BSMBOT2** (overtopping, with reservoir fill phase and the BRCH2010-01 tailwater-submergence event documented in `docs/BSMBOT2_FIX_ATTRIBUTION.md`):
| T (hr) | KG / KREG | Reason |
|---:|---|---|
| 0.05 | KG −1 / KREG 1 | OVERTOPPING_INITIATION |
| 0.05 | (below crest) | RESERVOIR_BELOW_BREACH_BOTTOM *(fill-period, not post-breach — see caveat)* |
| 27.55 | (reaches crest) | RESERVOIR_REFILL *(fill-period, not post-breach — see caveat)* |
| 27.60 | KG 1 | KG_1_TO_1 *(fill flag clears; KREG unchanged — neutral label, no confident finer name)* |
| 29.205 | KREG 2 | EROSION_REGION_CHANGE |
| 100.313 | KREG 2 | SIMULATION_TERMINATION |

Note BSMBOT2's log does **not** show a distinct entry at T≈62 hr for the tailwater-submergence event documented elsewhere — that event changes `SUB`/`QB` continuously, not `KREG`, so it is invisible to a `KREG`-based transition log by design. It is fully characterized instead in `docs/BSMBOT2_FIX_ATTRIBUTION.md` and the mass-balance / hydrograph data.

## Regression check

The normal production build (`tests/build_corrected.sh`, no `-D` flags) was rebuilt and re-run against all 5 examples after adding this instrumentation; output is byte-for-byte identical to before (`git status` clean on `outputs/corrected/`).
