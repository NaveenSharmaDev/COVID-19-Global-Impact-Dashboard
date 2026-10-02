from pathlib import Path

import io

import urllib.request

import pandas as pd

import numpy as np

import plotly.express as px

import plotly.graph_objects as go

import streamlit as st

st.set_page_config(

    page_title="COVID-19 Global Impact Dashboard",

    page_icon="🌐",

    layout="wide",

    initial_sidebar_state="expanded"

)

ROOT = Path(__file__).resolve().parents[1]

LOCAL_PATH = ROOT / "data" / "processed" / "covid_country_daily.csv"

OWID_COMPACT_URL = "https://catalog.ourworldindata.org/garden/covid/latest/compact/compact.csv"

OWID_LEGACY_URL = "https://covid.ourworldindata.org/data/owid-covid-data.csv"

OWID_VACCINATION_URL = "https://ourworldindata.org/grapher/people-fully-vaccinated-covid.csv?v=1&csvType=full&useColumnShortNames=true"

OWID_VACCINATION_SHARE_URL = "https://ourworldindata.org/grapher/share-people-fully-vaccinated-covid.csv?v=1&csvType=full&useColumnShortNames=true"

@st.cache_data(ttl=3600, show_spinner=False)

def _read_csv_api(url):

    request = urllib.request.Request(

        url,

        headers={"User-Agent": "Mozilla/5.0 COVID-Dashboard/1.0"}

    )

    with urllib.request.urlopen(request, timeout=25) as response:

        return pd.read_csv(

            io.BytesIO(response.read()),

            low_memory=False

        )

@st.cache_data(ttl=3600, show_spinner=False)

def load_vaccination_source():

    count_urls = [

        OWID_VACCINATION_URL,

        "https://ourworldindata.org/grapher/people-fully-vaccinated-covid.csv",

        "https://ourworldindata.org/grapher/people-fully-vaccinated-covid.csv?tab=table"

    ]

    counts = None

    errors = []

    for url in count_urls:

        try:

            counts = _read_csv_api(url)

            break

        except Exception as exc:

            errors.append(

                f"{url}: {type(exc).__name__}: {exc}"

            )

    if counts is None:

        raise RuntimeError(

            "Vaccination count API could not be reached. "

            + " | ".join(errors[-2:])

        )

    normalized = {

        str(column).strip().lower().replace(" ", "_"): column

        for column in counts.columns

    }

    entity_col = next(

        (

            normalized[key]

            for key in ("entity", "location")

            if key in normalized

        ),

        None

    )

    date_col = next(

        (

            normalized[key]

            for key in ("day", "date")

            if key in normalized

        ),

        None

    )

    count_col = next(

        (

            column

            for key, column in normalized.items()

            if "people_fully_vaccinated" in key

        ),

        None

    )

    if not entity_col or not date_col or not count_col:

        raise ValueError(

            f"Unexpected OWID vaccination count schema: "

            f"{list(counts.columns)}"

        )

    out = counts[

        [entity_col, date_col, count_col]

    ].copy()

    out.columns = [

        "country",

        "date",

        "people_fully_vaccinated"

    ]

    out["date"] = pd.to_datetime(

        out["date"],

        errors="coerce"

    )

    out["people_fully_vaccinated"] = pd.to_numeric(

        out["people_fully_vaccinated"],

        errors="coerce"

    )

    out["country"] = out["country"].astype(str).str.strip()

    share_urls = [

        OWID_VACCINATION_SHARE_URL,

        "https://ourworldindata.org/grapher/share-people-fully-vaccinated-covid.csv"

    ]

    for url in share_urls:

        try:

            shares = _read_csv_api(url)

            cols = {

                str(column).strip().lower().replace(" ", "_"): column

                for column in shares.columns

            }

            entity = next(

                (

                    cols[key]

                    for key in ("entity", "location")

                    if key in cols

                ),

                None

            )

            date = next(

                (

                    cols[key]

                    for key in ("day", "date")

                    if key in cols

                ),

                None

            )

            value = next(

                (

                    column

                    for key, column in cols.items()

                    if "fully_vaccinated" in key

                    and (

                        "per_hundred" in key

                        or "share" in key

                    )

                ),

                None

            )

            if entity and date and value:

                share_data = shares[

                    [entity, date, value]

                ].copy()

                share_data.columns = [

                    "country",

                    "date",

                    "fully_vaccinated_pct"

                ]

                share_data["country"] = (

                    share_data["country"].astype(str).str.strip()

                )

                share_data["date"] = pd.to_datetime(

                    share_data["date"],

                    errors="coerce"

                )

                share_data["fully_vaccinated_pct"] = pd.to_numeric(

                    share_data["fully_vaccinated_pct"],

                    errors="coerce"

                )

                out = out.merge(

                    share_data,

                    on=["country", "date"],

                    how="outer"

                )

                break

        except Exception:

            continue

    if "fully_vaccinated_pct" not in out.columns:

        out["fully_vaccinated_pct"] = np.nan

    return (

        out.dropna(subset=["date"])

        .sort_values(["country", "date"])

    )

@st.cache_data(ttl=3600, show_spinner=False)

def load_source(prefer_online=True):

    if prefer_online:

        for url in (

            OWID_COMPACT_URL,

            OWID_LEGACY_URL

        ):

            try:

                raw = pd.read_csv(

                    url,

                    low_memory=False

                )

                if {"location", "date"}.issubset(raw.columns):

                    return (

                        normalize_owid(raw),

                        "online",

                        url

                    )

            except Exception:

                continue

    if not LOCAL_PATH.exists():

        raise FileNotFoundError(

            f"Historical dataset not found: {LOCAL_PATH}"

        )

    local = pd.read_csv(

        LOCAL_PATH,

        parse_dates=["date"]

    )

    local["country"] = (

        local["country"].astype(str).str.strip()

    )

    required_columns = [

        "total_cases",

        "total_deaths",

        "total_recovered",

        "daily_cases",

        "daily_deaths",

        "daily_recovered",

        "daily_cases_chart",

        "daily_deaths_chart",

        "cases_7d_avg",

        "deaths_7d_avg",

        "cfr_percent",

        "active_estimate"

    ]

    for column in required_columns:

        if column not in local.columns:

            local[column] = np.nan

    local["people_vaccinated"] = np.nan

    local["people_fully_vaccinated"] = np.nan

    local["total_vaccinations"] = np.nan

    local["population"] = np.nan

    return (

        local,

        "historical",

        str(LOCAL_PATH)

    )

