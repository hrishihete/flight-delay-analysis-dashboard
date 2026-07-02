from __future__ import annotations

import os
import sqlite3
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("reports") / ".mplconfig"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "bts_on_time_2024_01.zip"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"

RELEVANT_COLUMNS = [
    "YEAR",
    "QUARTER",
    "MONTH",
    "DAY_OF_MONTH",
    "DAY_OF_WEEK",
    "FL_DATE",
    "OP_UNIQUE_CARRIER",
    "OP_CARRIER",
    "OP_CARRIER_FL_NUM",
    "ORIGIN",
    "ORIGIN_CITY_NAME",
    "ORIGIN_STATE_ABR",
    "DEST",
    "DEST_CITY_NAME",
    "DEST_STATE_ABR",
    "CRS_DEP_TIME",
    "DEP_TIME",
    "DEP_DELAY",
    "DEP_DEL15",
    "DEP_TIME_BLK",
    "CRS_ARR_TIME",
    "ARR_TIME",
    "ARR_DELAY",
    "ARR_DEL15",
    "ARR_TIME_BLK",
    "CANCELLED",
    "CANCELLATION_CODE",
    "DIVERTED",
    "CRS_ELAPSED_TIME",
    "ACTUAL_ELAPSED_TIME",
    "AIR_TIME",
    "FLIGHTS",
    "DISTANCE",
    "DISTANCE_GROUP",
    "CARRIER_DELAY",
    "WEATHER_DELAY",
    "NAS_DELAY",
    "SECURITY_DELAY",
    "LATE_AIRCRAFT_DELAY",
]

DELAY_NUMERIC_COLUMNS = [
    "DEP_DELAY",
    "DEP_DEL15",
    "ARR_DELAY",
    "ARR_DEL15",
    "CARRIER_DELAY",
    "WEATHER_DELAY",
    "NAS_DELAY",
    "SECURITY_DELAY",
    "LATE_AIRCRAFT_DELAY",
]

TIME_NUMERIC_COLUMNS = [
    "CRS_DEP_TIME",
    "DEP_TIME",
    "CRS_ARR_TIME",
    "ARR_TIME",
    "CRS_ELAPSED_TIME",
    "ACTUAL_ELAPSED_TIME",
    "AIR_TIME",
    "DISTANCE",
    "DISTANCE_GROUP",
]


def load_data() -> pd.DataFrame:
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Missing source file: {RAW_FILE}")
    return pd.read_csv(RAW_FILE, usecols=RELEVANT_COLUMNS, low_memory=False)


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    before_nulls = df.isna().sum().rename("nulls_before").to_frame()
    cleaned = df.copy()

    for column in DELAY_NUMERIC_COLUMNS + TIME_NUMERIC_COLUMNS + ["CANCELLED", "DIVERTED"]:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    cleaned["DEP_DELAY_WAS_NULL"] = cleaned["DEP_DELAY"].isna().astype(int)
    cleaned["ARR_DELAY_WAS_NULL"] = cleaned["ARR_DELAY"].isna().astype(int)

    # BTS delay-cause fields are null unless the flight arrived 15+ minutes late.
    # For aggregate delay-cause analysis, those nulls correctly become zero minutes.
    delay_cause_columns = [
        "CARRIER_DELAY",
        "WEATHER_DELAY",
        "NAS_DELAY",
        "SECURITY_DELAY",
        "LATE_AIRCRAFT_DELAY",
    ]
    cleaned[delay_cause_columns] = cleaned[delay_cause_columns].fillna(0)

    cleaned["CANCELLATION_CODE"] = cleaned["CANCELLATION_CODE"].fillna("Not Cancelled")

    completed_flights = (cleaned["CANCELLED"].fillna(0) == 0) & (cleaned["DIVERTED"].fillna(0) == 0)
    for column in ["DEP_DELAY", "DEP_DEL15", "ARR_DELAY", "ARR_DEL15"]:
        cleaned.loc[completed_flights, column] = cleaned.loc[completed_flights, column].fillna(0)

    cleaned["FL_DATE"] = pd.to_datetime(cleaned["FL_DATE"], format="%Y-%m-%d", errors="coerce")
    cleaned["IS_COMPLETED_FLIGHT"] = completed_flights.astype(int)
    cleaned["IS_DELAYED_ARRIVAL"] = (cleaned["ARR_DEL15"].fillna(0) == 1).astype(int)
    cleaned["IS_DELAYED_DEPARTURE"] = (cleaned["DEP_DEL15"].fillna(0) == 1).astype(int)

    after_nulls = cleaned.isna().sum().rename("nulls_after").to_frame()
    null_summary = before_nulls.join(after_nulls, how="outer").fillna(0).astype(int)
    null_summary["nulls_removed"] = null_summary["nulls_before"] - null_summary["nulls_after"]
    return cleaned, null_summary


