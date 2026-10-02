# Power BI Deliverables

This folder contains the complete set of files and specifications required to import, model, and build the Power BI report.

## Included Files

- **Fact_CovidCountryDaily.csv**, **Dim_Date.csv**, and **Dim_Country.csv** — Located in `data/processed/` and used as the source tables.
- **Power_Query_Fact.m** — Contains the Power Query M script for the fact table. Update the project folder path before importing.
- **DAX_Measures.dax** — Contains the DAX measures to be created in Power BI.
- **VEDA_COVID19_Theme.json** — An importable Power BI theme file.
- **POWER_BI_REPORT_LAYOUT.md** — Specifies the data model and the layout for all four report pages.

## PBIX File Information

A native `.pbix` file is created and saved using Power BI Desktop. Since this environment cannot execute Power BI Desktop, this package does not claim to include a generated PBIX file.

## Steps to Create the PBIX

1. Open **Power BI Desktop** on Windows.
2. Import the three CSV tables from `data/processed/`.
3. Create the two relationships as specified in the report layout.
4. Add the measures from `DAX_Measures.dax`.
5. Apply the theme using `VEDA_COVID19_Theme.json`.
6. Build the four report pages according to `POWER_BI_REPORT_LAYOUT.md`.
7. Save the completed report in this folder as:

   `COVID19_Global_Impact.pbix`