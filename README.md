# COVID-19 Global Impact Dashboard
**VEDA Technology Internship Project | Data Analytics**

An interactive historical data analytics dashboard developed using Python, Pandas, Plotly, and Streamlit. The project uses the original COVID-19 datasets supplied in two ZIP archives to explore reported cases, deaths, recoveries, and vaccination trends where a separate source is available.

## 1. Project Objectives

- Clean and aggregate province-level time-series observations into country/region-day records.
- Analyze cumulative and daily cases, deaths, and recoveries.
- Calculate 7-day moving averages, crude case fatality ratio (CFR), and estimated active cases.
- Compare selected countries over a chosen date range.
- Generate and export country-level snapshots for further analysis.

## 2. Data Sources and Provenance

### Primary Historical Source
`data/raw/CoronaVirus Data.csv`

This file was extracted unchanged from `Covid-19-Analysis-and-Prediction-main.zip` and is the single analytical source used by the reproducible historical data-processing pipeline.

### Additional Reference Files
The supplied JHU-style wide time-series files from both ZIP archives are retained in `data/raw/` for traceability.

Files prefixed with `second_zip_` were obtained from `COVID-19-master.zip`. These files are maintained as a separate reference set and are not merged with the primary dataset. This avoids accidental double counting and mixed-source totals.

### Data Scope and Limitations

The selected original source does not contain a compatible population table or vaccination time series. Therefore, the historical dataset is not used to calculate vaccination coverage, cases per million, or vaccine/death correlation.

These analyses require a separately sourced, cited, and date-compatible population or vaccination dataset.

The historical data ends on the date recorded in `data/processed/data_quality_summary.json`. It is not a live data source.

## 3. Dashboard Features

- Responsive dashboard with sidebar navigation, date, continent, and country filters.
- Reset controls and KPI cards.
- Overview, Global Trends, Country Comparison, Vaccination Analysis, Data Explorer, and Key Insights pages.
- Interactive world choropleth map and country rankings.
- Cumulative cases, deaths, recoveries, and crude CFR indicators.
- Global daily case and death trends.
- Cumulative case trend analysis.
- Country selection and date-range filtering.
- 7-day moving-average comparisons.
- Top country/region bar chart.
- Country snapshot table with CSV export.
- Data revision flags and documented data limitations.
- Interactive Plotly 3D country comparison.

## 4. Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly |
| Dashboard Framework | Streamlit |
| Data Storage | CSV |
| Data Processing | Python scripts |
| External Data Sources | Our World in Data (OWID) |

## 5. Installation and Execution on Windows

### Prerequisites
- Windows operating system
- Python 3.10 or newer
- Internet connection for online data refresh

### Setup Instructions

**Step 1: Extract the project**

Extract the project ZIP file to your preferred directory.

**Step 2: Open PowerShell**

Open PowerShell inside the extracted project folder.

**Step 3: Create and activate a virtual environment**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1