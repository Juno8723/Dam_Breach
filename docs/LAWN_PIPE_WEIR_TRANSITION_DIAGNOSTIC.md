# LAWN_PIPE_WEIR_TRANSITION_DIAGNOSTIC.md

**Purpose.** Explain, with code and output evidence, the sudden drop in
total outflow (`QTOT`) seen immediately after the discharge peak in the LAWN
(Lawn Lake Dam, 1982) model run, and document a throwaway experiment that
tested whether an existing-but-disabled piece of the original 1999 source
would fix it. **No code in `src/`, `original/`, or any input file was
modified.** The experiment lives entirely in a generated, clearly-labeled
variant file (`tests/attribution/variants/lawn_pipe_weir_smoothing_enabled.f`,
produced by `tools/build_lawn_pipe_weir_smoothing_variant.sh`) and its own
separate binary (`bin/breach1999_lawn_pipe_weir_smoothing_enabled`), which is
not used by any regression test.

## 1. What the discontinuity looks like

`outputs/corrected/LAWN.stdout.txt`, rows 77–81 (columns:
`I T DTH KG KC QTOT QTS QB SUB BT HY HC BO PPP HP TWD DH DHH KIT AGL`):

```
77   0.192 ...  20529.  ...  25.7  23.5  0.0  25.7 ...
78   0.195 ...  21562.  ...  26.4  23.4  0.0  26.4 ...   <- QBP (reported peak)
   PIPE FLOW TO WEIR FLOW TRANSITION
80   0.200 ...   7086.  ...  27.1  23.3  3.6  27.1 ...   <- QTOT crashes -67% in one step
81   0.202 ...  11334.  ...  82.6  23.3  3.6  27.1 ...   <- breach width also jumps 27.1->82.6 in one step
```

Total outflow drops from 21,562 to 7,086 ft³/s in a single timestep (I=78 to
I=80; row I=79 is consumed by the transition itself and isn't printed as a
normal data row), then partially recovers over the next several steps.

## 2. Why: LAWN is a piping failure, and this is the pipe-roof-collapse transition

`examples/LAWN.DAT` line 1 (`HI=26, HU=28, HL=0, HPI=2`) has `HPI>0.0001`, so
`KPIP=1` (`src/breach1999_documented_corrections.f:244`) — the simulation
starts in **piping mode** (`KREG=4`), modeling flow through a confined
pipe/orifice, not open-channel flow. This is confirmed in
`docs/STATE_TRANSITION_DIAGNOSTIC.md`: `T=0.0025 PIPE_INITIATION` →
`T=0.1975 OPEN_BREACH_TRANSITION` (`KREG=4`→`2`) → `T=0.2164
EROSION_REGION_CHANGE` (`KREG=2`→`3`).

During `KREG=4`, the pipe's crown/top elevation (`HPU`, printed as the `PPP`
column per `docs/VARIABLE_DICTIONARY.md`) erodes upward every step — visible
in the raw table as `PPP` rising from 2.0 (I=1) to 15.2 (I=78) while the
reservoir stays near `HY≈23-26`. The transition trigger is
(`src/breach1999_documented_corrections.f:1272-1274`):

```fortran
      IF(KREG.NE.4) GO TO 100
      DLL=HPU-0.5*(HPU+HC)
      IF(HY.GT.HPU+DLL) GO TO 105
C      TRANSITION FROM ORIFICE TO WEIR FLOW
   99 KPIP=0
      KPT=1
```

`DLL=0.5*(HPU-HC)` is half the remaining pipe-crown-to-breach-bottom
distance. The condition fires once the reservoir head above the pipe crown
(`HY-HPU`) shrinks to less than that half-distance — i.e., once continued
crown erosion has left too little material for the pipe to remain a stable
roofed conduit, the model assumes the roof collapses and switches from
confined pipe flow to open weir flow. This is a real, physically-motivated
regime change (the same "pipe roof collapse → open breach" transition
described qualitatively for real piping dams, including in this project's
own `docs/RESERVOIR_REFILL_TEST.md` discussion of `KREG` transitions).

**What happens computationally at that exact instant**
(`src/breach1999_documented_corrections.f:1276-1358`):

1. `HC=HC+HDP` (line 1283) — the breach-bottom elevation jumps up
   discontinuously by a computed collapse increment `HDP`, representing the
   collapsed roof material.
2. `KREG` becomes `2` (line 1303, for a man-made dam, `KNAT=0`), and the
   breach geometry variables are **recomputed from a different geometric
   model** — a trapezoidal open-channel cross-section (`BB1=BO`, `WC`, side
   slopes `ZU`/`ZD`) — instead of the pipe's circular/rectangular
   cross-section used during `KREG=4`. This is why `BT` (top width) jumps
   from 27.1 to 82.6 ft in one printed step: it is not "27.1 ft eroding
   wider," it is "an entirely different geometric formula being evaluated
   for the first time."
3. The discharge equation switches from a pipe/orifice formula (pressurized
   flow through a roughly-circular opening) to a weir formula — a new weir
   discharge estimate is computed as `QBW=3.*BO*(HY-HCP)**1.5` (line 1347,
   the standard broad-crested weir form).

Because the new geometry and the new equation are both evaluated using the
**same `HY`** the old orifice equation had (the reservoir has not had time to
respond within one timestep), and the two equations have fundamentally
different mathematical shapes, there is no guarantee the newly computed flow
equals the just-prior orifice-flow value. In this case it computes
substantially lower — hence the visible drop.