def normalize_owid(raw):

    data = raw.copy()

    if "location" in data.columns:

        data = data.rename(

            columns={"location": "country"}

        )

    data = data.rename(

        columns={

            "new_cases": "daily_cases",

            "new_deaths": "daily_deaths",

            "new_vaccinations": "daily_vaccinations",

            "total_people_fully_vaccinated": "people_fully_vaccinated",

            "total_people_vaccinated": "people_vaccinated",

            "total_population": "population",

            "people_fully_vaccinated_per_hundred": "fully_vaccinated_pct"

        }

    )

    data["date"] = pd.to_datetime(

        data["date"],

        errors="coerce"

    )

    numeric_columns = [

        "total_cases",

        "total_deaths",

        "new_cases",

        "new_deaths",

        "total_vaccinations",

        "people_vaccinated",

        "people_fully_vaccinated",

        "population",

        "new_vaccinations",

        "people_vaccinated_per_hundred",

        "people_fully_vaccinated_per_hundred",

        "total_vaccinations_per_hundred",

        "fully_vaccinated_pct",

        "new_cases_smoothed",

        "new_deaths_smoothed"

    ]

    for column in numeric_columns:

        if column in data.columns:

            data[column] = pd.to_numeric(

                data[column],

                errors="coerce"

            )

    required_numeric_columns = [

        "total_cases",

        "total_deaths",

        "daily_cases",

        "daily_deaths",

        "total_vaccinations",

        "people_vaccinated",

        "people_fully_vaccinated",

        "population",

        "daily_vaccinations",

        "fully_vaccinated_pct"

    ]

    for column in required_numeric_columns:

        if column not in data.columns:

            data[column] = np.nan

        data[column] = pd.to_numeric(

            data[column],

            errors="coerce"

        )

    data = data[

        data["date"].notna()

        & data["country"].notna()

    ].copy()

    data = data[

        ~data["country"].isin(

            ["World", "European Union", "International"]

        )

    ]

    data = data.sort_values(

        ["country", "date"]

    )

    data["daily_cases_chart"] = (

        pd.to_numeric(

            data["daily_cases"],

            errors="coerce"

        ).clip(lower=0)

    )

    data["daily_deaths_chart"] = (

        pd.to_numeric(

            data["daily_deaths"],

            errors="coerce"

        ).clip(lower=0)

    )

    if "new_cases_smoothed" in data.columns:

        data["cases_7d_avg"] = pd.to_numeric(

            data["new_cases_smoothed"],

            errors="coerce"

        )

    else:

        data["cases_7d_avg"] = (

            data.groupby("country")["daily_cases_chart"]

            .transform(

                lambda series: series.rolling(

                    7,

                    min_periods=1

                ).mean()

            )

        )

    if "new_deaths_smoothed" in data.columns:

        data["deaths_7d_avg"] = pd.to_numeric(

            data["new_deaths_smoothed"],

            errors="coerce"

        )

    else:

        data["deaths_7d_avg"] = (

            data.groupby("country")["daily_deaths_chart"]

            .transform(

                lambda series: series.rolling(

                    7,

                    min_periods=1

                ).mean()

            )

        )

    data["total_recovered"] = np.nan

    data["cfr_percent"] = np.where(

        data["total_cases"] > 0,

        data["total_deaths"] / data["total_cases"] * 100,

        np.nan

    )

    data["active_estimate"] = np.nan

    if "continent" not in data.columns:

        data["continent"] = pd.Series(

            index=data.index,

            dtype="object"

        )

    data["continent"] = (

        data["continent"]

        .fillna(data["country"].map(CONTINENT_BY_COUNTRY))

        .fillna("Other / not mapped")

    )

    return data

CONTINENTS = {

    "Asia": (

        "Afghanistan Armenia Azerbaijan Bahrain Bangladesh Bhutan Brunei Cambodia China Cyprus Georgia India Indonesia Iran Iraq Israel Japan Jordan Kazakhstan Kuwait Kyrgyzstan Laos Lebanon Malaysia Maldives Mongolia Myanmar Nepal North Korea Oman Pakistan Palestine Philippines Qatar Saudi Arabia Singapore South Korea Sri Lanka Syria Taiwan Tajikistan Thailand Timor-Leste Turkey Turkmenistan United Arab Emirates Uzbekistan Vietnam Yemen"

    ).split(),

    "Europe": (

        "Albania Andorra Austria Belarus Belgium Bosnia and Herzegovina Bulgaria Croatia Czechia Denmark Estonia Finland France Germany Greece Hungary Iceland Ireland Italy Kosovo Latvia Liechtenstein Lithuania Luxembourg Malta Moldova Monaco Montenegro Netherlands North Macedonia Norway Poland Portugal Romania Russia San Marino Serbia Slovakia Slovenia Spain Sweden Switzerland Ukraine United Kingdom Vatican City"

    ).split(),

    "Africa": (

        "Algeria Angola Benin Botswana Burkina Faso Burundi Cabo Verde Cameroon Central African Republic Chad Comoros Congo Democratic Republic of the Congo Djibouti Egypt Equatorial Guinea Eritrea Eswatini Ethiopia Gabon Gambia Ghana Guinea Guinea-Bissau Ivory Coast Kenya Lesotho Liberia Libya Madagascar Malawi Mali Mauritania Mauritius Morocco Mozambique Namibia Niger Nigeria Rwanda Sao Tome and Principe Senegal Seychelles Sierra Leone Somalia South Africa South Sudan Sudan Tanzania Togo Tunisia Uganda Zambia Zimbabwe"

    ).split(),

    "North America": (

        "Antigua and Barbuda Bahamas Barbados Belize Canada Costa Rica Cuba Dominica Dominican Republic El Salvador Grenada Guatemala Haiti Honduras Jamaica Mexico Nicaragua Panama Saint Kitts and Nevis Saint Lucia Saint Vincent and the Grenadines Trinidad and Tobago US United States"

    ).split(),

    "South America": (

        "Argentina Bolivia Brazil Chile Colombia Ecuador Guyana Paraguay Peru Suriname Uruguay Venezuela"

    ).split(),

    "Oceania": (

        "Australia Fiji Kiribati Marshall Islands Micronesia Nauru New Zealand Palau Papua New Guinea Samoa Solomon Islands Tonga Tuvalu Vanuatu"

    ).split()

}

