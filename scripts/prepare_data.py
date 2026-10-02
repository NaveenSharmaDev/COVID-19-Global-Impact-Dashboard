from pathlib import Path
import json

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "CoronaVirus Data.csv"
OUT = ROOT / "data" / "processed"

OUT.mkdir(parents=True, exist_ok=True)


def build():
    df = pd.read_csv(SOURCE)
    df.columns = df.columns.str.strip()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    numeric = [
        "Confirmed",
        "Deaths",
        "Recovered",
        "Confirmed Daily",
        "Deaths Daily",
        "Recovered Daily",
    ]

    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Date", "Country/Region"])
    df[numeric] = df[numeric].fillna(0)

    daily = (
        df.groupby(["Country/Region", "Date"], as_index=False)[numeric]
        .sum()
        .sort_values(["Country/Region", "Date"])
    )

    daily = daily.rename(
        columns={
            "Country/Region": "country",
            "Date": "date",
            "Confirmed": "total_cases",
            "Deaths": "total_deaths",
            "Recovered": "total_recovered",
            "Confirmed Daily": "reported_daily_cases",
            "Deaths Daily": "reported_daily_deaths",
            "Recovered Daily": "reported_daily_recovered",
        }
    )

    daily["daily_cases"] = (
        daily.groupby("country")["total_cases"]
        .diff()
        .fillna(daily["total_cases"])
    )

    daily["daily_deaths"] = (
        daily.groupby("country")["total_deaths"]
        .diff()
        .fillna(daily["total_deaths"])
    )

    daily["daily_recovered"] = (
        daily.groupby("country")["total_recovered"]
        .diff()
        .fillna(daily["total_recovered"])
    )

    daily["case_revision_flag"] = daily["daily_cases"] < 0
    daily["death_revision_flag"] = daily["daily_deaths"] < 0

    daily["daily_cases_chart"] = daily["daily_cases"].clip(lower=0)
    daily["daily_deaths_chart"] = daily["daily_deaths"].clip(lower=0)

    daily["cases_7d_avg"] = (
        daily.groupby("country")["daily_cases_chart"]
        .transform(lambda x: x.rolling(7, min_periods=1).mean())
    )

    daily["deaths_7d_avg"] = (
        daily.groupby("country")["daily_deaths_chart"]
        .transform(lambda x: x.rolling(7, min_periods=1).mean())
    )

    daily["cfr_percent"] = np.where(
        daily["total_cases"] > 0,
        daily["total_deaths"] / daily["total_cases"] * 100,
        np.nan,
    )

    daily["active_estimate"] = (
        daily["total_cases"]
        - daily["total_deaths"]
        - daily["total_recovered"]
    ).clip(lower=0)

    daily["month"] = daily["date"].dt.to_period("M").astype(str)

    daily.to_csv(
        OUT / "covid_country_daily.csv",
        index=False,
        date_format="%Y-%m-%d",
    )

    summary = {
        "rows": int(len(daily)),
        "countries_or_regions": int(daily["country"].nunique()),
        "date_start": str(daily["date"].min().date()),
        "date_end": str(daily["date"].max().date()),
        "duplicate_country_date_rows": int(
            daily.duplicated(["country", "date"]).sum()
        ),
        "negative_case_revisions": int(daily["case_revision_flag"].sum()),
        "negative_death_revisions": int(daily["death_revision_flag"].sum()),
        "vaccination_data_available": False,
        "population_data_available": False,
    }

    (OUT / "data_quality_summary.json").write_text(
        json.dumps(summary, indent=2)
    )

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    build()