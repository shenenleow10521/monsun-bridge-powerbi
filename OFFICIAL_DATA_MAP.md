# Official Data Map · DOSM Datathon Rule 9

## Critical correction

Verified DOSM releases do **not** support the statement “quarterly state tourism data”. Use this evidence architecture:

- **OBSERVED:** national quarterly Domestic Tourism Survey signal.
- **OBSERVED:** annual state tourism context.
- **DERIVED:** TAI, Monsoon Share, national TSEI and Counter-Seasonality Index.
- **MODELLED:** state/district allocation, tourism-linked workers, Worker-Month Exposure, transition scores, capacity proxies and programme-cost scenarios.

P1 and P2 now state this boundary explicitly. Do not remove those labels.

## Model input contract

Processed files live under `C:\MonsunBridge\data\processed` and use the `MB_*.csv` prefix. They must be reproducible outputs derived from the official sources in `DATA_EVIDENCE_REGISTER.csv`.

| File | Evidence role | Minimum provenance |
|---|---|---|
| `MB_fct_tourism_exposure.csv` | DERIVED / MODELLED | DOSM quarterly national releases + annual state context + formulas |
| `MB_fct_workforce_exposure.csv` | MODELLED | DOSM district labour force + stated tourism-dependency assumptions |
| `MB_fct_sector_seasonality.csv` | DERIVED | DOF monthly fish landings + tourism signal + CSI formula |
| `MB_fct_transition_pathway.csv` | MODELLED | MASCO/HRD text + weights + capacity evidence grade |
| `MB_fct_skill_evidence.csv` | OBSERVED TEXT mapping | Source URL or PDF page for every record |
| `MB_dim_occupation*.csv` | OBSERVED TEXT / curated | MASCO codes and citations |
| `MB_dim_district.csv` | OBSERVED / curated | DOSM district names; coordinate source recorded |
| `MB_dim_date.csv` | GENERATED | Deterministic calendar-generation code |
| `MB_dim_evidence_level.csv` | GOVERNANCE | Internal label dictionary |

`dim_monsoon_window` is embedded with only two verified METMalaysia seasons: 2020/21 and 2024/25. Add another season only after saving the official page citation.

## Prohibited claims

- Do not call district tourism allocation an official DOSM statistic.
- Do not call tourism-linked workers an observed worker register.
- Do not convert Worker-Month Exposure into RM income loss.
- Do not call a Level 2 capacity proxy a vacancy or guaranteed absorption count.
