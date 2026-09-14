# Monsun Bridge Power BI Redesign

This branch contains a reconstructed Power BI Project (PBIP) and the first visual redesign pass for P3 Skill Bridge and P4 Government Action Planner.

## Open in Power BI Desktop

1. Download this branch as a ZIP and extract it.
2. Open `codexversion.pbip` using a recent Power BI Desktop release with PBIP/PBIR support.
3. If Power BI reports external changes, allow it to reload the project.
4. If data is not available, reconnect the Power Query parameters to your verified local CSV/XLSX sources. Keep `.pbi/cache.abf` local; do not publish it to a public repository.
5. Test all slicers, cross-filtering, tooltips, tables and page navigation on P3 and P4.
6. Save a separate PBIX copy only after the project opens successfully.

## What changed

- Rebuilt the flattened upload into the official PBIP folder structure.
- Added a restrained policy-intelligence theme: navy, teal, amber and coral.
- P3 now uses a clear filter rail, ranked transition bar chart, recommendation KPIs and evidence table.
- P4 now uses four scenario controls, six decision KPIs, district allocation, cost/exposure comparison, implementation timeline and a concise modelled-scenario disclaimer.
- Renamed the misleading display label from “Cost per Worker-Month Avoided” to “Cost per Worker-Month Covered”. The underlying measure was not changed.

## Validation required

This environment cannot run Power BI Desktop. Treat this branch as a design candidate until it has been opened and tested on Windows.

## Data-integrity blocker

The semantic model currently references files named `DUMMY_*.csv` under `C:\MonsunBridge\dummy`. Before competition submission, confirm these files are authentic official-derived data and that “DUMMY” is only a temporary filename. Otherwise replace them with verified official Malaysian sources and preserve the OBSERVED / DERIVED / MODELLED evidence labels.
