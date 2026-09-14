# Power BI Validation Checklist

Open `codexversion.pbip` in a current Power BI Desktop build after fully extracting the repository.

## Data
- [ ] Run `scripts/download_official_data.ps1`.
- [ ] Generate every `MB_*.csv` from official inputs and record provenance.
- [ ] Refresh with zero `DUMMY_*` paths and zero missing-file errors.
- [ ] Confirm only verified METMalaysia seasons appear.

## P1 · WHEN
- [ ] Dynamic header and slicers render.
- [ ] Local allocation is not presented as observed district tourism.
- [ ] Monsoon table shows full dates.
- [ ] Combo chart sorts quarters chronologically and tooltips show TAI.

## P2 · WHO
- [ ] Static locator is labelled context-only.
- [ ] Priority Band filters all exposure visuals.
- [ ] Bars cross-filter the detail table.
- [ ] Worker counts and WME remain labelled MODELLED.
- [ ] No visual implies individual income loss.

## P3 · WHERE TO
- [ ] Occupation and district slicers filter ranking, cards and evidence.
- [ ] Rank 1 matches the recommendation card.
- [ ] Skill evidence includes source and reference.
- [ ] Capacity displays L1/L2/L3 correctly.
- [ ] Similarity is not described as job availability.

## P4 · WHAT ACTION
- [ ] Four parameters recalculate six KPIs.
- [ ] Cost and exposure use clearly different units/axes.
- [ ] District allocation totals reconcile.
- [ ] Disclaimer says MODELLED SCENARIO — NOT A BUDGET.
- [ ] Timeline is readable in PDF.

## Submission
- [ ] Test on three Windows computers.
- [ ] Inspect exported PDF at 100%.
- [ ] Final ZIP contains PBIX, PDF, data file and README.txt.
- [ ] Keep repository private until judging ends.