CONTINENT_BY_COUNTRY = {

    country: continent

    for continent, countries in CONTINENTS.items()

    for country in countries

}

NAVY = "#08152d"

BLUE = "#2f8cff"

CYAN = "#21d4e5"

RED = "#ff4f78"

GREEN = "#25d6a0"

PURPLE = "#9674ff"

GOLD = "#ffbd59"

st.markdown(

    """

    <style>

    .stApp {

        background: radial-gradient(

            ellipse at 70% 0%,

            #173b52 0%,

            #0b1c2b 48%,

            #07131f 100%

        );

        color: #e8f1f7;

    }

    [data-testid="stHeader"] {

        background: rgba(7, 19, 31, .96);

    }

    .block-container {

        padding: 1.65rem 1.55rem 2rem;

        max-width: 1900px;

        overflow: visible;

    }

    section[data-testid="stSidebar"] {

        background: linear-gradient(

            180deg,

            #102b43,

            #081827

        );

        border-right: 1px solid #31546b;

    }

    section[data-testid="stSidebar"] * {

        color: #eaf2ff;

    }

    h1, h2, h3 {

        color: #f1f7fb;

    }

    p, label, .stCaption {

        color: #c0d0dc;

    }

    .hero {

        display: block;

        position: relative;

        overflow: visible;

        background: linear-gradient(

            120deg,

            #17435b,

            #17616b

        );

        border: 1px solid #3d8390;

        border-radius: 15px;

        padding: 25px 27px 23px;

        margin: 8px 0 18px;

        box-shadow: 0 10px 26px rgba(0, 0, 0, .28);

    }

    .hero h1 {

        color: #ffffff !important;

        font-size: clamp(

            1.65rem,

            2.5vw,

            2.35rem

        ) !important;

        line-height: 1.25 !important;

        margin: 0 0 8px !important;

        padding-top: 2px;

        text-shadow: 0 1px 1px rgba(0, 0, 0, .2);

    }

    .hero-sub {

        color: #d9edf2 !important;

        font-size: 15px;

        line-height: 1.55;

    }

    .kicker {

        display: none;

    }

    .panel-title {

        font-size: 17px;

        font-weight: 750;

        color: #eaf4f8;

        margin: 0 0 8px;

    }

    .block-container [data-testid="stMetric"] {

        background: linear-gradient(

            145deg,

            #18364d,

            #10283b

        );

        border: 1px solid #315c73;

        border-radius: 14px;

        padding: 16px 18px;

        min-height: 112px;

        box-shadow: 0 8px 20px rgba(0, 0, 0, .22);

        transition: transform .2s, box-shadow .2s;

    }

    .block-container [data-testid="stMetric"]:hover {

        border-color: #4d9bad;

        box-shadow: 0 12px 25px rgba(0, 0, 0, .3);

        transform: translateY(-2px);

    }

    div[data-testid="stMetricLabel"],

    div[data-testid="stMetricLabel"] p {

        color: #b9d0dc !important;

    }

    div[data-testid="stMetricValue"],

    div[data-testid="stMetricValue"] div {

        color: #ffffff !important;

    }

    div[data-testid="stMetricDelta"] {

        color: #8fe5c7 !important;

    }

    .block-container [data-testid="stPlotlyChart"] {

        background: linear-gradient(

            145deg,

            #122b40,

            #0d2234

        );

        border: 1px solid #31566d;

        border-radius: 14px;

        padding: 8px;

        box-shadow: 0 8px 20px rgba(0, 0, 0, .22);

    }

    div[data-testid="stDataFrame"] {

        border: 1px solid #31566d;

        border-radius: 12px;

    }

    [data-testid="stDataFrame"] * {

        color: #e6f0f5;

    }

    .stSelectbox > div > div,

    .stMultiSelect > div > div,

    .stDateInput > div > div {

        background: #10283b;

        color: #f2f7fa;

        border-color: #3a6177;

    }

    div.stButton > button,

    div[data-testid="stDownloadButton"] button {

        border-radius: 10px;

        border: 1px solid #4b8295;

        background: #16465a;

        color: #f4fbff;

    }

    div.stButton > button:hover,

    div[data-testid="stDownloadButton"] button:hover {

        background: #1d6070;

        border-color: #73b9c4;

        color: white;

    }

    .note {

        background: #12354a;

        border: 1px solid #37687a;

        border-left: 4px solid #e2ad55;

        padding: 12px 14px;

        border-radius: 9px;

        color: #dcebf1;

    }

    .status {

        display: inline-block;

        border: 1px solid #397b83;

        background: #0c403f;

        color: #80f2ce;

        padding: 4px 9px;

        border-radius: 999px;

        font-size: 11px;

    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {

        padding: 4px 2px;

    }

    [data-testid="stAlert"] {

        background: #15364a;

        color: #e9f3f8;

        border: 1px solid #416c80;

    }

    </style>

    """,

    unsafe_allow_html=True

)

