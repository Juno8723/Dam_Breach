# PYTHON_PORT_READINESS.md

**No Python code was written for this assessment — this is a readiness evaluation only, per this task's explicit scope limit.**

## 1. Structural inventory

### MAIN loop boundaries

Single unstructured MAIN program (`original/SRC/Breach.for:1-1380` in the original numbering; grown by documented-correction comments in `src/breach1999_documented_corrections.f`), no internal procedure boundaries within it. The "loop" is a single labeled block (`22 T=T+DTH ... GO TO 22`, exit only via six independent `GO TO 120` sites) — there is no `DO`-loop structure to the outer time-stepping at all; it's entirely `GOTO`-driven. This is the single largest port risk (see §5).

### Input parsing dependencies

`SUBROUTINE RDDATA` reads a **fixed-column, position-dependent** file (`8F10.2` throughout, `20A4` for the title) with no delimiters and no field names — every downstream calculation implicitly depends on the exact field order and column width documented in `docs/VARIABLE_DICTIONARY.md`. A Python port's input layer needs to either (a) replicate this exact fixed-width parsing (straightforward, `struct`-like slicing) or (b) define a new, richer input format and provide a converter — but *not* silently reinterpret the existing `.DAT` files with a different parser, since several of this project's own bug-fixes (`NHSA`, `NCS`) depend on this exact fixed-width, blank-padded convention (see `docs/CHANGE_MATRIX.md` BRCH2018-01/02).

### COMMON blocks / global state

