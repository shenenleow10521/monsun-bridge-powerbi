# Monsun Bridge — research build handoff

## Status: NOT SUBMISSION-READY

This package contains implementation work, not a certified competition entry.
Do not remove the visible readiness warnings until the evidence and Desktop checks pass.

## What is implemented

- P1–P4 layouts, source-resolution warnings and consistent brand treatment.
- Official-data downloader for DOSM district labour/income and DOF marine landings.
- Three local-import Power BI tables and visual bindings on P2/P3.
- Raw CSV preservation, SHA-256 manifest, strict schema checks and missing-data failures.
- Common-year district selection and complete-year marine-fish selection.
- Revised planner algebra: targeted WME = participation rate × baseline WME.
- Skill evidence correctly described as source-occupation evidence, not target-specific validation.

## What has NOT happened

- Python has not run in the authoring environment.
- Official source rows have not been downloaded/validated by this new script yet.
- Power BI Desktop has not rendered, refreshed or exported this build.
- Existing exposure/AI numbers have not been replaced by verified model outputs.
- No final report PDF, dashboard PDF, PBIX or recorded MP4 has been produced here.
- JSON parse success is not PBIR-schema, DAX-engine or visual-layout certification.

## Run once on Windows

1. Extract the complete branch ZIP into a new folder. Keep your original PBIX unchanged.
2. Python 3.10+ is required for data preparation; no third-party Python packages are needed.
3. Double-click `scripts/BUILD_OFFICIAL_DATA.cmd`.
4. The program prints a new `data/official_runs/official_.../processed` path.
5. In Power Query parameters, set `OfficialDataFolder` to that exact printed path.
6. Keep `DataFolder` pointing to your existing MB_* processed files. They remain unverified.
7. Refresh. The new P2 context tables and P3 marine-landings chart use the official imports.
8. Send back the generated `BUILD_STATUS.json`, current processed data, and a PDF of P1–P4.

Do not run the filename-migration script as evidence of compliance. Renaming a file does not validate its contents.

## Final release gates

A. Official booklet/rubric and any poster clarification checked against the actual files.
B. Tourism observations and the training/validation split reproduced from cited sources.
C. District/occupation shares justified; aggregate labour data alone cannot identify boat operators.
D. Official occupational text corpus includes target roles and traceable citations.
E. Similarity, seasonality, geography, eligibility and capacity constraints evaluated separately.
F. Planner results described as targeting scenarios, not avoided loss.
G. Power BI refresh, PDF export and offline interaction tested on Windows.
H. Final files packaged to the official names and instructions confirmed by the team.
