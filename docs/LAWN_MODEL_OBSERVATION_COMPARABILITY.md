# LAWN_MODEL_OBSERVATION_COMPARABILITY.md

**Purpose.** Classify comparability (as in `docs/TETON_MODEL_OBSERVATION_COMPARABILITY.md`)
for the LAWN (Lawn Lake Dam, 1982) case, and — for items that classify as
`DIRECTLY_COMPARABLE` — compute the actual difference/relative error. **No code
or input file was modified** (`git status` confirmed clean for `src/`,
`original/`, and `examples/` throughout this investigation — all experiments
below run from byte-identical copies of `examples/LAWN.DAT`, verified by
`diff`). Model values are taken from the existing, already-committed
`outputs/corrected/LAWN.stdout.txt` / `outputs/corrected/LAWN.parsed.json`
plus one throwaway sensitivity re-run (§0) — no baseline was regenerated.
Observed values are from `docs/LAWN_OBSERVED_REFERENCE_DATA.md` (Jarrett and
Costa, USGS OFR 84-612).

**Classification legend:** identical to `docs/TETON_MODEL_OBSERVATION_COMPARABILITY.md`
(`DIRECTLY_COMPARABLE` / `CONDITIONALLY_COMPARABLE` / `NOT_COMPARABLE`).

**Related diagnostic:** `docs/LAWN_PIPE_WEIR_TRANSITION_DIAGNOSTIC.md`
explains a sharp discharge drop visible in the hydrograph shape right after
the peak (a pipe-roof-collapse flow-regime transition) and documents a
throwaway experiment that tried enabling disabled 1990-era smoothing code
for it. That experiment is **not adopted** and does not change any number in
this document (the discontinuity occurs strictly after the peak-flow instant
that `QBP`/`BRW`/`BO` are read from).

---

## 0. Sensitivity check: does the model reach a stable end-state, and does `TEH` matter?

`examples/LAWN.DAT` sets `TEH=1.0` (1-hour simulation duration). The last row
printed in the committed run (`outputs/corrected/LAWN.stdout.txt:261`,
`I=207, T=1.026 hr`) shows `QTOT=3,526 cfs` and breach top/bottom width
(`BT`/`BO`) still slowly increasing — raising the question of whether
`TEH=1.0` cuts the run off prematurely.

**Test performed:** a byte-identical copy of `examples/LAWN.DAT` was made in
a scratch directory with only the `TEH` field changed from `1.` to `5.`
(same `F10.2` fixed-width column position, verified by `diff` that no other
byte changed), then run through the unmodified `bin/breach1999_corrected`
logic (rebuilt from the unmodified `src/breach1999_documented_corrections.f`,
nothing patched for this specific test).

**Result:** the simulation did **not** run to `T=5.0`. It self-terminated at
`T=1.20 hr` (`I=209`) via a pre-existing, unmodified line in the 1999 source:

```fortran
      IF(KREG.EQ.3.AND.QB.LT.0.10*QBP) GO TO 120
```
(`src/breach1999_documented_corrections.f:1417`; present identically in
`original/SRC/Breach.for:1269`) — once in the draining/widening regime
(`KREG=3`), the model stops itself once breach flow drops below 10% of the
peak, independent of whatever `TEH` is set to.

At that natural stopping point (`I=209`): `BT=117.5 ft`, `BO=53.7 ft`,
`HY=5.1 ft`, `QB=2,031 cfs` (still 10% of `QBP`, i.e., **not** a fully
drained state). Comparing to the `TEH=1.0` cutoff (`I=207`, `T=1.026`):
`BT=117.0→117.5` (+0.4%), `BO=53.2→53.7` (+0.9%) — **essentially no further
change**. So:

- **Breach width was already close to converged at `TEH=1.0`.** The
  `T=1.026` values are a good proxy for the model's real "final" width
  prediction for this case, not an artificially truncated snapshot.
