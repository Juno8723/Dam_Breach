# RESERVOIR_REFILL_TEST.md

## Result summary (read this first)

**A full depletion → `QB=0` → refill → breach-flow-resumption cycle was not achieved within this session's effort budget, despite 12 documented parameter attempts across two base datasets.** This is reported honestly rather than engineered to appear successful. What *was* confirmed instead:

1. Direct code review that the BRCH2018-U02 guard (`src/breach1999_documented_corrections.f`, `IF(HY.LT.HC) THEN QB=0.0 ... GO TO 76`) is structurally correct: it doesn't touch breach geometry (`BO`, `BT`, `HC`), doesn't affect the mass-balance terms, and sits exactly where the weir-flow discharge would otherwise be computed.
2. Zero regression on all 5 real examples and both existing targeted tests (`negative_bmx.dat`, `steady_inflow.dat`) with this guard active.
3. **A real, naturally-occurring activation of the exact same code path**, documented in `docs/STATE_TRANSITION_DIAGNOSTIC.md`: BSMBOT2's own reservoir-filling phase produces `RESERVOIR_BELOW_BREACH_BOTTOM` at T=0.05 hr (pool below the not-yet-breached crest, `HC` initialized to `HU`) and `RESERVOIR_REFILL` at T=27.55 hr (pool rises to meet the crest) — after which the simulation proceeds completely normally to a full breach hydrograph (`QBP`>1.4M cfs). This confirms the guard correctly zeroes flow, doesn't corrupt state, and correctly *stops* zeroing flow once the condition clears, in a real (if not strictly *post-breach*) scenario. It does **not** confirm the *post-breach* depletion-refill case specifically.
4. The synthetic test built for this section (`examples/targeted/reservoir_refill.dat`) completes successfully on both `bin/breach1999_reference` and `bin/breach1999_corrected` with identical, physically plausible output (`QBP=310,552 cfs`, `HY_final=50.31 ft`), and exercises the same overtopping-initiation → erosion → widening pathway as CLAY, but does not reach a `HY<HC` state during this particular run.

**Per this task's own guidance, this is stated as:** *"The independently implemented refill logic was exercised through a synthetic test that confirmed no crashes, no NaN, no negative discharge, and correct mass-balance continuation under a two-pulse inflow hydrograph; a full depletion-then-resumption cycle was not reached in this specific run, and the underlying difficulty in constructing one is documented below."* No claim of exact equivalence with BRCH 2.0.0's own refill implementation is made — none could be, without their source or output.

## Why this was hard: three converging technical obstacles found during 12 attempts

All attempts followed the same target scenario: (1) trigger failure, (2) let it erode/drain, (3) cut inflow sharply so `HY` drops below the (by-then-stabilized) `HC`, (4) confirm `QB=0` there, (5) apply a second, larger inflow pulse, (6) confirm `HY` climbs back above `HC` and breach flow resumes, all without crashing or violating physical bounds.

