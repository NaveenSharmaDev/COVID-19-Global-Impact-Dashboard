# Power BI Report Build – Complete Layout Specification

## 1. Data Model – Star Schema

### Data Import

Import the following CSV files from `data/processed/`:

- `Fact_CovidCountryDaily.csv` – Fact Table
- `Dim_Date.csv` – Date Dimension
- `Dim_Country.csv` – Country Dimension

### Relationships

Create the following relationships with single-direction filtering and one-to-many cardinality:

| Primary Table | Primary Column | Related Table | Related Column | Cardinality |
|---|---|---|---|---|
| Dim_Date | date_key | Fact_CovidCountryDaily | date_key | One-to-Many |
| Dim_Country | country_key | Fact_CovidCountryDaily | country_key | One-to-Many |

### Model Configuration

- Mark `Dim_Date` as the Date Table using `Dim_Date[date]`.
- Sort `month_name` by `month_number`.
- Sort `year_month` by itself.

---

## 2. Page 1 – Executive Overview (16:9)

### Header

COVID-19 Global Impact | Historical Analysis

### Slicers

- Date Range
- Country / Region

### KPI Cards

1. Cases - Latest Visible Date
2. Deaths - Latest Visible Date
3. Recoveries - Latest Visible Date
4. Crude CFR %

### Visualizations

**1. Daily Cases and Deaths**

- Visual: Line Chart
- X-Axis: `Dim_Date[date]`
- Y-Axis:
  - Daily Cases (Chart)
  - Daily Deaths (Chart)

**2. Seven-Day Average Trends**

- Visual: Line Chart
- X-Axis: `Dim_Date[date]`
- Y-Axis:
  - 7D Avg Cases
  - 7D Avg Deaths

**3. Top 10 Countries by Cases**

- Visual: Bar Chart
- Category: `Dim_Country[country]`
- Values: Cases - Latest Visible Date
- Filter: Top N = 10

**4. Country-Wise Summary**

- Visual: Matrix
- Rows: Country
- Values:
  - Latest Cases
  - Deaths
  - Recoveries
  - CFR

**5. Reporting Information**

- Visual: Text Panel
- Content:
  - Reporting Revisions
  - Source Limitations

---

## 3. Page 2 – Global Trends

### Visualizations

- Cumulative Cases and Deaths over Date
- Daily Cases and Deaths with Seven-Day Averages

### Slicers

- Month
- Year

### Tooltip Configuration

Include the following fields:

- Date
- Daily Cases
- Daily Deaths
- Cumulative Cases
- Cumulative Deaths
- Seven-Day Average

---

## 4. Page 3 – Country Comparison

### Slicers

- Country (Multi-Select)

### Visualizations

**1. Country-Wise Comparison**

- Visual: Clustered Bar Chart
- Values:
  - Latest Cases
  - Latest Deaths

**2. Seven-Day Average Cases**

- Visual: Line Chart
- Values: 7D Avg Cases
- Legend: Country

**3. Latest Country Metrics**

- Visual: Table
- Fields:
  - Country
  - Latest Cases
  - Latest Deaths
  - Latest Recoveries
  - CFR %

### Data Interpretation Note

Values represent absolute reported counts, not per-million rates.

---

## 5. Page 4 – Data Quality and Definitions

### KPI Cards

- Revision Case Rows
- Revision Death Rows

### Visualizations

**Revision Analysis**

- Visual: Table
- Include records filtered by revision flags:
  - `case_revision_flag`
  - `death_revision_flag`

### Metric Definitions

**Crude Case Fatality Ratio (CFR)**

The ratio of reported deaths to reported confirmed cases, expressed as a percentage.

**Estimated Active Cases**

The estimated number of active cases based on the prepared dataset.

**Chart-Adjusted Daily Counts**

Daily reported counts adjusted for chart presentation and revision handling.

### Data Availability Note

The supplied selected dataset does not contain vaccination data or a population denominator.

---

## 6. Formatting and Design Specifications

### Page Configuration

- Page Size: 16:9
- Canvas Background: `#F4F7FB`
- Title Color: Navy
- Primary Accent: Blue
- Secondary Accent: Cyan
- Highlight Accent: Orange

### Theme Configuration

Apply the following Power BI theme:

`VEDA_COVID19_Theme.json`

### Number Formatting

| Metric Type | Format |
|---|---|
| Total Cases | Comma Separator, 0 Decimal Places |
| Total Deaths | Comma Separator, 0 Decimal Places |
| Total Recoveries | Comma Separator, 0 Decimal Places |
| Daily Counts | Comma Separator, 0 Decimal Places |
| CFR % | 2 Decimal Places |

### Data Aggregation Rules

- Do not sum cumulative measures across multiple dates in a visual.
- Use latest-visible-date measures for snapshot KPI cards.
- Maintain appropriate date relationships for time-series analysis.
- Use the date dimension for date-based filtering and reporting.
- Do not title CFR as Infection Fatality Rate.

---

## 7. Final Report Structure

| Page | Report Name | Primary Purpose |
|---|---|---|
| 1 | Executive Overview | Global KPIs and summary |
| 2 | Global Trends | Historical COVID-19 trends |
| 3 | Country Comparison | Country-level comparison |
| 4 | Data Quality & Definitions | Revision analysis and metric definitions |

**Project Title:** COVID-19 Global Impact Dashboard

**Platform:** Microsoft Power BI Desktop

**Data Architecture:** Star Schema

**Report Pages:** 4

**Canvas Format:** 16:9