# COVID-19 Global Impact Dashboard
## Project Report — VEDA Technology Internship

**Project:** COVID-19 Global Impact Dashboard  
**Domain:** Data Analytics and Visualization  
**Technology:** Python, Pandas, NumPy, Plotly, Streamlit  
**Dataset:** Original files supplied by the project submitter  
**Report date:** 30 September 2026

## 1. Executive Summary
This project converts supplied historical COVID-19 time-series data into a country/region-level analytical dataset and an interactive dashboard. The workflow covers data ingestion, cleaning, aggregation, feature engineering, visualization, and documentation. It is designed to communicate historical reported trends to a non-technical audience.

The project deliberately distinguishes available measures from unavailable measures. The supplied selected source includes cases, deaths, and recoveries but no compatible population or vaccination series. As a result, per-million rates and vaccination correlations are not presented as if they were measured.

## 2. Problem Statement
Raw pandemic time series can be wide, fragmented by province/state, and difficult to compare. Stakeholders need a consistent daily table, clear trend metrics, and interactive country/date filters. Reporting corrections and differences in data collection can also make daily counts noisy.

## 3. Objectives
- Preserve original supplied source files.
- Produce a tidy country/region-day dataset.
- Compute daily changes, 7-day averages, CFR and estimated active cases.
- Identify and document retrospective revisions.
- Build an interactive dashboard with country and date filters.
- Provide reproducible setup instructions and Power BI guidance.

## 4. Dataset and Scope
Primary file: `data/raw/CoronaVirus Data.csv` from the first supplied ZIP. It contains province/state, country/region, coordinates, date, cumulative confirmed cases, deaths, recoveries, and daily fields. Three wide-format JHU-style global time-series files are retained from the first archive, and matching global confirmed/deaths/recovered time-series files from the second archive are also included in `data/raw/` with a `second_zip_` prefix. To avoid mixing overlapping source snapshots, the dashboard pipeline uses only the first archive's daily-format source; the second archive's files are retained separately for traceability.

**Scope limitation:** No vaccination or population field is present in the selected data. Vaccination coverage, cases per million, and a vaccination/death relationship are not computed. The data is historical and not live.

## 5. Methodology
1. **Ingestion:** Read the supplied CSV with Pandas.
2. **Standardization:** Trim column names, parse dates, convert numeric fields, and remove records with invalid date/country.
3. **Aggregation:** Sum province/state rows by country/region and date.
4. **Feature engineering:** Derive daily changes from cumulative totals; calculate 7-day rolling averages, crude CFR, and estimated active cases.
5. **Revision handling:** Preserve negative differences as revision flags and retain the unmodified derived value. For chart display only, negative daily values are floored at zero.
6. **Visualization:** Streamlit + Plotly dashboard with global trends, country comparisons, KPIs, table and CSV export.
7. **Validation:** Record row counts, date range, country/region count, duplicate keys and revision counts in the QA JSON.

## 6. Metric Definitions
| Metric | Formula / interpretation |
|---|---|
| Daily cases | Current cumulative cases − previous date cumulative cases, by country |
| Daily deaths | Current cumulative deaths − previous date cumulative deaths, by country |
| 7-day average | Rolling mean of chart-adjusted daily values |
| CFR | Cumulative reported deaths ÷ cumulative reported cases × 100 |
| Estimated active | max(cases − deaths − recoveries, 0) |
| Cases per million | Not computed: compatible population denominator unavailable |
| Vaccination coverage | Not computed: vaccination time series unavailable |

CFR is a crude reported ratio, not an infection fatality rate. Estimated active cases depend on recovery reporting and are not a clinical count.

## 7. Dashboard Components
- Dark, multi-page Streamlit interface inspired by the provided dashboard reference.
- Sidebar navigation, date range, continent and country filters.
- Overview, Global Trends, Country Comparison, Vaccination Analysis, Data Explorer, Key Insights and Methodology pages.
- Interactive world choropleth and country ranking charts.
- KPI cards for cumulative cases, deaths, recoveries and CFR.
- Global daily reported cases/deaths trend.
- Cumulative cases area chart.
- Country multi-select and date range controls.
- 7-day average case comparison.
- Top country/region cumulative case chart.
- Country snapshot table with CSV export.
- In-dashboard limitations and interpretation notes.

## 8. Data Quality and Limitations
The pipeline validates dates and numeric columns, aggregates duplicate province/state observations to country-day, and reports duplicate keys after aggregation. Retrospective negative differences are flagged. Filling missing numeric values with zero is a pragmatic aggregation choice and must not be interpreted as proof of zero incidence. Reporting definitions and completeness vary across jurisdictions. The selected source does not support population normalization or vaccination analysis.

## 9. Observed Insights
For the supplied data coverage (22 January 2020–1 January 2021), the global roll-up excludes a possible `World` row to avoid double counting.

1. On 1 January 2021, the roll-up contained 83,963,772 reported confirmed cases, 1,827,540 reported deaths, and 46,794,641 reported recoveries.
2. The largest cumulative case counts in the final snapshot were the United States (20,128,693), India (10,286,709), and Brazil (7,700,578). These are absolute counts, not population-adjusted rates.
3. The maximum global 7-day average of reported daily cases was approximately 749,627 on 16 December 2020.
4. The maximum global 7-day average of reported daily deaths was approximately 11,670 on 23 December 2020.
5. The data pipeline flagged 51 country-date negative case revisions and 72 negative death revisions derived from cumulative totals.

These are descriptive observations from the supplied historical file, not causal findings or current pandemic conditions. See `OBSERVED_INSIGHTS.md` for detail. Do not claim vaccination effects: vaccination and population fields are absent.

## 10. Reproducibility
Install dependencies with `python -m pip install -r requirements.txt`, then run `python -m streamlit run app/app.py`. To rebuild processed data, run `python scripts/prepare_data.py`. The processed dataset and QA summary are included.

## 11. Conclusion
The deliverable provides a reproducible historical analysis and interactive dashboard based on the user's supplied data. It meets the core requirements for cleaning, trend analysis, derived metrics, country comparison, and visual communication. Additional population and vaccination datasets would be required to extend the analysis to normalized incidence and vaccination-related questions.

## 12. References
- Our World in Data, COVID-19 data documentation: https://docs.owid.io/projects/etl/api/covid/
- OWID COVID-19 data repository documentation and source caveats: https://github.com/owid/covid-19-data
- Supplied original ZIP archives (see `data/raw/` and README).


## Updated dashboard implementation
The revised app removes the Methodology navigation item and VEDA Analytics label, adds project-name branding below COVID-19, introduces a layered 3D-inspired visual theme and a rotatable Plotly 3D country comparison. It attempts to load the current OWID COVID catalog and falls back to the supplied original historical data if the network source is unavailable. Vaccination visuals are shown only when source vaccination fields exist; no synthetic vaccination values are generated.


## Final QA corrections — 30 September 2026
The dashboard hero spacing and typography were adjusted to prevent clipping. The visual treatment was refined for a more natural, professional analytics appearance. Vaccination coverage is now retrieved from OWID's dedicated full-vaccination percentage series and is kept separate from the supplied JHU case/death files. The Overview KPI uses the latest global observation available up to the selected end date. Country KPI snapshots use the last available observation within the selected date window. When the vaccination endpoint is offline, the dashboard explicitly reports that it could not load the series rather than inventing a value.
