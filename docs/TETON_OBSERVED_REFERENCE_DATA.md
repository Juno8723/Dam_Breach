# TETON_OBSERVED_REFERENCE_DATA.md

**Purpose and scope.** This document collects *only* externally sourced, official
observational/reported data on the actual 1976 Teton Dam failure, for future
comparison against this project's model output. **No comparison to the model's
output is made in this document** (per task instructions) — that is deferred to a
future step. **No code or input file in this repository was modified to produce
this document.**

**Priority sources actually used, and what could not be obtained:**

1. **U.S. Bureau of Reclamation — primary/official investigation reports (used):**
   - *Report to U.S. Department of the Interior and State of Idaho on Failure of
     Teton Dam*, by the **Independent Panel to Review Cause of Teton Dam Failure**
     (Wallace L. Chadwick, Chairman), Idaho Falls, Idaho, **December 1976**. Retrieved
     directly as a PDF from the Bureau of Reclamation's own site:
     `https://www.usbr.gov/pn/snakeriver/dams/uppersnake/teton/1976failure.pdf`
     (590 pages; combined report + appendices). Cited below as **"Independent Panel
     (1976)"**, with the PDF page number of that specific file.
   - *Failure of Teton Dam — A Report of Findings*, by the **U.S. Department of the
     Interior, Teton Dam Failure Review Group** (F. William Eikenberry, Chairman),
     **April 1977**. This is the Bureau of Reclamation's own internal review, a
     separate document from the Independent Panel report above. Retrieved as a full
     scanned/OCR text from the Internet Archive (a library-deposited U.S. Government
     Printing Office copy, not a blog or a summary site):
     `https://archive.org/details/failureoftetonda00teto`. Cited below as **"BOR
     Report of Findings (1977)"**, with the report's own printed page numbers
     (visible in the OCR text) where available.
2. **USGS official reports (partially used):**
   - The USGS's own dedicated hydrologic report on this event — Ray, H.A., Kjelstrom,
     L.C., Crosthwaite, E.G., and Low, W.H., *The flood in southeastern Idaho from the
     Teton Dam failure of June 5, 1976*, U.S. Geological Survey Open-File Report
     77-765 (1978) — is the report most likely to contain the primary, directly
     measured/estimated **peak breach outflow** figure. **Its full text could not be
     retrieved in this session**: the USGS Publications Warehouse page
     (`https://pubs.usgs.gov/publication/ofr77765`) explicitly states no digital
     version is linked, and no working PDF URL could be found. **This is recorded as
     a data-access gap, not filled by guessing.**
   - A different, directly retrieved USGS report — Scott, W.E., *Geologic Effects of
     Flooding From Teton Dam Failure, Southeastern Idaho*, U.S. Geological Survey
     Open-File Report 77-507 (1977), `https://pubs.usgs.gov/of/1977/0507/report.pdf`
     — **quotes** the peak-discharge figure from the above unavailable Ray & Kjelstrom
     report. This is used below, explicitly labeled as a **secondary citation chain**
     (an official USGS report quoting another official USGS report), not as a
     first-hand reading of OFR 77-765 itself.