- **Reservoir level is a different story.** `HY` continues to drop
  meaningfully after width stops changing (7.32 ft at `T=1.026` → 5.1 ft at
  the natural stop, `T=1.20`) because water keeps draining through the
  now-fixed-size opening. More importantly, the model's own design
  intentionally stops **while still discharging at 10% of peak flow** — this
  is not "fully drained," and no value of `TEH` changes that, since the
  `QB<0.10*QBP` condition fires regardless. The observed comparison value
  (`docs/LAWN_OBSERVED_REFERENCE_DATA.md` §6, `10,975.69 ft`) is a **settled,
  6-days-later dead-storage survey** — a different physical endpoint than
  what this model is designed to ever report as "final." This is a
  structural/definitional gap confirmed by direct test, not a hypothesis.

---

## Comparison table

| Item | Model value (source) | Observed value (source) | Classification | Difference / relative error (only where `DIRECTLY_COMPARABLE`) |
|---|---|---|---|---|
| **Peak breach outflow** | `QBP = 21,562 cfs`, "MAX OUTFLOW(CFS) THRU BREACH" (`outputs/corrected/LAWN.stdout.txt:270`) | `18,000 cfs`, "from Lawn Lake dam" (`docs/LAWN_OBSERVED_REFERENCE_DATA.md` §1) | **DIRECTLY_COMPARABLE** — same location (at the dam) and same definition (peak breach discharge). **Caveat, not a disqualifier:** the observed figure is itself a dam-break *model* result (USGS's own routing model), not a field measurement — this is a model-vs-model comparison, not model-vs-ground-truth | `+3,562 cfs`, **+19.8%** relative to the observed figure (`(21562−18000)/18000`) |
| **Breach formation time** | Two model estimates, both "TIME OF FAILURE...LINEAR EQUIVALENT OF TRS": `TFH = −1.98 hr` (simplified equation method — **negative, i.e., not physically meaningful as a duration for this run**) and `TFHI = 0.16 hr` (9.6 min, integrated-Q_b method); also `TP = 0.19 hr` (11.4 min, time to peak) and `TB = 0.00 hr` (`outputs/corrected/LAWN.stdout.txt:271-285`) | **~10 min** (`docs/LAWN_OBSERVED_REFERENCE_DATA.md` §2) | **CONDITIONALLY_COMPARABLE** — same structural gap as TETON: nothing in this repository documents what real clock time the model's `T=0` (piping already present, `HPI=2`) represents, so no formal error is computed. **Qualitative note only** (not a validated comparison): `TFHI` (9.6 min) and `TP` (11.4 min) are numerically close to the observed ~10 min figure, which is a mildly encouraging sign worth recording, but this project explicitly does not treat "numerically close" as equivalent to "confirmed comparable" without the missing epoch assumption. Separately, `TFH = −1.98 hr` being negative is itself worth flagging as a model-output oddity for this fast-piping case, independent of the comparison question | *(none — conditional)* |
| **Final breach top width** | `BT = 117.5 ft` at the model's own natural end-of-run (`I=209`, §0 sensitivity test — **not** the `BRW=26.36 ft` "AT PEAK BREACH FLOW" summary field, which measures a much earlier instant; see correction note below) | `97 ft`, surveyed (`docs/LAWN_OBSERVED_REFERENCE_DATA.md` §3) | **DIRECTLY_COMPARABLE** — both now describe the final/fully-developed breach opening, not two different time instants | `+20.5 ft`, **+21.1%** (model over-predicts) |
| **Final breach bottom width** | `BO = 53.7 ft` at the model's natural end-of-run (same source as above; **not** `BO_final=26.36 ft` from the summary field) | `55 ft`, surveyed, corroborated twice (`docs/LAWN_OBSERVED_REFERENCE_DATA.md` §4) | **DIRECTLY_COMPARABLE** | `−1.3 ft`, **−2.4%** (very close) |
| **Breach depth** | `BRD = 28.00 ft`, "FINAL DEPTH(FT) OF BREACH" (`outputs/corrected/LAWN.stdout.txt:275`) | `28 ft`, surveyed (`docs/LAWN_OBSERVED_REFERENCE_DATA.md` §5) | **DIRECTLY_COMPARABLE** — but see the caveat below the table | `0.00 ft`, **0.0%** |
| **Reservoir drawdown** | `HI=26.00 ft → HY=5.1 ft` **at the model's own natural stopping point**, confirmed by §0 to occur **while still discharging at 10% of peak flow**, not a drained state | `10,996.42 ft → 10,975.69 ft` = 20.73 ft, where the final value is a **6-days-later, settled residual-lake survey** (`docs/LAWN_OBSERVED_REFERENCE_DATA.md` §6) | **NOT_COMPARABLE** (confirmed, not just suspected — §0 shows this is a structural property of the model's termination rule, unfixable by adjusting `TEH`) | *(none)* |