def save_charts(cleaned: pd.DataFrame) -> None:
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    completed = cleaned[cleaned["IS_COMPLETED_FLIGHT"] == 1].copy()

    airline = (
        completed.groupby("OP_UNIQUE_CARRIER", as_index=False)
        .agg(flights=("FLIGHTS", "sum"), arrival_delay_rate=("IS_DELAYED_ARRIVAL", "mean"))
        .query("flights >= 500")
        .sort_values("arrival_delay_rate", ascending=False)
        .head(10)
    )
    airline["arrival_delay_rate"] *= 100
    plt.figure(figsize=(10, 5))
    sns.barplot(data=airline, x="arrival_delay_rate", y="OP_UNIQUE_CARRIER", color="#2563eb")
    plt.title("Top 10 Airlines by Arrival Delay Rate - Jan 2024")
    plt.xlabel("Arrival delay rate (%)")
    plt.ylabel("Airline")
    plt.tight_layout()
    plt.savefig(SCREENSHOTS_DIR / "week2_airline_delay_rate.png", dpi=150)
    plt.close()

    time_block = (
        completed.groupby("DEP_TIME_BLK", as_index=False)
        .agg(flights=("FLIGHTS", "sum"), arrival_delay_rate=("IS_DELAYED_ARRIVAL", "mean"))
        .sort_values("DEP_TIME_BLK")
    )
    time_block["arrival_delay_rate"] *= 100
    plt.figure(figsize=(12, 5))
    sns.lineplot(data=time_block, x="DEP_TIME_BLK", y="arrival_delay_rate", marker="o", color="#0f766e")
    plt.title("Arrival Delay Rate by Departure Time Block - Jan 2024")
    plt.xlabel("Departure time block")
    plt.ylabel("Arrival delay rate (%)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(SCREENSHOTS_DIR / "week2_delay_by_time_block.png", dpi=150)
    plt.close()

    causes = (
        completed[["CARRIER_DELAY", "WEATHER_DELAY", "NAS_DELAY", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"]]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    causes.columns = ["delay_cause", "delay_minutes"]
    plt.figure(figsize=(10, 5))
    sns.barplot(data=causes, x="delay_minutes", y="delay_cause", color="#dc2626")
    plt.title("Total Delay Minutes by Cause - Jan 2024")
    plt.xlabel("Delay minutes")
    plt.ylabel("Delay cause")
    plt.tight_layout()
    plt.savefig(SCREENSHOTS_DIR / "week2_delay_causes.png", dpi=150)
    plt.close()


def write_summary(cleaned: pd.DataFrame, null_summary: pd.DataFrame) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    completed = cleaned[cleaned["IS_COMPLETED_FLIGHT"] == 1]
    cancelled = int(cleaned["CANCELLED"].fillna(0).sum())
    diverted = int(cleaned["DIVERTED"].fillna(0).sum())
    arrival_delay_rate = completed["IS_DELAYED_ARRIVAL"].mean() * 100
    departure_delay_rate = completed["IS_DELAYED_DEPARTURE"].mean() * 100

    top_nulls = null_summary.sort_values("nulls_before", ascending=False).head(12)
    summary = [
        "# Data Cleaning Summary",
        "",
        "Source: BTS Reporting Carrier On-Time Performance, January 2024.",
        "",
        f"- Rows loaded: {len(cleaned):,}",
        f"- Columns retained after filtering: {len(RELEVANT_COLUMNS)}",
        f"- Completed flights: {len(completed):,}",
        f"- Cancelled flights: {cancelled:,}",
        f"- Diverted flights: {diverted:,}",
        f"- Arrival delay rate for completed flights: {arrival_delay_rate:.2f}%",
        f"- Departure delay rate for completed flights: {departure_delay_rate:.2f}%",
        "",
        "## Null Handling",
        "",
        "- Delay-cause nulls were filled with `0` because BTS leaves these fields blank when no qualifying delay cause exists.",
        "- `CANCELLATION_CODE` nulls were filled with `Not Cancelled`.",
        "- Missing arrival/departure delay indicators for completed flights were filled with `0`.",
        "- Null flags were added for original departure and arrival delay nulls.",
        "",
        "## Top Null Fields Before/After Cleaning",
        "",
        top_nulls.to_markdown(),
        "",
        "## Outputs",
        "",
        "- `data/processed/flight_delay_cleaned_2024_01.csv`",
        "- `data/processed/flight_delay_cleaned_2024_01.sqlite`",
        "- `screenshots/week2_airline_delay_rate.png`",
        "- `screenshots/week2_delay_by_time_block.png`",
        "- `screenshots/week2_delay_causes.png`",
    ]
    (REPORTS_DIR / "data_cleaning_summary.md").write_text("\n".join(summary), encoding="utf-8")


def main() -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(REPORTS_DIR / ".mplconfig"))
    Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    raw = load_data()
    cleaned, null_summary = clean_data(raw)

    cleaned_csv = PROCESSED_DIR / "flight_delay_cleaned_2024_01.csv"
    cleaned_db = PROCESSED_DIR / "flight_delay_cleaned_2024_01.sqlite"
    cleaned.to_csv(cleaned_csv, index=False)
    with sqlite3.connect(cleaned_db) as conn:
        cleaned.to_sql("flight_delay_cleaned", conn, if_exists="replace", index=False)
        null_summary.reset_index(names="column_name").to_sql("delay_null_summary", conn, if_exists="replace", index=False)

    null_summary.to_csv(PROCESSED_DIR / "delay_null_summary_2024_01.csv")
    save_charts(cleaned)
    write_summary(cleaned, null_summary)

    print(f"Rows cleaned: {len(cleaned):,}")
    print(f"Columns retained: {len(cleaned.columns):,}")
    print(f"Wrote: {cleaned_csv}")
    print(f"Wrote: {cleaned_db}")
    print(f"Wrote: {REPORTS_DIR / 'data_cleaning_summary.md'}")


if __name__ == "__main__":
    main()