1. **A minimum-erosion-per-step floor makes erosion hard to "pause" via inflow alone.** `original/SRC/Breach.for` clamps the erosion-depth increment via `IF(DHE.LT.0.01) DHE=0.01` — meaning downstream-face erosion advances by at least 0.01 ft every accepted time step once triggered (`NFAIL=1`), regardless of how low the current flow/shear stress is. Over the hundreds of time steps a typical run takes, this alone drives the breach to (near-)full depth within a few hours even when inflow is cut to near zero shortly after initiation. Confirmed by directly reducing the first pulse to 0.3 hr (attempt 5, 7) — erosion still reached full or near-full depth.
2. **For the three provided examples with `HL=0`** (`CLAY`, `LAWN`, `TETON`), the breach bottom `HC` erodes to (or within a fraction of a foot of) the valley floor `HL`. Since the model has a **separate, independent** hard-termination condition (`IF(HY.LT.HL+1.) GO TO 120`, untouched by this project — it is not part of BRCH2018-U02's documented scope), any attempt to let `HY` drop below such a near-`HL` `HC` risks the *entire simulation ending* before the second pulse can be tested (observed directly in attempts 1-7 and 11 — one of which, attempt 11, additionally produced a non-physical `HY=-186 ft` before the next check point, an out-of-envelope numerical artifact from an oversized synthetic pulse rather than a real depletion event, and was discarded).
3. **For `PERU` (the one provided example with a large `HC`-`HL` margin, `HC_final≈217 ft` vs `HL=0`)**, `HC` itself continues drifting downward under sustained low inflow at a pace similar to `HY`'s decline (attempt 10: 150 simulated hours of 5 cfs inflow after initiation still left `HY=228.99 ft` *above* `HC=217.62 ft`) — so `HY` never actually crosses below the (also-moving) `HC` within the tested window either.

None of these three findings are new bugs — they describe how the original 1999 erosion/termination logic behaves, which this session's scope did not (and should not) change. Constructing a input that reliably produces the target 8-step sequence would likely require either a dataset with an artificially-capped breach (e.g. a very small `BMX` that halts widening while leaving depth erosion room, combined with careful tuning of when depth-erosion itself naturally slows) or a properly-validated modification to erosion-resistance parameters beyond what trial-and-error in this session achieved (one attempt, raising `COHS` 13×, unexpectedly *accelerated* rather than slowed erosion — see attempt 6's raw data in `outputs/analysis/` if useful for a future session — indicating the clay erosion formula's parameter sensitivity is not simply monotonic and would need dedicated study, not guessing).

## What was built and tested

- `examples/targeted/reservoir_refill.dat`: CLAY.DAT's dam geometry with a synthetic two-pulse inflow hydrograph (`QIN=[500,50,10,10,300000,300000,10,10]` cfs at `TIN=[0,0.3,1,5,8,20,22,30]` hr) and `TEH` extended to 30 hr. Explicitly a software-path stress test, not a physically-representative hydrograph (the second pulse, 300,000 cfs, is far larger than any real inflow event for a dam this size) — chosen specifically to probe the code path's stability under an extreme, rapidly-varying input, which is a legitimate and separate kind of test value even though it didn't reach the target depletion state.
- `tests/test_reservoir_refill.py`: runs the 10 checks from this task's §6.3 against the parsed output, honestly reporting `PASS` / `FAIL` / `NOT_EXERCISED` per criterion (not just pass/fail) — see the table below. Exit code 0 (no `FAIL`s) confirms nothing broke; the `NOT_EXERCISED` entries are the honest finding of this section.
- `outputs/targeted/reservoir_refill/{reference,corrected}.{stdout,stderr,exitcode,parsed.json}`: both binaries run on the same input, both complete successfully with **identical** output (this specific input doesn't reach any of BRCH2010/2018's other trigger conditions either, so reference and corrected coincide here).

### Verification results (`python3 tests/test_reservoir_refill.py`)

| Criterion | Result | Detail |
|---|---|---|
| Simulation completed | PASS | |
| Depletion event exists (`HY<HC`) | NOT_EXERCISED | 0 of 870 accepted steps |
| `QB=0` while `HY<HC` | NOT_EXERCISED | no depletion event occurred |
| Inflow/mass-balance continues throughout | PASS | 870 accepted-step rows |
| Elevation rises back above `HC` after a dip | NOT_EXERCISED | no dip-then-recovery observed |
| Breach flow resumes after recovery | NOT_EXERCISED | depends on the above |
| No NaN in `HY`/`QB` | PASS | |
| No numeric overflow in output | PASS | |
| No negative breach discharge | PASS | |
| No non-physical runaway elevation | PASS | |

## Recommendation for a future session

Start from `PERU.DAT` (large natural `HC`-`HL` margin) rather than `CLAY.DAT`, and instead of trying to *pause* erosion via inflow, let the breach fully stabilize first (its natural ~120 hr run), then apply a controlled study of exactly how fast `HC` itself continues to drift under near-zero inflow (this session found it drifts, but did not fully characterize the rate) to find a pulse-timing window where the (slower-moving, once `KREG=3` widening is well underway) `HC` can be out-paced by `HY`'s decline before a second pulse arrives. This would need dedicated iteration time this session did not have remaining.
