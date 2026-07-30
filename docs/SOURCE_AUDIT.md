# SOURCE_AUDIT.md — NWS BREACH (1999) Static Analysis

## 1. Provenance and integrity

| File | SHA-256 | Lines | Bytes |
|---|---|---|---|
| `original/SRC/Breach.for` | `1bf7c6a5dde036846af0c98d0aa7fe9a22d44487340f6ef1c8aad6a45631253` | 1847 | 55973 |
| `original/Input/BSMBOT2.DAT` | `1a901eddac560fedb539cea15b1dc92ada90340ca33aa098faa12e329ab35ed` | – | 983 |
| `original/Input/CLAY.DAT` | `a0f84150c343ce13b3dcdc30bc965571b88e93ac305a140e5110d3e33973444` | – | 473 |
| `original/Input/LAWN.DAT` | `7db97aada2dc75ad3bce066a34842c294e9d931cf387ad49cbffcbefab13e67` | – | 543 |
| `original/Input/PERU.DAT` | `16101fd623d5d1d8cb3ccc36370d9f98a323923df2ad0cac399b2752863dc09` | – | 553 |
| `original/Input/TETON.DAT` | `344149a66483811b6d6ee613ab6db00a052954154d03fd9d5120067fa4c170e` | – | 1216 |

These files are byte-for-byte archived under `original/` and are never modified again after this commit. `src/breach1999_reference.f` is an identical copy used only to produce a reproducible baseline build (it compiled cleanly with no source edits needed).