11 named `COMMON` blocks (`CRD10`–`CRD14`, `CSTW`, `EL`, `INT`, `INTPL`, `RES`, `SLMP`, `CNSPH`, plus this project's added `CNHSA`/`CNCS`) share state between MAIN and 10 subroutines. None are read-only from a subroutine's perspective — e.g. `SLUMP` both reads and writes `COMMON/SLMP/`. A Python port should replace these with either a single mutable state object/dataclass passed explicitly, or (cleaner) split into the smaller logical groupings the `COMMON` names already suggest (reservoir/inflow state, cross-section tables, cohesive/noncohesive material properties, slump-angle state). The *existing* `COMMON` grouping is a reasonable starting decomposition — don't invent a different one without reviewing why each variable is grouped where it is.

### GOTO and computed GOTO

Extensive unstructured `GOTO` (no computed/assigned `GOTO` was found — all are literal numeric-label `GOTO`s). Roughly 150+ `GOTO` statements in MAIN alone. Several serve as **loop constructs** (the convergence retry loop `GO TO 25`, the tailwater rating-curve search `GO TO 77`, the outer time loop `GO TO 22`) and would translate to `while`/`for` loops relatively directly; others implement **branch dispatch** on `KREG` (effectively an unstructured `switch`) and would translate to `if`/`elif` chains; a few (e.g. jumping into the middle of the piping-vs-weir dispatch depending on `KPIP`) are genuinely tangled control flow that will need careful, tested-step-by-step translation, not a mechanical rewrite.

### State variables

`KREG` (five-way plus fill/collapse: 1-5, and the printed `KG`/`KRP` display which folds in `NFIL`), `KNAT`, `KPIP`, `KPT`, `KCOL`, `KSLUMP`/`KSLMPC`, `NFIL`, `NFAIL`, `IFIL` — a genuine finite-state-machine, but implemented as loosely-coupled integer flags rather than an explicit state enum, and several combinations are checked ad hoc (`IF(KREG.EQ.1.AND.NFIL.EQ.0.AND.NFAIL.EQ.1)`) rather than through a single dispatch point. `docs/STATE_TRANSITION_DIAGNOSTIC.md` (this project) documents the transitions actually observed across all 5 examples plus 3 targeted tests — useful as a starting spec for a Python state-machine class, but not proven exhaustive (see its own coverage gaps, e.g. `KREG=5` collapse and slump state were never observed).

### Arrays and table dimensions

All hardcoded to size 8 (`RSA`, `HSA`, `BSTW`, `HSTW`, `CMTW`, `TIN`, `QIN`, `SPQ`, `SPH`) except the internal time-series buffers (`TT`, `QSAV`, `QBS`, `TPL`, `QPL` at size 5000, with a hard `I≥4999` termination). A Python port should use dynamically-sized arrays/lists for the input tables (this project's `NHSA`/`NCS` fix already establishes "actual count, not hardcoded 8" as the correct semantic — carry that forward rather than reintroducing a fixed cap) and either a dynamic list or a documented, generous fixed cap for the time-series buffers.

### Units

Feet, hours, cfs, acres throughout (confirmed via `docs/MASS_BALANCE_DIAGNOSTIC.md`'s unit audit); no internal SI. The undocumented Metric I/O option (`docs/UNRESOLVED_BRCH2018.md`) would need to be a pure input/output conversion layer around this same internal unit system, not a rewrite of the internal units.

### Numerical precision

Single-precision `REAL` throughout (`docs/VALIDATION_REPORT.md` §1). A Python port using native `float` (double precision) will **not** reproduce this Fortran build's output bit-for-bit, and should not be expected to — see the tolerance discussion in `docs/VALIDATION_REPORT.md`'s "Recommended tolerance for a future Python port" section. This is a deliberate, informed choice point, not an oversight: decide explicitly whether the port targets bit-for-bit legacy reproduction (would need `numpy.float32` throughout) or improved numerical fidelity (native `float`, expect small legitimate divergence from this Fortran build, especially in the same threshold-crossing-sensitive spots documented in `docs/TIMESTEP_CONVERGENCE.md` and `docs/BSMBOT2_FIX_ATTRIBUTION.md`).

### File I/O coupling

Original: `OPEN(5,FILE='in.dat')` (hardcoded filename, no CLI argument), writes to stdout (unit 6) and one stderr line (unit 0). This project's diagnostic builds add two more hardcoded-filename outputs (`mass_balance.csv`, `state_transitions.csv`) behind compile-time flags. A Python port should make all of these explicit function parameters / return values rather than hardcoded paths — but the *default* filenames are a reasonable backward-compatible CLI default.

### Plotting subroutine dependencies

`SUBROUTINE PLOT` (ASCII line-printer hydrograph plot) is self-contained, reads no `COMMON` state, and is the **safest, lowest-risk module to port first or drop entirely** (a Python port would more naturally use `matplotlib`/similar — see `tools/plot_bsmbot2_attribution.py` and `tools/plot_timestep_convergence.py` in this project for the equivalent modern approach already used for analysis). Its one gotcha: the `DIMENSION Q(1),T(1)` F77 idiom (`docs/CHANGE_MATRIX.md` diagnostic note) — a Python port trivially avoids this by using properly-sized arrays/lists, no equivalent bug is possible.

### Deterministic behavior

Confirmed deterministic (bit-for-bit reproducible across repeated runs and fresh rebuilds) for all 5 real examples and the corrected build generally — **except** the specific uninitialized-variable bug documented in `docs/NEGATIVE_BMX_DIAGNOSTIC.md` (fixed in this project's corrected source; the *original* 1999 source is confirmed non-deterministic under the negative-`BMX` condition). A Python port starting from a clean state (no manually-managed static/uninitialized variables — Python doesn't have Fortran's implicit-static-storage default) should not be able to reproduce that specific class of bug at all, which is worth calling out as a genuine advantage of porting, not just a stylistic one.

### Reference output completeness

`outputs/baseline/` (5 examples), `outputs/corrected/` (5 examples), `outputs/targeted/` (4 synthetic edge cases), `outputs/analysis/` (attribution, convergence, mass-balance, state-transition data) together give substantial regression coverage for a port to check itself against — but `docs/TEST_COVERAGE_MATRIX.md` documents real gaps (spillway flow, pipe roof collapse, slump failure, isolated cohesive-vs-noncohesive erosion, a genuine post-breach depletion-refill cycle) that a port effort should either accept as un-validated or invest in closing *before* trusting a port's behavior in those code paths.

## 2. Porting order recommendation

**Port first (low risk, self-contained, already has a natural Python-native alternative):**
- `PLOT` → replace with `matplotlib`, don't literally translate.
- `SHIELD`, `WEIR`, `GRASSN` — pure functions, no `COMMON` state, small, already well-understood from this project's `docs/SOURCE_AUDIT.md`.
- `tools/parse_breach_output.py` and `tools/compute_release_volume.py` (already Python, already validated against this Fortran build's actual output format across hundreds of runs in this project) — reusable as-is for any port's regression harness.

**Port with care (moderate risk, `COMMON`-coupled but logically bounded):**
- `RECT`, `TRAP` (channel hydraulics, `COMMON`-free, but feed into and are fed by MAIN's larger state).
- `TWSEC`, `INTPS`/`INTPT`/`INTPSP`/`INTPPL` (table interpolation) — straightforward once the input-table data model is decided, but this project's `NHSA`/`NCS` fixes changed exactly this code, so a port must carry forward the *fixed* interpolation logic (`docs/CHANGE_MATRIX.md` BRCH2018-01/02), not the original hardcoded-8 version.
- `SLUMP` — moderate `COMMON` coupling (`COMMON/SLMP/`), self-contained algorithm, but never observed triggering in any of this project's test runs (`docs/TEST_COVERAGE_MATRIX.md`), so a port would have **no regression data to validate against** without first constructing a slump-triggering test case.

**Highest risk (port last, needs the most hand-verification):**
- **MAIN's outer time-stepping and `KREG` dispatch logic.** This is where nearly all of this project's real bugs were found (`AFR`/`AFRA`, `QBP`/`BOS`/`BTS`/`ZS`/`TFHI` uninitialized-read, the tailwater/`DTHFIL` fixes) — precisely because it's the most tangled, `GOTO`-heavy, `COMMON`-coupled part of the program. A mechanical line-by-line translation risks reproducing subtle control-flow bugs in a new language where they'll be *harder* to spot (Python's implicit variable creation on first assignment means a Python port could silently mask what would be an "uninitialized variable" bug in Fortran, or conversely raise a `NameError` where Fortran silently used garbage — both are behavior changes from this project's corrected Fortran that need deliberate, tested decisions, not a straight transliteration).
- The piping ↔ weir-flow transition block (label 99-105 range) and the deep-seated collapse block (`KREG=5`) — both control-flow-dense and, per `docs/TEST_COVERAGE_MATRIX.md`, the collapse path specifically has **zero test coverage** in this project, meaning a port of that block would ship unverified.

## 3. Legacy-compatible mode vs. documented-corrected mode

A Python port should decide early whether it offers:
- **A legacy-compatible mode** reproducing `original/SRC/Breach.for`'s behavior including its known bugs (useful for validating the port itself against 40 years of prior BREACH usage/publications), requiring the port to *deliberately* reintroduce e.g. the uninitialized-`QBP` behavior or the `DTHFIL` degenerate-formula bug behind an explicit flag — not by accident.
- **A documented-corrected mode** matching `src/breach1999_documented_corrections.f` (recommended default), which is what this project's `outputs/corrected/` regression data validates against directly.

Both modes are valuable to offer (a `--legacy`/`--corrected` flag, mirroring how `tests/compare_outputs.py` keeps a `--tol` legacy mode alongside its new default) — but they must not be silently blended; every one of this project's documented fixes should be an identifiable, toggleable unit in the port, the same way each is an identifiable, isolated `C BRCH20xx-DOCFIX-NN` comment block in the Fortran source now.

## 4. Blockers to resolve before (or explicitly defer during) a Python port

1. **Metric unit option**: still `INSUFFICIENT_INFORMATION` (`docs/UNRESOLVED_BRCH2018.md`) — a port can't implement what isn't documented; defer or design fresh.
2. **`PPP`/`HP` post-collapse ambiguity** (`docs/UNRESOLVED_BRCH2018.md` BRCH2018-U01): two plausible interpretations, neither confirmed. A port must pick one and document the choice, or preserve the original's (also arguably wrong) behavior explicitly.
3. **Reservoir depletion-refill**: this project's own conservative implementation was never validated end-to-end (`docs/RESERVOIR_REFILL_TEST.md`) — a port inherits the same unresolved validation gap, not a solved problem to copy confidently.
4. **No official BRCH 2.0.0 comparison ever performed**, at any point in this project (see this and the prior session's final reports) — a port validated only against `outputs/corrected/` inherits the same "independently corrected, not RiverMechanics-verified" status, and should say so as clearly as this project does.

## 5. What a Python port should compare its output against, and how

- Every `outputs/baseline/*.parsed.json` and `outputs/corrected/*.parsed.json` (summary fields + `KREG` transitions) — direct target for a legacy-mode / corrected-mode port respectively.
- `outputs/analysis/timestep_convergence.csv`, `mass_balance_summary.csv`, `bsmbot2_attribution/*.parsed.json` — secondary validation that a port's *numerical behavior under parameter variation* matches, not just its output for the default parameters.
- `tools/parse_breach_output.py` and `tests/compare_outputs.py` (this project's variable-specific-tolerance version) are directly reusable as the port's regression harness without modification — point them at the port's output (once it's shaped into the same `stdout` format, or adapt the parser to the port's native output format) instead of rewriting comparison logic from scratch.

## 6. Readiness verdict

See the final report for `READY_FOR_PYTHON_PORT` / `READY_WITH_MINOR_GAPS` / `NOT_READY_FOR_PYTHON_PORT` and the reasoning — summarized here: the Fortran corrected source, its documentation, and its regression data are in good enough shape to **start** a port (structure is well-understood and documented, most bugs found so far are fixed, build/test tooling is reusable), but real, identified gaps remain (`KREG=5` collapse, slump failure, spillway flow, the refill cycle, `PPP`/`HP` ambiguity) that a port would inherit as unvalidated rather than solved.
