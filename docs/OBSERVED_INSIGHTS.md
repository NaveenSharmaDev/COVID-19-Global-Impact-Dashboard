# Observed Insights — Supplied Historical Dataset

**Scope:** Country/region records in the supplied `CoronaVirus Data.csv`, aggregated by date; date coverage 22 January 2020–1 January 2021. The global roll-up excludes any row named `World` to avoid double counting. Counts are reported totals, not population-adjusted rates.

1. **Cumulative burden at the final available date:** On 1 January 2021, the country/region roll-up contained **83,963,772 reported confirmed cases**, **1,827,540 reported deaths**, and **46,794,641 reported recoveries**.
2. **Largest cumulative case counts in the final snapshot:** The United States had **20,128,693** reported cases, India **10,286,709**, and Brazil **7,700,578**. These are absolute counts; population-adjusted comparisons are not possible from the supplied files.
3. **Highest 7-day average of reported daily cases:** The global roll-up's maximum 7-day average was approximately **749,627 cases per day on 16 December 2020**.
4. **Highest 7-day average of reported daily deaths:** The global roll-up's maximum 7-day average was approximately **11,670 deaths per day on 23 December 2020**.
5. **Data quality:** The preparation pipeline flagged **51 country-date negative case revisions** and **72 negative death revisions** when daily changes were derived from cumulative totals. These likely reflect retrospective data corrections; the dashboard flags them and floors only chart display values at zero.

**Interpretation note:** These observations describe the supplied historical dataset. They do not establish causes, vaccination effects, or current pandemic conditions.