with st.sidebar:

    st.markdown("## 🌐 COVID-19")

    st.markdown("**Global Impact Dashboard**")

    st.caption("Interactive analytics")

    page = st.radio(

        "NAVIGATION",

        [

            "Overview",

            "Global Trends",

            "Country Comparison",

            "Vaccination Analysis",

            "Data Explorer",

            "Key Insights"

        ],

        index=0,

        label_visibility="visible"

    )

    st.markdown("---")

    st.markdown("### Dashboard filters")

    if st.button(

        "↻ Refresh online data",

        width="stretch"

    ):

        load_source.clear()

        load_vaccination_source.clear()

        st.rerun()

    if st.button(

        "Reset date and country filters",

        width="stretch"

    ):

        for state_key in [

            "covid_date_range_v4",

            "covid_continent_filter",

            "covid_country_filter"

        ]:

            st.session_state.pop(state_key, None)

        st.rerun()

    df, source_mode, source_used = load_source(True)

    if (

        df.empty

        or "date" not in df.columns

        or "country" not in df.columns

    ):

        st.error(

            "The selected COVID-19 data source returned "

            "no usable country-date records."

        )

        st.stop()

    df["country"] = (

        df["country"].astype(str).str.strip()

    )

    if "continent" not in df or df["continent"].isna().all():

        df["continent"] = (

            df["country"]

            .map(CONTINENT_BY_COUNTRY)

            .fillna("Other / not mapped")

        )

    else:

        fallback = df["country"].map(

            CONTINENT_BY_COUNTRY

        )

        df["continent"] = (

            df["continent"]

            .fillna(fallback)

            .fillna("Other / not mapped")

        )

    df = df[

        df.country.str.lower() != "world"

    ].copy()

    vaccination_mode = "unavailable"

    vaccination_source = None

    vaccination_data = pd.DataFrame(

        columns=[

            "country",

            "date",

            "people_fully_vaccinated",

            "fully_vaccinated_pct"

        ]

    )

    try:

        vaccination_data = load_vaccination_source()

        vaccination_mode = "online"

        merge_columns = [

            "country",

            "date",

            "people_fully_vaccinated",

            "fully_vaccinated_pct"

        ]

        df = df.merge(

            vaccination_data[merge_columns],

            on=["country", "date"],

            how="left",

            suffixes=("", "_vax")

        )

        for column in [

            "people_fully_vaccinated",

            "fully_vaccinated_pct"

        ]:

            api_column = column + "_vax"

            if api_column in df.columns:

                if column not in df.columns:

                    df[column] = df[api_column]

                else:

                    df[column] = (

                        df[column].combine_first(

                            df[api_column]

                        )

                    )

                df.drop(

                    columns=[api_column],

                    inplace=True

                )

        vaccination_source = OWID_VACCINATION_URL

    except Exception as vaccination_error:

        vaccination_columns = [

            column

            for column in [

                "people_fully_vaccinated",

                "fully_vaccinated_pct"

            ]

            if column in df.columns

        ]

        if (

            vaccination_columns

            and df[vaccination_columns].notna().any().any()

        ):

            keep_columns = [

                "country",

                "date"

            ] + vaccination_columns

            vaccination_data = df[keep_columns].copy()

            if "people_fully_vaccinated" not in vaccination_data:

                vaccination_data["people_fully_vaccinated"] = np.nan

            if "fully_vaccinated_pct" not in vaccination_data:

                vaccination_data["fully_vaccinated_pct"] = np.nan

            vaccination_mode = "primary source fallback"

        else:

            vaccination_mode = "unavailable"

            vaccination_error_message = (

                f"{type(vaccination_error).__name__}: "

                f"{vaccination_error}"

            )

    dmin = df.date.min().date()

    vax_max = (

        pd.to_datetime(

            vaccination_data["date"],

            errors="coerce"

        ).max()

        if not vaccination_data.empty

        else pd.NaT

    )

    dmax = (

        max(df.date.max(), vax_max).date()

        if pd.notna(vax_max)

        else df.date.max().date()

    )

    date_range = st.date_input(

        "Date range",

        value=(dmin, dmax),

        min_value=dmin,

        max_value=dmax,

        key="covid_date_range_v4"

    )

    if (

        isinstance(date_range, (tuple, list))

        and len(date_range) == 2

    ):

        start, end = (

            pd.Timestamp(date_range[0]),

            pd.Timestamp(date_range[1])

        )

    else:

        start, end = (

            pd.Timestamp(dmin),

            pd.Timestamp(dmax)

        )

    continent_options = (

        ["All"]

        + sorted(df.continent.dropna().unique().tolist())

    )

    continent = st.selectbox(

        "Continent",

        continent_options,

        index=0,

        key="covid_continent_filter"

    )

    scope = (

        df

        if continent == "All"

        else df[df.continent == continent]

    )

    country_options = sorted(

        scope.country.unique().tolist()

    )

    selected = st.multiselect(

        "Country (optional)",

        country_options,

        default=[],

        key="covid_country_filter"

    )

    st.markdown("---")

    if source_mode == "online":

        st.markdown(

            '<span class="status">● Online source loaded</span>',

            unsafe_allow_html=True

        )

        st.caption(

            "OWID cases/deaths catalog + dedicated vaccination API "

            "• 1-hour cache"

        )

    else:

        st.markdown(

            '<span class="status" style="background:#55401b;'

            'border-color:#9b7735;color:#ffe0a1">'

            '● Historical fallback</span>',

            unsafe_allow_html=True

        )

        st.caption(

            "Original supplied data used for cases/deaths. "

            "Vaccination API is fetched separately when internet is available."

        )

    st.caption(

        f"Data coverage: {dmin:%d %b %Y} – {dmax:%d %b %Y}"

    )

