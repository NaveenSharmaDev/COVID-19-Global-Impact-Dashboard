Total Cases =
SUM(
    covid_country_daily[total_cases]
)


Total Deaths =
SUM(
    covid_country_daily[total_deaths]
)


Total Recovered =
SUM(
    covid_country_daily[total_recovered]
)


Crude CFR % =
DIVIDE(
    [Total Deaths],
    [Total Cases],
    0
) * 100


Daily Cases (Chart) =
SUM(
    covid_country_daily[daily_cases_chart]
)


Daily Deaths (Chart) =
SUM(
    covid_country_daily[daily_deaths_chart]
)


Average 7D Cases =
AVERAGE(
    covid_country_daily[cases_7d_avg]
)


Average 7D Deaths =
AVERAGE(
    covid_country_daily[deaths_7d_avg]
)


Estimated Active =
SUM(
    covid_country_daily[active_estimate]
)