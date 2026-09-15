# Methods and limitations — material for the report

This is a methodology correction note, not a completed findings chapter.

## Tourism resolution and attribution
The examined quarterly DTS releases support a national time signal; the examined state release supplies annual context. This does not establish that no finer official dataset exists. Never label a state-quarter estimate OBSERVED merely because its inputs come from DOSM.

A national domestic-tourism curve cannot by itself identify monsoon disruption in a specific island district. Calendar effects, school holidays, travel purpose, trend, pandemic disruptions and other factors can change demand. Report association/exposure, not causal monsoon impact, without an identification strategy.

## Index construction
Do not put z-scored quantities into TSEI = 100 × (1 − TAI/baseline): negative or zero baselines make that interpretation invalid. Use a positive, clearly scaled activity measure and disclose normalization, weights, reference window and treatment of negative TSEI values. Fit preprocessing only on the training period in forecasts. Check redundancy between visitors and trips, and deflate nominal expenditure if comparing real activity.

Monsoon Share is a fraction of calendar days overlapping a dated season. It does not recover within-quarter tourism observations and is not weather intensity. Use an inclusive or half-open day convention consistently. Official monsoon dates and their method need to be cited per season; two seasons do not form a continuous historical series.

A fixed Nov–Mar window is a calendar assumption, not an observed annual onset record. Label it separately.

## Forecast evaluation
Use rolling-origin or time-ordered holdouts and a seasonal-naive benchmark. Report training/test dates, observations, MAE and RMSE. Avoid MAPE where actual values are zero/near zero. Prediction intervals need a specified procedure and empirical coverage check; STL residual spread alone is not automatically a calibrated forecast interval.

Do not claim p-values must approach zero because the season is predictable. Temporal dependence, confounding, sample size and identification determine what a test can support.

## Workforce
DOSM lfs_district labour and employment totals are in thousands. The official context table retains those published units.
District aggregate employment does not reveal the number of boat operators or tourism workers. Such allocation needs separately justified shares and uncertainty. Do not use the national services proportion as tourism dependence.

WME needs distinct definitions for tourism-linked workers and dependence to avoid counting the same share twice. Align snapshot years explicitly, and do not silently sum repeated annual populations.

## Alternative activity
DOF fish_landings is marine fish landed, not aquaculture production or vacancies. Landings location is not catch location.
The source ends in 2023 in the examined metadata. A newer tourism period cannot be paired with older fish observations as a contemporaneous comparison.
Aggregate monthly landings to common quarters before a CSI calculation; do not invent monthly tourism values.
A CSI above one means relative activity resilience under that definition, not absolute growth, available jobs or safe working conditions.

## Skills
The existing fct_skill_evidence lacks alt_occupation_code. Therefore its skill counts cannot change meaningfully by target pathway. Target-specific evidence requires an occupation-pair key, cited task/skill texts and validation.
A semantic score measures text similarity, not employability. Certificates, safety, schedules, language and travel constraints can be hard exclusions rather than small score penalties.
Training duration needs cited course duration or an explicitly named planning assumption.
Do not label this an implemented AI model until code, corpus, model revision, licence, outputs and evaluation are available.

## Capacity
Registered establishments and production are sector-presence proxies. They are not job slots.
Without evidence connecting a proxy to job capacity, do not multiply it by an arbitrary employment coefficient and call it absorption.
A zero-capacity or ineligible route must not be selected merely because its additive score is high.
linear_sum_assignment is one-to-one assignment; many-worker capacity allocation needs slot expansion or a capacitated flow/linear program with documented constraints.

## Planner
The corrected targeted-exposure scenario is p × WME for uniform participation probability p.
This deliberately does not estimate causal exposure reduction or successful placement.
Training/support duration affects cost; effectiveness is not observed. The report must not describe that cost-only parameterization as an evaluated policy effect.
Budget = participants × training months × rate + participants × support months × rate × 0.6, plus 10% administration. These coefficients are team assumptions, not official programme rates.
When targeted WME is zero, cost per targeted worker-month is undefined and should show blank.