date_view = df[

    (df.date >= start)

    & (df.date <= end)

]

if continent != "All":

    date_view = date_view[

        date_view.continent == continent

    ]

if selected:

    date_view = date_view[

        date_view.country.isin(selected)

    ]

latest_rows = (

    date_view.sort_values("date")

    .groupby("country", as_index=False)

    .tail(1)

)

global_daily = (

    df.groupby("date", as_index=False)[

        [

            "daily_cases_chart",

            "daily_deaths_chart",

            "total_cases",

            "total_deaths"

        ]

    ].sum(min_count=1)

)

global_daily = global_daily[

    (global_daily.date >= start)

    & (global_daily.date <= end)

]

if continent != "All":

    global_daily = (

        date_view.groupby("date", as_index=False)[

            [

                "daily_cases_chart",

                "daily_deaths_chart",

                "total_cases",

                "total_deaths"

            ]

        ].sum(min_count=1)

    )

elif selected:

    global_daily = (

        date_view.groupby("date", as_index=False)[

            [

                "daily_cases_chart",

                "daily_deaths_chart",

                "total_cases",

                "total_deaths"

            ]

        ].sum(min_count=1)

    )

global_latest = latest_rows[

    [

        "total_cases",

        "total_deaths",

        "total_recovered"

    ]

].sum(min_count=1)

def val(value):

    return 0 if pd.isna(value) else float(value)

def fmt(value):

    value = val(value)

    if value >= 1_000_000_000:

        return f"{value / 1_000_000_000:.2f}B"

    if value >= 1_000_000:

        return f"{value / 1_000_000:.2f}M"

    return f"{value:,.0f}"

def dark(fig, height=340):

    fig.update_layout(

        height=height,

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(

            color="#e5f0f5",

            family="Arial",

            size=12

        ),

        title=dict(

            font=dict(

                color="#f2f8fb",

                size=16

            )

        ),

        margin=dict(

            l=24,

            r=22,

            t=48,

            b=25

        ),

        legend=dict(

            orientation="h",

            y=1.12,

            x=0,

            font=dict(color="#dceaf0")

        ),

        hoverlabel=dict(

            bgcolor="#10283b",

            font=dict(color="#ffffff")

        ),

        hovermode="x unified"

    )

    fig.update_xaxes(

        gridcolor="#29485d",

        linecolor="#527287",

        zerolinecolor="#35566b",

        tickfont=dict(color="#c6d8e2"),

        title_font=dict(color="#e5f0f5")

    )

    fig.update_yaxes(

        gridcolor="#29485d",

        linecolor="#527287",

        zerolinecolor="#35566b",

        tickfont=dict(color="#c6d8e2"),

        title_font=dict(color="#e5f0f5")

    )

    return fig

def header(title, subtitle):

    st.markdown(

        f'<div class="hero">'

        f'<h1>{title}</h1>'

        f'<div class="hero-sub">{subtitle}</div>'

        f'</div>',

        unsafe_allow_html=True

    )

def chart_country_snapshot(metric):

    snapshot = (

        latest_rows.groupby(

            "country",

            as_index=False

        )[metric]

        .sum(min_count=1)

        .dropna()

    )

    return (

        snapshot.nlargest(10, metric)

        .sort_values(metric)

    )