3. **Other federal-agency/academic corroboration (used only as corroboration, never
   as the sole source for a number):**
   - Ostrander, C., et al., *Simulating the 1976 Teton Dam Failure using GeoClaw and
     HEC-RAS and comparing with Historical Observations*, arXiv:2206.00766 (2022),
     `https://arxiv.org/pdf/2206.00766`. Its Table 2 ("Historical data for downstream
     locations...") is explicitly sourced by that paper to "Reclamation, 1976; USGS,
     1976" and is used **only to corroborate** (independently reproduce) the same
     peak-discharge figure obtained from Scott (1977) above, and to add a
     downstream-arrival clock time. Where this paper's *own* modeling assumptions
     (e.g., its HEC-RAS breach-geometry calibration) are not themselves a cited
     historical measurement, they are explicitly **excluded** from the tables below
     (see the breach-width/depth section).
   - No blog posts, dam-safety-association summaries, Wikipedia, or similar
     unsourced/secondary-summary pages were used as a source for any numeric value
     in this document, per task instructions.

---

## 1. Estimated peak breach outflow

| Field | Value |
|---|---|
| Value | **65,000 m³/s ≈ 2.3 × 10⁶ cfs (2,300,000 cfs)** |
| Single value or range | Single value ("indirectly estimated") |
| Observed or post-hoc estimate | **Post-hoc estimate** — explicitly described by the citing source as "indirectly estimated," i.e., back-calculated (almost certainly via slope-area / high-water-mark indirect discharge measurement, standard USGS practice for flows too large/dangerous to gauge directly), not a direct streamgage reading |
| Exact definition and reference point | Peak **flood discharge** in a river cross-section **about 4 km (2.5 mi) downstream of the dam**, in the canyon below the damsite. **This is downstream-channel peak discharge, not necessarily identical to peak flow at the breach face itself** — some attenuation/translation between the breach and this cross-section is physically expected over 2.5 mi of canyon, though the source does not quantify it |
| Source | Scott, W.E. (1977), *Geologic Effects of Flooding From Teton Dam Failure, Southeastern Idaho*, USGS Open-File Report 77-507, p. 3 (PDF p. 5 of `pubs.usgs.gov/of/1977/0507/report.pdf`) — quoting: *"Flood discharge in a cross section about 4 km (2.5 mi) below the dam was indirectly estimated at 65,000 m³/sec (2.3 × 10⁶ cfs) (Ray and Kjelstrom, 1977)."* **Original citation is to Ray, H.A. and Kjelstrom, L.C. (1977), USGS Open-File Report [77-765 draft]** — not independently verified in this session (see access-gap note above) |
| Corroboration (not an independent source) | arXiv:2206.00766, Table 2: "Teton Canyon, 4 km, arrival 12:05, Peak Flow 65,129 m³/s" — same order of magnitude and same location, sourced by that paper to "Reclamation, 1976; USGS, 1976" |

**A second, farther-downstream data point** (included because it clarifies that "peak breach outflow" and "peak flow at a fixed downstream gauge" are different quantities that decay with distance):

| Field | Value |
|---|---|
| Value | **30,000 m³/s ≈ 1 × 10⁶ cfs (1,000,000 cfs)** |
| Single value or range | Single value |
| Observed or post-hoc estimate | Post-hoc estimate (same indirect-estimation source) |
| Exact definition and reference point | Flood discharge at the **Teton–Wilford–St. Anthony road** crossing, roughly 13 km (8 mi) downstream of the dam |
| Source | Scott (1977), USGS OFR 77-507, p. 8 (PDF p. 10), quoting Ray and Kjelstrom (1977) |

**No value for peak discharge *at the breach itself* (i.e., at the dam face, distance = 0) was found in any source read in this session.**

---

## 2. Peak-flow / breach-progression chronology

All times below are Mountain Standard/Daylight Time, June 5, 1976, as reported (both source documents note times are approximate, reconstructed from eyewitness testimony and photograph timestamps).

| Time | Event | Source |
|---|---|---|
| June 3, 1976 | Two small seeps noted 1,300–1,500 ft downstream of the dam toe (right abutment), 40 and 60 gpm | BOR Report of Findings (1977), Table 1 ("Chronology of Significant Happenings..."), p. 46 |
| June 4, 1976 | One small seep noted 160–200 ft downstream of toe, 20 gpm | BOR Report of Findings (1977), Table 1, p. 46 |
| 7:00 a.m. | Slightly turbid leakage first noted near El. 5200 (right abutment) | BOR Report of Findings (1977), Table 1, p. 46 |
| 7:30–8:00 a.m. | Turbid leakage first noted at El. 5045 (right abutment) | BOR Report of Findings (1977), Table 1, p. 46 |
| 8:30 a.m. | Leakage at El. 5045 estimated at 20–30 cfs | BOR Report of Findings (1977), Table 1, p. 46; corroborated in Independent Panel (1976), PDF p. 46 |
| 9:10 a.m. | Leakage at El. 5200 estimated at 2 cfs; erosion noted along embankment–abutment contact | BOR Report of Findings (1977), Table 1, p. 46 |
| 9:20 a.m. | Leakage at El. 5045 estimated at 40–50 cfs | BOR Report of Findings (1977), Table 1, p. 46 |
| 10:15 a.m. | Wet spot at El. 5200 begins to leak and erode embankment rapidly | BOR Report of Findings (1977), Table 1, p. 47 |
| 10:30 a.m. | Loud noise heard by on-site personnel | BOR Report of Findings (1977), Table 1, p. 47 |
| 10:40 a.m. | Two dozers begin pushing material into the El. 5200 hole | BOR Report of Findings (1977), Table 1, p. 47 |
| 10:43 a.m. | County sheriff notified; downstream evacuation ordered | BOR Report of Findings (1977), Table 1, p. 47 |
| 11:00 a.m. | Whirlpool develops in the reservoir near the dam face | BOR Report of Findings (1977), Table 1, p. 47 |
| 11:10 a.m. | Dozer becomes stuck at the edge of the downstream hole | BOR Report of Findings (1977), Table 1, p. 47 |
| 11:30 a.m. | Dozers slide into the downstream hole | BOR Report of Findings (1977), Table 1, p. 47; Independent Panel (1976), PDF p. 46 |
| 11:40–11:50 a.m. | Sinkhole forms near Sta. 14+00, El. 5315 | BOR Report of Findings (1977), Table 1, p. 47; text, p. 41 |
| 11:45 a.m. | Dozers on top of the dam withdrawn | BOR Report of Findings (1977), Table 1, p. 47 |
| **11:55 a.m.** | **Embankment crest collapses** | BOR Report of Findings (1977), Table 1, p. 47, text p. 41 ("The embankment crest collapsed at 11:55 a.m."); Independent Panel (1976), PDF p. 50, Fig. 2-14 caption: "Dam crest breaching. 11:55 a.m." |
| **11:57 a.m.** | **Dam breached** | BOR Report of Findings (1977), Table 1, p. 47, text p. 41 ("...and the dam was breached at 11:57 a.m."); corroborated by multiple sworn eyewitness statements in Independent Panel (1976) Appendix C converging on 11:55–11:58 a.m. (e.g., PDF pp. 391, 445, 449, 452, 454 in that combined file) |
| 11:47 a.m. (± instrumental) | Independent seismographic confirmation: regional seismic network began recording ground motion "within 1 minute of 11:47 a.m. MDT," attributed to the physical breakup of the dam and release of reservoir water; amplitude peaked within ~30 min and continued ~1 hour, with detectable motion for at least 4.5 hours total | BOR Report of Findings (1977), main text (page number not reliably recoverable from the OCR scan) and Appendix B ("Seismicity") |
| 12:05 p.m. | Peak flow arrival at the Teton Canyon gauge, 4 km downstream | arXiv:2206.00766, Table 2 (citing "Reclamation, 1976; USGS, 1976") — corroboration only, not a primary source read directly |
| 5:00–6:00 p.m. | **Reservoir essentially empty** | BOR Report of Findings (1977), Table 1, p. 47 |

**Note on the seismic timestamp:** the 11:47 a.m. instrumental record is an independent, non-eyewitness confirmation that catastrophic failure was already underway several minutes before the commonly cited 11:55–11:57 a.m. "crest collapse / dam breached" times — but it measures *ground motion*, not breach discharge or geometry, so it should not be read as contradicting the 11:55/11:57 chronology; it corroborates that large-scale material movement began earlier than the crest's final visible collapse.

---

## 3. Breach formation duration

**No single official figure explicitly labeled "breach formation time/duration" was found.** Instead, the source documents state several different, precisely time-bounded intervals, each with a different start point — reported here individually rather than collapsed into one number:

| Interval definition | Duration | Observed/estimate | Source |
|---|---|---|---|
| Crest collapse → full embankment breach | **2 minutes** (11:55 a.m. → 11:57 a.m.) | Observed (eyewitness/photographic timestamps) | BOR Report of Findings (1977), p. 41, 47 |
| Reservoir whirlpool first observed → full breach | **~57 minutes** (11:00 a.m. → 11:57 a.m.) | Observed | BOR Report of Findings (1977), Table 1, p. 47 |
| First observed seepage in the immediate vicinity of the dam → dam failure | **5 hours** (explicitly stated) | Observed, stated directly in the source text | BOR Report of Findings (1977), p. 41: *"It took only 5 hours from the time of the first observed seepage in the immediate proximity of the dam until the dam failed."* |
| Last time dam observed to have **no** visible leakage (9:00 p.m., June 4) → dam breached | **15 hours** (explicitly stated) | Observed, stated directly in the source text | BOR Report of Findings (1977), p. 41: *"From the time at which the dam was last observed to have no visible leakage, 9:00 p.m. the previous night, only 15 hours were required to breach the dam."* |
| Dam breached → reservoir essentially empty | **~5–6 hours** (11:57 a.m. → 5:00–6:00 p.m.) | Observed (qualitative endpoint — "essentially empty" is not a precise numeric criterion) | BOR Report of Findings (1977), Table 1, p. 47 |

---

## 4. Observed final breach top width

**Not found.** Neither the Independent Panel (1976) report nor the BOR Report of Findings (1977) — both read in full-text search in this session — states a measured final top width of the breach opening. The word "breach" appears only 12 times in the BOR Report of Findings, almost entirely in the geotechnical/soil-mechanics appendix (describing the *excavated investigation face*, not the as-failed breach geometry), and the Independent Panel report's mentions of "breach" are similarly about the post-failure investigation excavation, not a formal breach-width survey. USGS OFR 77-765 (Ray et al.) — the report most likely to contain this — could not be retrieved (see access-gap note above).

---

## 5. Observed final breach bottom width

**Not found**, for the same reason as §4. One number exists in the literature search that specifically is **not** used here: arXiv:2206.00766 reports a "final bottom width of 55 m" for its own HEC-RAS breach parameterization, but the paper states this was chosen as "the best fit... to match historical literature values and fit the terrain" — i.e., it is that paper's own calibrated *model input*, not a cited, directly-measured historical field value, and the paper does not attach a specific citation to the number 55 m itself. Per this task's instruction to exclude unclear-provenance secondary figures, it is **not** reported as an observed value.

---

## 6. Observed breach depth

**No single reported "breach depth" figure was found.** The following raw elevation data points exist in the source documents and are reported here **only as-is, individually** — no depth has been computed or inferred from them, since doing so would be this project's own derived estimate, not a reported historical value:

| Elevation reference | Value | Source |
|---|---|---|
| Embankment crest (before camber) | El. 5332 ft | Independent Panel (1976), PDF p. 26: *"The crest elevation before camber was 5332..."* |
| Right-abutment leak/erosion elevation (lower) | El. 5045 ft | BOR Report of Findings (1977), Table 1, p. 46 and Fig. 19 caption |
| Sinkhole location elevation | El. 5315 ft | BOR Report of Findings (1977), Table 1, p. 47 |

---

## 7. Initial and final reservoir water level / drawdown

| Field | Value |
|---|---|
| **Initial value** | **El. 5301.7 ft** |
| Single value or range | Single value (staff-gauge reading) |
| Observed or post-hoc estimate | Observed — a direct instrument reading, taken and read at approximately 8:00 a.m. June 5, 1976, sustained through the failure sequence |
| Exact definition and reference point | Reservoir water-surface elevation at the moment of failure, June 5, 1976. Explicitly stated to be **3.3 ft below the spillway sill** and **22.6 ft below the maximum (design) water level of El. 5324.3 ft** |
| Source | Independent Panel (1976), PDF p. 7 (Summary and Conclusions): *"Teton Dam failed on June 5, 1976, when the reservoir was at El. 5301.7, 3.3 ft below the spillway sill."*; PDF p. 26: *"...reservoir water level was at El. 5301.7. That level was 22.6 ft below the maximum water level and 3.3 ft below the spillway sill."* Independently corroborated with a direct eyewitness quote at PDF p. 391 ("The reservoir was at elevation 5301.7") and again in BOR Report of Findings (1977), p. 32: *"The water level had only reached the spillway approach channel (El. 5301.7) when failure occurred."* |

| Field | Value |
|---|---|
| **Final value** | **Not numerically quantified in either source read.** Only a qualitative descriptor exists: **"Reservoir essentially empty"** |
| Single value or range | N/A — qualitative statement, not a number |
| Observed or post-hoc estimate | Observed (qualitative field/photographic assessment), not a surveyed final pool elevation |
| Exact definition and reference point | Same-day status, reported for the window **5:00–6:00 p.m., June 5, 1976** (i.e., about 5–6 hours after the 11:57 a.m. breach) |
| Source | BOR Report of Findings (1977), Table 1 ("Chronology of Significant Happenings..."), p. 47, item 20 |

**Drawdown**: because no numeric final elevation was found, an exact drawdown magnitude (ft) is **not reported** here — computing one from "essentially empty" would require assuming a valley-floor/outlet-invert datum not stated in either source, which this document does not do.

---

## Summary of gaps (per task instruction — items with no usable data found)

- Peak breach outflow **at the dam face itself** (only a downstream-canyon cross-section estimate, 2.5 mi below the dam, was found, via a secondary citation chain)
- Direct access to USGS Open-File Report 77-765 (Ray, Kjelstrom, Crosthwaite, and Low, 1978), the report most likely to hold the primary hydrologic estimate — no digital copy could be located in this session
- Observed final breach top width — not found in any source read
- Observed final breach bottom width — not found in any source read (one unrelated *model-calibrated* value exists in a secondary academic paper and is deliberately excluded here)
- Observed breach depth — not found as a single reported figure; only unconnected raw elevation data points exist
- Exact numeric final reservoir water-surface elevation / exact drawdown — only a qualitative "essentially empty" statement was found, with a same-day time window but no elevation
