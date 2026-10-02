// Power BI Power Query M — use one query per table.
// Replace C:\PATH\TO\COVID19_Global_Impact_Dashboard with the extracted project folder.

let
    ProjectFolder = "C:\PATH\TO\COVID19_Global_Impact_Dashboard",

    Source = Csv.Document(
        File.Contents(
            ProjectFolder & "\data\processed\Fact_CovidCountryDaily.csv"
        ),
        [
            Delimiter = ",",
            Encoding = 65001,
            QuoteStyle = QuoteStyle.Csv
        ]
    ),

    Headers = Table.PromoteHeaders(
        Source,
        [PromoteAllScalars = true]
    ),

    Types = Table.TransformColumnTypes(
        Headers,
        {
            {"country", type text},
            {"date", type date},
            {"total_cases", Int64.Type},
            {"total_deaths", Int64.Type},
            {"total_recovered", Int64.Type},
            {"daily_cases", Int64.Type},
            {"daily_deaths", Int64.Type},
            {"daily_recovered", Int64.Type},
            {"daily_cases_chart", Int64.Type},
            {"daily_deaths_chart", Int64.Type},
            {"cases_7d_avg", type number},
            {"deaths_7d_avg", type number},
            {"cfr_percent", type number},
            {"active_estimate", Int64.Type},
            {"country_key", Int64.Type},
            {"date_key", Int64.Type}
        }
    )
in
    Types