if page == "Overview":

    header(

        "COVID-19 Global Impact Dashboard",

        "Cases, deaths, recoveries and vaccination indicators "

        "• historical and online data"

    )

    k1, k2, k3, k4 = st.columns(4)

    cases = global_latest.get(

        "total_cases",

        np.nan

    )

    deaths = global_latest.get(

        "total_deaths",

        np.nan

    )

    rec = global_latest.get(

        "total_recovered",

        np.nan

    )

    cfr = (

        val(deaths) / val(cases) * 100

        if val(cases) > 0

        else np.nan

    )

    k1.metric(

        "Confirmed cases",

        fmt(cases)

    )

    k2.metric(

        "Reported deaths",

        fmt(deaths),

        f"CFR {cfr:.2f}%" if pd.notna(cfr) else "Not available"

    )

    world_vax_count = None

    world_vax_share = None

    try:

        vax_world = load_vaccination_source()

        vax_world = vax_world[

            (vax_world.country.str.lower() == "world")

            & (vax_world.date <= end)

        ]

        valid_count = vax_world.dropna(

            subset=["people_fully_vaccinated"]

        )

        if not valid_count.empty:

            world_vax_count = float(

                valid_count.sort_values("date")

                .iloc[-1]["people_fully_vaccinated"]

            )

        valid_share = vax_world.dropna(

            subset=["fully_vaccinated_pct"]

        )

        if not valid_share.empty:

            world_vax_share = float(

                valid_share.sort_values("date")

                .iloc[-1]["fully_vaccinated_pct"]

            )

    except Exception:

        pass

    if world_vax_count is not None:

        k3.metric(

            "People fully vaccinated",

            fmt(world_vax_count),

            (

                f"{world_vax_share:.1f}% of world population"

                if world_vax_share is not None

                else "Latest reported global total"

            )

        )

    elif (

        "fully_vaccinated_pct" in latest_rows

        and latest_rows["fully_vaccinated_pct"].notna().any()

    ):

        percentage = float(

            latest_rows["fully_vaccinated_pct"]

            .dropna()

            .iloc[-1]

        )

        k3.metric(

            "Fully vaccinated coverage",

            f"{percentage:.1f}%",

            "Latest available country record"

        )

    else:

        k3.metric(

            "People fully vaccinated",

            "Data unavailable",

            "Check internet and refresh source"

        )

    k4.metric(

        "Countries / regions",

        f"{latest_rows.country.nunique():,}"

    )

    left, right = st.columns([1.45, 1])

    with left:

        st.markdown(

            '<div class="panel-title">'

            '▰ Global trend • 7-day average</div>',

            unsafe_allow_html=True

        )

        fig = go.Figure()

        fig.add_trace(

            go.Scatter(

                x=global_daily.date,

                y=global_daily.daily_cases_chart.rolling(

                    7,

                    min_periods=1

                ).mean(),

                name="New cases",

                line=dict(

                    color=BLUE,

                    width=3

                ),

                fill="tozeroy",

                fillcolor="rgba(47,140,255,.13)"

            )

        )

        fig.add_trace(

            go.Scatter(

                x=global_daily.date,

                y=global_daily.daily_deaths_chart.rolling(

                    7,

                    min_periods=1

                ).mean(),

                name="New deaths",

                line=dict(

                    color=RED,

                    width=2.5

                )

            )

        )

        fig.update_layout(

            title="Reported daily counts",

            yaxis_title="Count"

        )

        st.plotly_chart(

            dark(fig, 360),

            width="stretch"

        )

    with right:

        st.markdown(

            '<div class="panel-title">'

            '▰ Country distribution</div>',

            unsafe_allow_html=True

        )

        snapshot = (

            latest_rows.groupby(

                "country",

                as_index=False

            ).total_cases

            .sum(min_count=1)

            .dropna()

        )

        fig = px.choropleth(

            snapshot,

            locations="country",

            locationmode="country names",

            color="total_cases",

            color_continuous_scale=[

                "#18385f",

                "#2677d8",

                "#21d4e5",

                "#ffbd59",

                "#ff4f78"

            ],

            title="Cumulative confirmed cases"

        )

        fig.update_layout(

            geo=dict(

                bgcolor="rgba(0,0,0,0)",

                showframe=False,

                showcoastlines=True,

                coastlinecolor="#6d91a5",

                landcolor="#19394e"

            ),

            margin=dict(

                l=0,

                r=0,

                t=48,

                b=0

            )

        )

        st.plotly_chart(

            dark(fig, 360),

            width="stretch"

        )

    a, b, c = st.columns([1, 1, 1.2])

    with a:

        st.markdown(

            '<div class="panel-title">'

            'Top countries • cases</div>',

            unsafe_allow_html=True

        )

        top = chart_country_snapshot("total_cases")

        fig = px.bar(

            top,

            x="total_cases",

            y="country",

            orientation="h",

            color_discrete_sequence=[BLUE]

        )

        st.plotly_chart(

            dark(fig, 290),

            width="stretch"

        )

    with b:

        st.markdown(

            '<div class="panel-title">'

            'Top countries • deaths</div>',

            unsafe_allow_html=True

        )

        top = chart_country_snapshot("total_deaths")

        fig = px.bar(

            top,

            x="total_deaths",

            y="country",

            orientation="h",

            color_discrete_sequence=[RED]

        )

        st.plotly_chart(

            dark(fig, 290),

            width="stretch"

        )

    with c:

        st.markdown(

            '<div class="panel-title">'

            'Country metrics snapshot</div>',

            unsafe_allow_html=True

        )

        snapshot = (

            latest_rows.groupby(

                "country",

                as_index=False

            )[

                [

                    "total_cases",

                    "total_deaths",

                    "people_fully_vaccinated"

                ]

            ]

            .sum(min_count=1)

            .sort_values(

                "total_cases",

                ascending=False

            )

            .head(8)

        )

        snapshot = snapshot.rename(

            columns={

                "country": "Country",

                "total_cases": "Cases",

                "total_deaths": "Deaths",

                "people_fully_vaccinated": "Fully vaccinated"

            }

        )

        st.dataframe(

            snapshot,

            hide_index=True,

            width="stretch",

            height=270

        )

    st.markdown(

        '<div class="note">'

        '3D-inspired interface uses layered cards, depth shadows '

        'and interactive charts. COVID-19 reporting is periodic; '

        '“online” means the connected source was fetched, not '

        'real-time clinical surveillance.'

        '</div>',

        unsafe_allow_html=True

    )

elif page == "Global Trends":

    header(

        "Global Trends",

        "Explore reported cases, deaths and cumulative trends"

    )

    metric = st.selectbox(

        "Trend measure",

        [

            "7-day average",

            "Daily reported",

            "Cumulative"

        ]

    )

    fig = go.Figure()

    if metric == "Cumulative":

        fig.add_trace(

            go.Scatter(

                x=global_daily.date,

                y=global_daily.total_cases,

                name="Cases",

                line=dict(

                    color=BLUE,

                    width=3

                )

            )

        )

        fig.add_trace(

            go.Scatter(

                x=global_daily.date,

                y=global_daily.total_deaths,

                name="Deaths",

                line=dict(

                    color=RED,

                    width=3

                )

            )

        )

    else:

        cases = global_daily.daily_cases_chart

        deaths = global_daily.daily_deaths_chart

        if metric == "7-day average":

            cases = cases.rolling(

                7,

                min_periods=1

            ).mean()

            deaths = deaths.rolling(

                7,

                min_periods=1

            ).mean()

        fig.add_trace(

            go.Scatter(

                x=global_daily.date,

                y=cases,

                name="Cases",

                line=dict(

                    color=BLUE,

                    width=3

                )

            )

        )

        fig.add_trace(

            go.Scatter(

                x=global_daily.date,

                y=deaths,

                name="Deaths",

                line=dict(

                    color=RED,

                    width=2.5

                )

            )

        )

    fig.update_layout(

        title=metric + " • global",

        yaxis_title="Reported count"

    )

    st.plotly_chart(

        dark(fig, 460),

        width="stretch"

    )

    monthly = (

        global_daily.assign(

            month=global_daily.date.dt.to_period("M").astype(str)

        )

        .groupby(

            "month",

            as_index=False

        )[

            [

                "daily_cases_chart",

                "daily_deaths_chart"

            ]

        ]

        .sum()

    )

    monthly_fig = px.bar(

        monthly,

        x="month",

        y=[

            "daily_cases_chart",

            "daily_deaths_chart"

        ],

        barmode="group",

        title="Monthly reported counts",

        color_discrete_map={

            "daily_cases_chart": BLUE,

            "daily_deaths_chart": RED

        }

    )

    st.plotly_chart(

        dark(monthly_fig, 350),

        width="stretch"

    )

