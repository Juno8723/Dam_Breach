# UNRESOLVED_BRCH2018.md

Items where the public BRCH 2010/2018 release descriptions available in this session did not provide enough detail to implement with confidence, or where this session's testing coverage has a known gap. Nothing here was guessed at in `src/breach1999_documented_corrections.f` — original 1999 behavior is preserved for all of it unless noted.

## BRCH2018-U01: `PPP`/`HP` after piping collapse

**What's documented:** After a piping-induced collapse (`KREG=5`), the breach length `PPP` and breach depth `HP` had "an error" in the original code; RiverMechanics' fix made these more accurate but changed peak outflow only slightly.

**What we found by reading the code:**
- `PPP` and `HP` are heavily overloaded across `KREG` values (see `VARIABLE_DICTIONARY.md`): depth eroded (`KREG=1`), vertical erosion (`KREG=2`), Δwidth (`KREG=3`), pipe-top elevation (`KREG=4`).
- During/after collapse (`KREG=5`, set at `original/SRC/Breach.for:1253` in the 1999 source), the code path falls through to the `KREG` branches above rather than assigning `PPP`/`HP` freshly for the collapsed geometry — e.g. at label 44 (`IF(KREG.EQ.2.AND.KPT.EQ.0) HP=HV`, `PPP=CL`) which was written for the pre-collapse upstream-face-erosion case, not explicitly for post-collapse geometry.
- At least two plausible interpretations exist for "the error":
  1. `PPP`/`HP` should be recomputed relative to the *new* post-collapse `HC` (`HC=HC1=HC-YC`, set at the collapse block) rather than inheriting values computed against the pre-collapse geometry.
  2. `PPP`/`HP` should use the *collapsed* `WC` (`WC=WCC+ZUD*YC`, also set at the collapse block) in the length/width sense rather than whatever `CL`/`HV` carries over from the prior `KREG`.
- Both changes are plausible, would touch the same few lines, and would produce different (if reportedly small) shifts in peak outflow — exactly the ambiguity the task asked us not to resolve by guessing.

**Decision:** Not implemented. Original computation preserved unchanged. Confirming which interpretation (if either) matches RiverMechanics' actual fix would require either their source or a documented before/after numeric example for a collapse-triggering case, neither of which is available here.

## BRCH2018-U02: reservoir refill below breach bottom

**Implemented (conservative, independent):** see `CHANGE_MATRIX.md` — breach outflow (`QB`) is forced to 0 whenever `HY < HC` (pool below the controlling breach-bottom elevation), while inflow/spillway/mass-balance terms continue to update `HY` every iteration, and breach geometry (`BO`, `BT`, `HC`) is left untouched so flow can resume once `HY` rises back above `HC`.

**Known test gap:** none of the 5 provided example datasets naturally drive `HY` below `HC` and then back above it within the simulation window (their inflow hydrographs are single-pulse), so the fix shows zero regression on all 5 — expected, but not a positive demonstration of refill actually re-triggering breach flow. A hand-constructed two-pulse synthetic input was not completed in this session because reliably driving this specific state (drain below `HC`, then refill above it) without destabilizing the erosion/slump sub-models needs more trial-and-error than was practical here. This should be treated as **unverified beyond code-level reasoning and zero-regression confirmation**, not as a positive test pass.

**What we did not attempt:** re-triggering/geometry rules beyond "leave everything alone except `QB`" — e.g. whether `KREG` should reset, whether slump timers (`TDEL`/`TDELC`) should reset, whether the breach should behave like "a newly formed dam" in some more literal sense (re-running the initial grass-erosion/threshold-velocity check, for instance). The release note's phrase "acts like a newly formed dam" could mean any of these; we chose the most conservative reading (nothing resets, only outflow gates).

## BRCH2018-U03 / BRCH2018-04(a): tailwater "enhanced under all conditions"

**Implemented from this family:**
- BRCH2010-01 (tailwater ≥ pool ⇒ `QB=0`, applied at both the piping-orifice `HEAD` calc and the weir-path `SUB`/`CV` calc)
- BRCH2010-02 (`TWD` initialized to `HSTW(1)`, an elevation, not `0`)
- BRCH2018-02 (`NCS`-bounded `TWSEC`, explicit table-size handling for the tailwater rating curve)

**Not implemented:** computing a tailwater elevation *during active reservoir filling* (`NFIL=1`) when spillway flow exists. In the 1999 source, `TWSEC` is never called at all while `NFIL=1` — the fill-phase branch (`original/SRC/Breach.for:327-397`) has no tailwater-rating-curve call anywhere. The release text ("tailwater algorithm under all conditions was enhanced") is the *only* description available for this; it doesn't specify a formula, a call site, or how the fill-phase inflow/spillway/tailwater interaction should work. Inventing that formula would be exactly the kind of guess the task instructions prohibit. None of the 5 example datasets have `HSP` (spillway crest) low enough to produce spillway flow during their fill phase, so this gap has no observable effect on any provided example either way.

## BRCH2018-07: gfortran compatibility / initialization audit

**Done:**
- Full compile with `-Wall -Wextra -Wconversion -fcheck=all -fbacktrace -ffpe-trap=invalid,zero,overflow`; 32 warnings, 0 errors (`bin/breach1999_debug.diagnostics.txt`), all either `-Wunused-label` (15, dead labels from prior 1987-1999 edits, e.g. label 439, 998, 999 — harmless) or `-Wconversion` (17, intentional truncating real→integer assignments like `NTD=DELT/DTH+1`, a deliberate F77 idiom throughout, not a bug).
- Found and fixed one genuine "read effectively uninitialized" case: `AFR` used in the pre-loop `WRITE(6,402)` before its first real assignment (BRCH2018-06).
- Confirmed (and left alone, documented in `CHANGE_MATRIX.md`'s diagnostic-note section) that `SUBROUTINE PLOT`'s `DIMENSION Q(1),T(1)` is a standard F77 size-agnostic-dummy idiom that only `-fcheck=all` misflags; not a real bug, not touched.

**Not done:** a full variable-by-variable "used before assigned" certification across all ~1900 lines and every `KREG`/`KNAT`/`KPIP` branch combination. This would require either symbolic/dataflow tooling beyond what's practical to build in this session, or manually tracing every branch — given the size of the state space (dozens of flags interacting), we did not attempt exhaustive manual coverage beyond what static compiler diagnostics plus direct reading surfaced. Any additional uninitialized-variable bugs beyond the ones already found (`AFR`) are **not ruled out** by this audit.

## Metric option

**Not implemented.** The 2018 release describes the *architecture* (metric input → English-unit conversion → English internal computation → metric output) but the 1999 source has **no unit flag, no conversion routine, and no metric-related field anywhere** in its input format. Implementing this would require guessing an input-file convention (where the unit flag lives, what value(s) select metric vs. English, which fields if any change meaning) that RiverMechanics never published in the material available to this session. Per the task's own instructions, this is deferred rather than guessed. If real BRCH 2010/2018 input-file documentation (an "Input Summary" describing the metric flag's field position) becomes available, this can be implemented as a dedicated, isolated pre/post-processing layer (convert on read, convert on write, no change to the English-unit internal computation) without touching any of the corrections already applied.