### Correction note on breach width (superseded an earlier version of this document)

An earlier pass compared `BRW`/`BO_final` from the `OUTPUT SUMMARY` block
against the observed survey and reported large under-predictions (−72.8%
top, −52.1% bottom). That was a **methodological error**: those two summary
fields are explicitly labeled "AT PEAK BREACH FLOW"
(`outputs/corrected/LAWN.stdout.txt:276,287`) — i.e., breach geometry at the
instant discharge peaks (`T=0.195 hr`), which for this piping case occurs
**before** most of the breach widening happens (widening continues well
past the flow peak, through the pipe-to-weir transition and subsequent
erosion). The observed `97 ft`/`55 ft` are final, post-event surveyed
values, which should be compared against the model's own **final**
width — read from the raw per-step table's last rows, not the
"at-peak-flow" summary fields. Corrected numbers are in the table above.

---

## Notes on the breach-depth "exact match"

`BRD = 28.00 ft` matching the observed `28 ft` exactly is worth treating
carefully rather than as an unqualified validation success. In
`outputs/corrected/LAWN.stdout.txt`, `HC_final = 0.000` (final elevation of the
breach bottom) and `HU = 28.00` (top of dam, echoing the input file's `HU=28`
directly) — so `BRD = HU − HC_final = 28 − 0 = 28` follows close to
mechanically once the breach has eroded down to the local datum's `HL=0`
floor, which is the typical/expected outcome for a full piping failure that
erodes to the valley floor. Since `HU=28` was itself a value chosen by
whoever built `LAWN.DAT` (already discussed in
`docs/LAWN_OBSERVED_REFERENCE_DATA.md`'s cross-check section as being close
to, but not identical to, the report's "26 ft high" figure), part of this
match reflects the **input file's crest value already being close to the real
dam height**, not solely an independent model prediction of erosion depth.
This does not invalidate the `DIRECTLY_COMPARABLE` classification (definition
and location still align), but it means the 0.0% figure should not be read as
strong evidence of the erosion-depth physics being correct — only that the
breach reached full depth in both the model and reality, which for a fully
piped-through embankment is the expected qualitative outcome either way.

---

## Summary

| Item | Classification | Result |
|---|---|---|
| Peak breach outflow | DIRECTLY_COMPARABLE | Model **+19.8%** vs. observed (model-estimate) |
| Breach formation time | CONDITIONALLY_COMPARABLE | Not computed; qualitatively close (9.6–11.4 min model vs. ~10 min observed) |
| Breach top width | DIRECTLY_COMPARABLE | Model **+21.1%** (over-prediction; corrected from an earlier, wrong −72.8% figure — see correction note above) |
| Breach bottom width | DIRECTLY_COMPARABLE | Model **−2.4%** (close; corrected from an earlier, wrong −52.1% figure) |
| Breach depth | DIRECTLY_COMPARABLE | Model **0.0%** (see mechanical-match caveat above) |
| Reservoir drawdown | NOT_COMPARABLE | Confirmed by direct test (§0): model's termination rule structurally never reaches a "fully drained" state |

Four of six rows now have a computed number, and three of those four are
reasonably close (+19.8%, +21.1%, −2.4%, 0.0%) — a materially better picture
than an earlier pass of this document showed, once the width fields were
read from the correct (final, not peak-flow-instant) point in the run. No
interpretation of *why* the small remaining gaps exist (e.g., input-parameter
choice vs. a genuine model/physics gap) is offered here — that would require
examining `LAWN.DAT`'s erosion-related parameters (`COHS`, `D50S`, `BMX`,
etc.) against the case, which is outside this comparison step and not
requested yet.