elif page == "Country Comparison":

    header(

        "Country Comparison",

        "Compare countries with an interactive 3D metric view"

    )

    if date_view.empty:

        st.info("No rows match these filters.")

    else:

        latest = (

            date_view.sort_values("date")

            .groupby("country")

            .tail(1)

            .copy()

        )

        latest = latest.dropna(

            subset=[

                "total_cases",

                "total_deaths"

            ]

        )

        latest["CFR"] = (

            latest.total_deaths

            / latest.total_cases.replace(0, np.nan)

            * 100

        )

        measure = st.selectbox(

            "3D vertical measure",

            [

                "Total cases",

                "Total deaths",

                "CFR (%)"

            ]

        )

        zcol = {

            "Total cases": "total_cases",

            "Total deaths": "total_deaths",

            "CFR (%)": "CFR"

        }[measure]

        top = latest.nlargest(

            25,

            zcol

        )

        fig = go.Figure(

            data=[

                go.Scatter3d(

                    x=top.total_cases,

                    y=top.total_deaths,

                    z=top[zcol],

                    mode="markers+text",

                    text=top.country,

                    textposition="top center",

                    marker=dict(

                        size=6,

                        color=top[zcol],

                        colorscale="Turbo",

                        opacity=0.88,

                        line=dict(

                            color="#d8eaff",

                            width=1

                        )

                    ),

                    hovertemplate=(

                        "<b>%{text}</b><br>"

                        "Cases: %{x:,.0f}<br>"

                        "Deaths: %{y:,.0f}<br>"

                        + measure

                        + ": %{z:,.2f}<extra></extra>"

                    )

                )

            ]

        )

        fig.update_layout(

            title="3D country comparison • drag to rotate",

            scene=dict(

                xaxis_title="Total cases",

                yaxis_title="Total deaths",

                zaxis_title=measure,

                bgcolor="rgba(0,0,0,0)",

                xaxis=dict(

                    backgroundcolor="#102747",

                    gridcolor="#345575",

                    color="#dceaff"

                ),

                yaxis=dict(

                    backgroundcolor="#102747",

                    gridcolor="#345575",

                    color="#dceaff"

                ),

                zaxis=dict(

                    backgroundcolor="#102747",

                    gridcolor="#345575",

                    color="#dceaff"

                )

            ),

            paper_bgcolor="rgba(0,0,0,0)",

            font=dict(color="#e5efff"),

            height=590,

            margin=dict(

                l=0,

                r=0,

                t=50,

                b=0

            )

        )

        st.plotly_chart(

            fig,

            width="stretch"

        )

        st.dataframe(

            latest[

                [

                    "country",

                    "total_cases",

                    "total_deaths",

                    "CFR"

                ]

            ].sort_values(

                zcol,

                ascending=False

            ),

            hide_index=True,

            width="stretch"

        )