No `BRREAD.ME`, BREACH technical report, "BRCH Input Summary", or RiverMechanics release notes files were present in the working directory. This audit and the change matrix in `CHANGE_MATRIX.md` are based on (a) reading `original/SRC/Breach.for` directly and (b) the BRCH 2010/2018 change descriptions supplied by the user in this session (translated summaries of RiverMechanics' public release notes). No RiverMechanics BRCH source code was obtained, viewed, or copied at any point.

## 2. Embedded 1987–1999 change history (preserved verbatim intent)

The original header (`original/SRC/Breach.for:1-61`) documents eleven rounds of changes by the original author/maintainers between 1987 and 1999:

| Date | Summary |
|---|---|
| 1987-05-13 | Fixed undefined `BC` at label 80; fixed undefined `NTD` (replaced with `NT`) |
| 1988-02-17 | Added `TFHI` (integrated Qb vs time) and `TFH` (simplified discharge eq.) outputs; fixed undefined output on piping→weir transition and slump failure |
| 1988-07-08 | Added clay transport via critical shear stress for clay dams; redefined `QBP,TFH,BRW,BO` outputs; allowed `BO` to grow during `KREG=1`; moved input reading into `RDDATA` |
| 1989-04-25 | Commented out statement #438; added statements after #598 and #872 |
| 1990-08-13 | Added upper limit to sediment/water concentration (`SEDCON`); corrected piping-height-above-bottom check near label 177 |
| 1991-03-13 | Corrected computation of `CL` and `DTH` when `KREG=3` |
| 1991-06-05 | Large revision: bottom width continues widening after reaching a landslide-dam bottom; adaptive time step during reservoir filling; automated time-step control based on erosion rate; submergence coefficient lag/suppressor; added `BTMX` (max breach top width) |
| 1993-08-05 | Removed time delay for pipe→weir transition; material over pipe drops to bottom at transition |
| 1997-09-23 | Set `TFH=0` when routing period too short |
| 1999-07-27 | Initialize `WB, HMP, DTHOLD`; reset `NHP` to actual point count; set tolerances for `TFH` |

This is the "NWS BREACH 1999" baseline referenced throughout this project — i.e. the version already carrying the 1999-07-27 patch, not the original 1988 release.

## 3. Program structure

Single translation unit, fixed-form FORTRAN 77 (`.for`), no `INCLUDE` files, no modules.

### MAIN program (unnamed, `original/SRC/Breach.for:1-1380`)
- Opens `in.dat` on unit 5 (`OPEN(5,FILE='in.dat')`), writes all report output to unit 6 (default stdout — no `OPEN` for unit 6), writes a one-line version banner to unit 0 (stderr) at line 168.
- Calls `RDDATA` once, then runs the explicit time-stepping erosion loop (labels 22…120), then prints the summary block and hydrograph plot, then `STOP`.

### Subroutines / functions (no FUNCTIONs; all SUBROUTINEs)

| Name | Lines | Purpose |
|---|---|---|
| `RDDATA` | 1547–1688 | Reads all fixed-format (`8F10.2`) input records from unit 5; derives `NHP` (inflow points), `NSPH` (spillway rating points), `ASTW` (cross-section area table), `SEDCON`/`SWRM`, and applies several "if unset, use default" fallbacks (`BR`, `DTH`, `H`, `UNFCC`, `BMX`, `ERR`, …). |
| `GRASSN` | 1381–1432 | Grass-cover erosion resistance coefficient (Manning's n proxy) as a function of grass length/condition and unit discharge, for the "no erosion yet" check on the downstream face. |
| `INTPPL` | 1433–1443 | Linear interpolation on the *plotting* time array `TT(5000)` (used only when building the final hydrograph plot). |
| `INTPS` | 1444–1458 | Linear interpolation of reservoir surface area `RSA` vs elevation `HSA`. **Hardcodes loop bound 8** regardless of how many `(RSA,HSA)` pairs were actually supplied — see `CHANGE_MATRIX.md` BRCH2018-01. |
| `INTPSP` | 1459–1471 | Linear interpolation of spillway rating `SPQ` vs `SPH`, already correctly bounded by `NSPH` (computed in `RDDATA`). |
| `INTPT` | 1472–1482 | Linear interpolation of inflow hydrograph `QIN` vs `TIN`, correctly bounded by `NHP`. |
| `PLOT` | 1483–1546 | ASCII line-printer plot of the outflow hydrograph (the ASA carriage-control style page/column plot seen in program output). |
| `RECT` | 1689–1706 | Rectangular breach channel hydraulics (Manning's eq., normal depth) — used when `KREC=1`. |
| `SHIELD` | 1707–1721 | Shields critical shear stress / mobility parameter for the breach channel bed material. |
| `SLUMP` | 1722–1773 | Side-slope slump/mass-failure timing and angle progression (three-stage angle model `TH1/TH2/TH3`, `H1/H2/H3`). |
| `TRAP` | 1774–1819 | Trapezoidal breach channel hydraulics (bisection solve for normal depth) — used when `KREC=0`. |
| `TWSEC` | 1820–1838 | Tailwater channel cross-section properties (area, top width, Manning's n) vs stage `Y`, from `HSTW/BSTW/ASTW/CMTW` tables. **Hardcodes loop bound 8**, using an `HSTW(K)<0.01` sentinel to detect the true table size — see `CHANGE_MATRIX.md` BRCH2018-02. |
| `WEIR` | 1839–1847 | Broad-crested rectangular + triangular (side-slope) weir discharge for the open breach channel. |

### Call graph (top level)

```
MAIN
 ├─ RDDATA                     (once, at start)
 ├─ INTPSP, INTPS, INTPT       (every iteration — table lookups)
 ├─ SLUMP                      (every iteration while KREG∈{1,2,3} eroding)
 ├─ GRASSN                     (pre-failure, downstream-face check)
 ├─ RECT | TRAP                (breach channel geometry, per KREC flag)
 ├─ SHIELD                     (critical shear, feeds sediment transport)
 ├─ WEIR                       (open-channel breach discharge)
 ├─ TWSEC                      (tailwater rating, inside submergence block)
 ├─ INTPPL                     (post-loop, hydrograph resampling for plot)
 └─ PLOT                       (post-loop, final ASCII hydrograph)
```

## 4. Functional area map (line ranges, `original/SRC/Breach.for`)

| Area | Lines | Notes |
|---|---|---|
| Input processing | 1547–1688 (`RDDATA`) | Fixed `8F10.2` records; see `VARIABLE_DICTIONARY.md` for field order. |
| Reservoir (pool) tracking | 718–758 (`HY`, water balance `DY`), 384–397 (fill-phase time step `DTHFIL`) | Mass balance: `DY ∝ (inflow − outflow)·Δt / surface area`. |
| Spillway flow | 253–254, 744–746 (`QSP` via `SPQ/SPH`), 750–754 (`QT`, uncontrolled overflow of dam crest via `CRES`) | Two separate spillway/overflow paths. |
| Breach discharge (weir/open-channel) | 809–817 (`CALL WEIR`), 870–871 (`RECT`/`TRAP` geometry) | |
| Breach discharge (piping/orifice) | 658–667 (piping mode entry, `KREG=4`), 762–808 (orifice head/flow eq.) | `HEAD=HY-PCC`, with `PCC` possibly overridden by `TWD` — direct point where tailwater elevation enters a `SQRT(HEAD)` computation. |
| Sediment transport (non-cohesive) | 873–910 | Shields-based transport capacity, `AQS` coefficient, upper limit via `SWRM`. |
| Cohesive erosion | 340–360 (`CDS/CDA/CDC`, `H1/H2/H3`, slump-angle geometry), 876–878 (`CRSHR` via `CA,CB,PI` power law for high-plasticity clay) | |
| Piping | 405–408, 658–667, 762–808, 841–852 | Piping-specific geometry `PL`, `PLC`, expansion after collapse `QEXP/DQP`. |
| Pipe-to-weir transition | 1124–1210 (label 99–105, "TRANSITION FROM ORIFICE TO WEIR FLOW") | Recomputes `HCP`, `WC`, `TDEL/TDELC`, resets `KPIP=0, KPT=1`. |
| Slump / slope failure | 620–648, 680–712 (calls into `SLUMP`), 1211–1266 (deep-seated collapse check, `KREG=5`) | Three-stage angle model. |
| Tailwater & submergence | 1281–1301 (`TWSEC` rating loop, `SUB`/`CV` correction), 787–807 (`TWD` inside piping `HEAD`) | See BRCH2010-01/02 and BRCH2018-04/U03. |
| Adaptive time step | 384–397 (`DTHFIL`, fill phase), 998–1088 (main adaptive `DTH` logic, convergence retry at 955–974) | See BRCH2018-05. |
| Output processing | 943–951, 977–985 (debug rows), 1333–1378 (summary block + hydrograph plot) | |
| Program termination | 423 (`IF(T.GT.TMAX) GO TO 120`), 1268–1277 (`KREG=3` low-flow cutoff, `I.GE.4999`, `T.GT.TEH`), 759 (`HY.LT.HL+1.` → terminate) | Multiple independent exit conditions converge on label 120. |

## 5. Compiler diagnostics (reference build)

`gfortran -std=legacy -ffixed-form -O0 -fno-range-check` on the unmodified source: **zero errors, zero warnings.**

`gfortran -std=legacy -ffixed-form -O0 -Wall -Wextra -Wconversion -fcheck=all -fbacktrace -ffpe-trap=invalid,zero,overflow` diagnostics are classified in `CHANGE_MATRIX.md` / `BRCH2018-07`; see that document for the full list and the "old syntax vs stability vs cosmetic" triage.