## 3. This is a known limitation left in the original 1999 source, not something this project introduced

Immediately after the transition, the source contains a smoothing/blending
calculation that is clearly intended to prevent exactly this kind of jump
(`src/breach1999_documented_corrections.f:988-996`):

```fortran
      QEXP=(DHYY/DHPP)*DQP
      QTR=QB+QEXP
C     CHANGE 8/13/90
C     HCPCHK SUBSTITUTED FOR HCP
      HCPCHK=HCP-HL
CCC      IF(HCPCHK.GT.3.) QB=QTR
CCC      IF(HCPCHK.LE.3..AND.QTR.LE.QPMAX) QB=QTR
CCC      IF(HCPCHK.LE.3..AND.QTR.GT.QPMAX) QB=QPMAX
C     END CHANGE 8/13/90
```

`DQP=(QPMAX-QBW)*0.9` (line 1348) is precomputed as 90% of the gap between
the last pipe-flow value and the new weir-flow estimate, and `QEXP` ramps
that gap in proportionally to how far the reservoir has moved past the
collapse threshold (`DHYY/DHPP`). This is a linear-blend transition —
**but the three lines that would actually apply `QTR` to `QB` are commented
out with a `CCC` prefix**, so `QTR` is computed every step and then
discarded. **This exact same commenting-out is present in
`original/SRC/Breach.for:849-851`, unchanged** — confirmed by direct `diff`
against this project's corrected source. This is therefore a genuine,
longstanding characteristic of the unmodified 1999 NWS BREACH model, dated
by its own comment to a 8/13/90 change that was implemented and then left
disabled — not a defect introduced by this project, and not something this
project's documented BRCH2010/2018 correction scope covers.

## 4. Experiment: what happens if the disabled smoothing is enabled

**Method:** `tools/build_lawn_pipe_weir_smoothing_variant.sh` generates
`tests/attribution/variants/lawn_pipe_weir_smoothing_enabled.f` — a copy of
`src/breach1999_documented_corrections.f` with only those 3 `CCC` lines
uncommented (verified via `diff` to be the only difference) — builds it as
`bin/breach1999_lawn_pipe_weir_smoothing_enabled`, and runs it against the
same, byte-identical `examples/LAWN.DAT` (verified via `diff`). Output saved
to `outputs/analysis/lawn_pipe_weir_transition/LAWN_smoothing_enabled.stdout.txt`.

**Result:** the sudden drop is indeed gone —

```
78   0.195 ...  21562. ...   <- same as before (pre-transition, unaffected)
   PIPE FLOW TO WEIR FLOW TRANSITION
80   0.200 ...  20956. ...   <- no crash (vs. 7,086 in the unmodified build)
81   0.202 ...  24999. ...   <- but flow keeps climbing, past the original peak
```

Flow does not settle near the pre-transition value; it keeps rising to a
**second, higher peak of 27,885 ft³/s at T=0.213 hr** before declining
(`outputs/analysis/lawn_pipe_weir_transition/LAWN_smoothing_enabled.stdout.txt`,
`OUTPUT SUMMARY`). Full comparison:

| | Unmodified (current repo) | Smoothing enabled (experiment) | Observed (`docs/LAWN_OBSERVED_REFERENCE_DATA.md`) |
|---|---|---|---|
| `QBP` | 21,562 cfs | **27,885 cfs** | 18,000 cfs (model estimate) |
| Error vs. observed | +19.8% | **+54.9%** | — |
| `BRW` (top width at peak flow) | 26.36 ft | 90.81 ft | 97 ft (final survey) |
| `BO` (bottom width at peak flow) | 26.36 ft | 27.10 ft | 55 ft (final survey) |
| `BRD` | 28.00 ft | 28.00 ft | 28 ft |
| `HY_final` | 7.32 ft | 5.81 ft | — |

**Conclusion: this is not adopted.** Removing the visual discontinuity comes
at the cost of nearly tripling the peak-discharge error against the one
observed benchmark available for this case (+19.8% → +54.9%). This is
consistent with — though does not prove — a plausible reason the original
1990-dated fix may have been deliberately left disabled rather than
accidentally forgotten: enabling it does not uniformly improve the model's
behavior, it trades one problem (a visible discontinuity) for a different,
arguably worse one (an unbounded-looking secondary overshoot) for at least
this test case. No claim is made about whether this holds for other inputs;
only `LAWN.DAT` was tested.

## 5. Does this affect the comparison numbers already reported?

No. `QBP` (21,562) and `BRW`/`BO` "at peak breach flow" (26.36/26.36) in
`docs/LAWN_MODEL_OBSERVATION_COMPARABILITY.md` are all read from row I=78,
**strictly before** this transition occurs (I=80). The discontinuity and this
experiment concern only the *shape* of the hydrograph after the peak, not
the summary values already compared.

## 6. Open question, recorded rather than guessed

Whether the model's specific transition dynamics (either the unmodified
sudden drop, or the enabled-smoothing overshoot) resembles what a real
piping dam's discharge does at the moment its pipe roof collapses cannot be
determined from the data available in this project. `docs/LAWN_OBSERVED_REFERENCE_DATA.md`
contains only a single peak-discharge estimate and final breach geometry for
the real 1982 event — no time-resolved (hydrograph-shape) field or model
data exists in any source read in this project to compare against either
version of the simulated curve shape. This is recorded as an unresolved gap,
not answered by assumption.