elif page == "Vaccination Analysis":

    header(

        "Vaccination Analysis",

        "Reported full-vaccination counts and population coverage "

        "• OWID source"

    )

    if vaccination_data.empty:

        st.warning(

            "Vaccination records could not be loaded from the online "

            "source. The supplied historical case/death files do not "

            "contain vaccination fields."

        )

        st.info(

            "Connect to the internet and press Refresh online data. "

            "The dashboard will use the dedicated OWID API or "

            "vaccination fields from the live catalog when available."

        )

        if "vaccination_error_message" in globals():

            with st.expander("Technical details"):

                st.code(vaccination_error_message)

    else:

        vacc = vaccination_data.copy()

        vacc = vacc[

            vacc.country.str.lower() != "world"

        ]

        vacc["continent"] = (

            vacc.country

            .map(CONTINENT_BY_COUNTRY)

            .fillna("Other / not mapped")

        )

        vacc = vacc[

            (vacc.date >= start)

            & (vacc.date <= end)

        ]

        if continent != "All":

            vacc = vacc[

                vacc.continent == continent

            ]

        if selected:

            vacc = vacc[

                vacc.country.isin(selected)

            ]

        if vacc.empty:

            st.info(

                "No vaccination observations match the selected "

                "date, continent and country filters."

            )

        else:

            latest_v = (

                vacc.sort_values("date")

                .groupby(

                    "country",

                    as_index=False

                )

                .tail(1)

            )

            total_fully = latest_v[

                "people_fully_vaccinated"

            ].sum(min_count=1)

            latest_count_date = latest_v.loc[

                latest_v.people_fully_vaccinated.notna(),

                "date"

            ].max()

            latest_share = vaccination_data[

                (

                    vaccination_data.country.str.lower()

                    == "world"

                )

                & (vaccination_data.date <= end)

            ].dropna(

                subset=["fully_vaccinated_pct"]

            )

            share_value = (

                float(

                    latest_share.sort_values("date")

                    .iloc[-1]

                    .fully_vaccinated_pct

                )

                if not latest_share.empty

                else np.nan

            )

            m1, m2, m3 = st.columns(3)

            m1.metric(

                "Fully vaccinated people",

                fmt(total_fully),

                (

                    f"Latest country observations through "

                    f"{latest_count_date:%d %b %Y}"

                    if pd.notna(latest_count_date)

                    else "No count date"

                )

            )

            m2.metric(

                "Global coverage",

                (

                    f"{share_value:.1f}%"

                    if pd.notna(share_value)

                    else "Not reported"

                ),

                "World population • latest available"

            )

            m3.metric(

                "Countries with data",

                f"{latest_v.country.nunique():,}"

            )

            metric_options = [

                "Fully vaccinated people",

                "Fully vaccinated (% population)"

            ]

            vmetric = st.selectbox(

                "Vaccination metric",

                metric_options

            )

            vcol = {

                "Fully vaccinated people": "people_fully_vaccinated",

                "Fully vaccinated (% population)": "fully_vaccinated_pct"

            }[vmetric]

            vdata = vacc.dropna(

                subset=[vcol]

            )

            if vdata.empty:

                st.info(

                    f"{vmetric} is not reported for the selected "

                    "filter/date range."

                )

            else:

                left, right = st.columns([1.35, 1])

                with left:

                    if (

                        vcol == "fully_vaccinated_pct"

                        and continent == "All"

                        and not selected

                    ):

                        trend = vaccination_data[

                            (

                                vaccination_data.country.str.lower()

                                == "world"

                            )

                            & (vaccination_data.date >= start)

                            & (vaccination_data.date <= end)

                        ].dropna(

                            subset=[vcol]

                        )

                        fig = px.area(

                            trend,

                            x="date",

                            y=vcol,

                            title="Global share of people fully vaccinated"

                        )

                        fig.update_traces(

                            line_color=GREEN,

                            fillcolor="rgba(37,214,160,.18)"

                        )

                    else:

                        fig = px.line(

                            vdata,

                            x="date",

                            y=vcol,

                            color="country",

                            title=vmetric + " over time",

                            line_group="country"

                        )

                    st.plotly_chart(

                        dark(fig, 410),

                        width="stretch"

                    )

                with right:

                    last = (

                        vdata.sort_values("date")

                        .groupby(

                            "country",

                            as_index=False

                        )

                        .tail(1)

                        .dropna(subset=[vcol])

                    )

                    top = (

                        last.nlargest(12, vcol)

                        .sort_values(vcol)

                    )

                    bar = px.bar(

                        top,

                        x=vcol,

                        y="country",

                        orientation="h",

                        title="Latest reported by country",

                        color_discrete_sequence=[GREEN]

                    )

                    st.plotly_chart(

                        dark(bar, 410),

                        width="stretch"

                    )

                st.caption(

                    "OWID vaccination data is an official-source "

                    "compilation. The dedicated vaccination series "

                    "is historical and is not updated at the same "

                    "frequency as the cases/deaths catalog."

                )

                display_columns = [

                    column

                    for column in [

                        "country",

                        "date",

                        "people_fully_vaccinated",

                        "fully_vaccinated_pct"

                    ]

                    if column in latest_v.columns

                ]

                st.dataframe(

                    latest_v[display_columns].sort_values(

                        "people_fully_vaccinated",

                        ascending=False,

                        na_position="last"

                    ),

                    hide_index=True,

                    width="stretch",

                    height=280

                )

elif page == "Data Explorer":

    header(

        "Data Explorer",

        "Inspect and export the filtered country-date data"

    )

    columns = [

        column

        for column in [

            "country",

            "continent",

            "date",

            "total_cases",

            "total_deaths",

            "total_recovered",

            "daily_cases",

            "daily_deaths",

            "cases_7d_avg",

            "deaths_7d_avg",

            "people_vaccinated",

            "people_fully_vaccinated",

            "fully_vaccinated_pct",

            "total_vaccinations",

            "population",

            "cfr_percent",

            "active_estimate"

        ]

        if column in date_view.columns

    ]

    st.caption(

        f"{len(date_view):,} records • Source: "

        f"{'online OWID' if source_mode == 'online' else 'supplied historical data'}"

    )

    view = (

        date_view[columns]

        .sort_values(

            ["date", "country"],

            ascending=[False, True]

        )

    )

    st.dataframe(

        view,

        width="stretch",

        hide_index=True,

        height=520

    )

    st.download_button(

        "Download filtered CSV",

        view.to_csv(index=False).encode("utf-8"),

        "covid_filtered_data.csv",

        "text/csv"

    )

else:

    header(

        "Key Insights",

        "Descriptive observations based on the selected data and filters"

    )

    if date_view.empty:

        st.info(

            "No data available for this selection."

        )

    else:

        latest = (

            date_view.sort_values("date")

            .groupby("country")

            .tail(1)

        )

        top = (

            latest.dropna(subset=["total_cases"])

            .nlargest(1, "total_cases")

        )

        if not top.empty:

            row = top.iloc[0]

            st.markdown(

                f"**Largest cumulative case count in the current "

                f"selection:** {row.country} — "

                f"{row.total_cases:,.0f} on {row.date:%d %b %Y}."

            )

        daily = (

            date_view.groupby(

                "date",

                as_index=False

            )[

                [

                    "daily_cases_chart",

                    "daily_deaths_chart"

                ]

            ].sum(min_count=1)

        )

        for column, label in [

            ("daily_cases_chart", "daily cases"),

            ("daily_deaths_chart", "daily deaths")

        ]:

            series = daily[column].rolling(

                7,

                min_periods=1

            ).mean()

            if series.notna().any():

                index = series.idxmax()

                st.markdown(

                    f"**Peak 7-day average {label}:** "

                    f"{series.loc[index]:,.0f} on "

                    f"{daily.loc[index, 'date']:%d %b %Y}."

                )

        st.markdown(

            '<div class="note">'

            'Reported counts depend on testing, definitions, and '

            'reporting schedules. Country comparisons are descriptive '

            'and do not establish causation.'

            '</div>',

            unsafe_allow_html=True

        )

st.markdown("---")

st.caption(

    f"Cases/deaths source: {source_used} • "

    f"Main source mode: {source_mode} • "

    f"Vaccination source: OWID dedicated series ({vaccination_mode}) • "

    f"Periodic reporting, not real-time clinical surveillance."

)
