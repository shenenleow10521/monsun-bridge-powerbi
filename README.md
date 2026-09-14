# Monsun Bridge · Power BI

Competition dashboard branch: `codex/dashboard-redesign`.

## Open
1. Download the branch ZIP and **extract the entire folder**.
2. Open `codexversion.pbip` in a current Power BI Desktop release.
3. Put verified processed files in `C:\MonsunBridge\data\processed`.
4. If old files start with `DUMMY_`, run `scripts/migrate_local_filenames.ps1`.
5. Refresh and complete `POWER_BI_VALIDATION_CHECKLIST.md`.

## Evidence and data
- `DATA_EVIDENCE_REGISTER.csv` lists verified Malaysian official sources.
- `OFFICIAL_DATA_MAP.md` defines OBSERVED / DERIVED / MODELLED boundaries.
- `scripts/download_official_data.ps1` downloads five official CSV inputs.

The repository is public at the time of this redesign. Make it private until DOSM judging is complete.
