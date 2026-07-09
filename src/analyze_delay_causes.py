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
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"

CLEANED_CSV = PROCESSED_DIR / "flight_delay_cleaned_2024_01.csv"
OUTPUT_DB = PROCESSED_DIR / "delay_cause_analysis_2024_01.sqlite"

CAUSE_COLUMNS = [
    "CARRIER_DELAY",
    "WEATHER_DELAY",
    "NAS_DELAY",
    "SECURITY_DELAY",
    "LATE_AIRCRAFT_DELAY",
]

CAUSE_LABELS = {
    "CARRIER_DELAY": "Carrier",
    "WEATHER_DELAY": "Weather",
    "NAS_DELAY": "NAS",
    "SECURITY_DELAY": "Security",
    "LATE_AIRCRAFT_DELAY": "Late Aircraft",
}


def load_cleaned_data() -> pd.DataFrame:
    if not CLEANED_CSV.exists():
        raise FileNotFoundError(
            f"Missing cleaned file: {CLEANED_CSV}. Run src/clean_delay_data.py first."
        )
    columns = [
        "FL_DATE",
        "OP_UNIQUE_CARRIER",
        "ORIGIN",
        "ORIGIN_CITY_NAME",
        "DEST",
        "DEST_CITY_NAME",
        "DEP_TIME_BLK",
        "ARR_DEL15",
        "IS_COMPLETED_FLIGHT",
        "FLIGHTS",
        *CAUSE_COLUMNS,
    ]
    return pd.read_csv(CLEANED_CSV, usecols=columns, low_memory=False)


def prepare_delay_data(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df.copy()
    for column in ["ARR_DEL15", "IS_COMPLETED_FLIGHT", "FLIGHTS", *CAUSE_COLUMNS]:
        prepared[column] = pd.to_numeric(prepared[column], errors="coerce").fillna(0)
    prepared["TOTAL_CAUSE_DELAY"] = prepared[CAUSE_COLUMNS].sum(axis=1)
    prepared["HAS_REPORTED_CAUSE_DELAY"] = (prepared["TOTAL_CAUSE_DELAY"] > 0).astype(int)
    return prepared[prepared["IS_COMPLETED_FLIGHT"] == 1].copy()


def build_summary_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    total_flights = int(df["FLIGHTS"].sum())
    delayed_arrivals = int((df["ARR_DEL15"] == 1).sum())
    cause_total_minutes = df[CAUSE_COLUMNS].sum()
    total_cause_minutes = float(cause_total_minutes.sum())

    cause_summary = pd.DataFrame(
        {
            "cause_code": cause_total_minutes.index,
            "cause": [CAUSE_LABELS[col] for col in cause_total_minutes.index],
            "total_delay_minutes": cause_total_minutes.values,
            "flights_with_cause": [(df[col] > 0).sum() for col in cause_total_minutes.index],
        }
    )
    cause_summary["share_of_cause_minutes_pct"] = (
        cause_summary["total_delay_minutes"] / total_cause_minutes * 100
    ).round(2)
    cause_summary["avg_minutes_per_affected_flight"] = (
        cause_summary["total_delay_minutes"] / cause_summary["flights_with_cause"].replace(0, pd.NA)
    ).round(2)
    cause_summary = cause_summary.sort_values("total_delay_minutes", ascending=False)

    airline = (
        df.groupby("OP_UNIQUE_CARRIER", as_index=False)
        .agg(
            flights=("FLIGHTS", "sum"),
            delayed_arrivals=("ARR_DEL15", "sum"),
            carrier_delay_minutes=("CARRIER_DELAY", "sum"),
            weather_delay_minutes=("WEATHER_DELAY", "sum"),
            nas_delay_minutes=("NAS_DELAY", "sum"),
            security_delay_minutes=("SECURITY_DELAY", "sum"),
            late_aircraft_delay_minutes=("LATE_AIRCRAFT_DELAY", "sum"),
        )
        .assign(arrival_delay_rate_pct=lambda x: (x["delayed_arrivals"] / x["flights"] * 100).round(2))
        .sort_values("carrier_delay_minutes", ascending=False)
    )

    origin = (
        df.groupby(["ORIGIN", "ORIGIN_CITY_NAME"], as_index=False)
        .agg(
            flights=("FLIGHTS", "sum"),
            delayed_arrivals=("ARR_DEL15", "sum"),
            carrier_delay_minutes=("CARRIER_DELAY", "sum"),
            weather_delay_minutes=("WEATHER_DELAY", "sum"),
            nas_delay_minutes=("NAS_DELAY", "sum"),
            security_delay_minutes=("SECURITY_DELAY", "sum"),
            late_aircraft_delay_minutes=("LATE_AIRCRAFT_DELAY", "sum"),
        )
        .assign(arrival_delay_rate_pct=lambda x: (x["delayed_arrivals"] / x["flights"] * 100).round(2))
        .sort_values("nas_delay_minutes", ascending=False)
    )

    time_block = (
        df.groupby("DEP_TIME_BLK", as_index=False)
        .agg(
            flights=("FLIGHTS", "sum"),
            delayed_arrivals=("ARR_DEL15", "sum"),
            carrier_delay_minutes=("CARRIER_DELAY", "sum"),
            weather_delay_minutes=("WEATHER_DELAY", "sum"),
            nas_delay_minutes=("NAS_DELAY", "sum"),
            security_delay_minutes=("SECURITY_DELAY", "sum"),
            late_aircraft_delay_minutes=("LATE_AIRCRAFT_DELAY", "sum"),
        )
        .assign(arrival_delay_rate_pct=lambda x: (x["delayed_arrivals"] / x["flights"] * 100).round(2))
        .sort_values("DEP_TIME_BLK")
    )

    overview = pd.DataFrame(
        [
            {"metric": "completed_flights", "value": total_flights},
            {"metric": "delayed_arrivals", "value": delayed_arrivals},
            {"metric": "arrival_delay_rate_pct", "value": round(delayed_arrivals / total_flights * 100, 2)},
            {"metric": "flights_with_reported_cause_delay", "value": int(df["HAS_REPORTED_CAUSE_DELAY"].sum())},
            {"metric": "total_reported_cause_delay_minutes", "value": round(total_cause_minutes, 2)},
        ]
    )

    return {
        "delay_cause_overview": overview,
        "delay_cause_summary": cause_summary,
        "delay_cause_by_airline": airline,
        "delay_cause_by_origin": origin,
        "delay_cause_by_time_block": time_block,
    }


def save_tables(tables: dict[str, pd.DataFrame]) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(OUTPUT_DB) as conn:
        for name, table in tables.items():
            table.to_csv(PROCESSED_DIR / f"{name}_2024_01.csv", index=False)
            table.to_sql(name, conn, if_exists="replace", index=False)


def save_charts(tables: dict[str, pd.DataFrame]) -> None:
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    summary = tables["delay_cause_summary"].copy()
    plt.figure(figsize=(10, 5))
    sns.barplot(data=summary, x="total_delay_minutes", y="cause", color="#2563eb")
    plt.title("Total Delay Minutes by Cause - Jan 2024")
    plt.xlabel("Reported delay minutes")
    plt.ylabel("Delay cause")
    plt.tight_layout()
    plt.savefig(SCREENSHOTS_DIR / "week3_total_delay_minutes_by_cause.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 8))
    plt.pie(
        summary["share_of_cause_minutes_pct"],
        labels=summary["cause"],
        autopct="%1.1f%%",
        startangle=90,
        colors=sns.color_palette("Set2", n_colors=len(summary)),
    )
    plt.title("Share of Reported Delay Minutes by Cause - Jan 2024")
    plt.tight_layout()
    plt.savefig(SCREENSHOTS_DIR / "week3_delay_cause_share.png", dpi=150)
    plt.close()

    airline = tables["delay_cause_by_airline"].head(10).copy()
    plt.figure(figsize=(11, 5))
    sns.barplot(data=airline, x="carrier_delay_minutes", y="OP_UNIQUE_CARRIER", color="#dc2626")
    plt.title("Top Airlines by Carrier Delay Minutes - Jan 2024")
    plt.xlabel("Carrier delay minutes")
    plt.ylabel("Airline")
    plt.tight_layout()
    plt.savefig(SCREENSHOTS_DIR / "week3_top_airlines_carrier_delay.png", dpi=150)
    plt.close()

    time_block = tables["delay_cause_by_time_block"].copy()
    heatmap_data = time_block.set_index("DEP_TIME_BLK")[
        [
            "carrier_delay_minutes",
            "weather_delay_minutes",
            "nas_delay_minutes",
            "security_delay_minutes",
            "late_aircraft_delay_minutes",
        ]
    ].T
    heatmap_data.index = ["Carrier", "Weather", "NAS", "Security", "Late Aircraft"]
    plt.figure(figsize=(13, 5))
    sns.heatmap(heatmap_data, cmap="YlOrRd", linewidths=0.3)
    plt.title("Delay Cause Minutes by Departure Time Block - Jan 2024")
    plt.xlabel("Departure time block")
    plt.ylabel("Delay cause")
    plt.tight_layout()
    plt.savefig(SCREENSHOTS_DIR / "week3_delay_cause_time_heatmap.png", dpi=150)
    plt.close()


def write_report(tables: dict[str, pd.DataFrame]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    overview = tables["delay_cause_overview"]
    summary = tables["delay_cause_summary"]
    airline = tables["delay_cause_by_airline"]
    origin = tables["delay_cause_by_origin"]
    time_block = tables["delay_cause_by_time_block"]

    metric = dict(zip(overview["metric"], overview["value"], strict=False))
    top_cause = summary.iloc[0]
    top_carrier_airline = airline.iloc[0]
    top_nas_origin = origin.iloc[0]
    peak_time = time_block.assign(total_minutes=time_block[
        [
            "carrier_delay_minutes",
            "weather_delay_minutes",
            "nas_delay_minutes",
            "security_delay_minutes",
            "late_aircraft_delay_minutes",
        ]
    ].sum(axis=1)).sort_values("total_minutes", ascending=False).iloc[0]

    summary_display = summary.copy()
    for column in ["total_delay_minutes", "flights_with_cause"]:
        summary_display[column] = summary_display[column].map(lambda value: f"{int(value):,}")
    for column in ["share_of_cause_minutes_pct", "avg_minutes_per_affected_flight"]:
        summary_display[column] = summary_display[column].map(lambda value: f"{float(value):.2f}")

    airline_display = airline.head(10)[
        [
            "OP_UNIQUE_CARRIER",
            "flights",
            "delayed_arrivals",
            "arrival_delay_rate_pct",
            "carrier_delay_minutes",
            "late_aircraft_delay_minutes",
        ]
    ].copy()
    for column in ["flights", "delayed_arrivals", "carrier_delay_minutes", "late_aircraft_delay_minutes"]:
        airline_display[column] = airline_display[column].map(lambda value: f"{int(value):,}")
    airline_display["arrival_delay_rate_pct"] = airline_display["arrival_delay_rate_pct"].map(lambda value: f"{float(value):.2f}")

    origin_display = origin.head(10)[
        [
            "ORIGIN",
            "ORIGIN_CITY_NAME",
            "flights",
            "delayed_arrivals",
            "arrival_delay_rate_pct",
            "nas_delay_minutes",
            "weather_delay_minutes",
        ]
    ].copy()
    for column in ["flights", "delayed_arrivals", "nas_delay_minutes", "weather_delay_minutes"]:
        origin_display[column] = origin_display[column].map(lambda value: f"{int(value):,}")
    origin_display["arrival_delay_rate_pct"] = origin_display["arrival_delay_rate_pct"].map(lambda value: f"{float(value):.2f}")

    lines = [
        "# Delay Cause Analysis",
        "",
        "Source: BTS Reporting Carrier On-Time Performance, January 2024.",
        "",
        "## Overview",
        "",
        f"- Completed flights analyzed: {int(metric['completed_flights']):,}",
        f"- Delayed arrivals: {int(metric['delayed_arrivals']):,}",
        f"- Arrival delay rate: {metric['arrival_delay_rate_pct']:.2f}%",
        f"- Flights with reported delay-cause minutes: {int(metric['flights_with_reported_cause_delay']):,}",
        f"- Total reported delay-cause minutes: {int(metric['total_reported_cause_delay_minutes']):,}",
        "",
        "## Main Findings",
        "",
        f"- Largest delay cause: {top_cause['cause']} with {int(top_cause['total_delay_minutes']):,} minutes ({top_cause['share_of_cause_minutes_pct']:.2f}% of reported cause minutes).",
        f"- Highest carrier-delay airline by minutes: {top_carrier_airline['OP_UNIQUE_CARRIER']} with {int(top_carrier_airline['carrier_delay_minutes']):,} carrier-delay minutes.",
        f"- Highest NAS-delay origin airport by minutes: {top_nas_origin['ORIGIN']} ({top_nas_origin['ORIGIN_CITY_NAME']}) with {int(top_nas_origin['nas_delay_minutes']):,} NAS-delay minutes.",
        f"- Peak time block by total cause minutes: {peak_time['DEP_TIME_BLK']} with {int(peak_time['total_minutes']):,} reported delay minutes.",
        "",
        "## Delay Cause Summary",
        "",
        summary_display.to_markdown(index=False),
        "",
        "## Top 10 Airlines by Carrier Delay Minutes",
        "",
        airline_display.to_markdown(index=False),
        "",
        "## Top 10 Origin Airports by NAS Delay Minutes",
        "",
        origin_display.to_markdown(index=False),
        "",
        "## Outputs",
        "",
        "- `data/processed/delay_cause_analysis_2024_01.sqlite`",
        "- `data/processed/delay_cause_summary_2024_01.csv`",
        "- `data/processed/delay_cause_by_airline_2024_01.csv`",
        "- `data/processed/delay_cause_by_origin_2024_01.csv`",
        "- `data/processed/delay_cause_by_time_block_2024_01.csv`",
        "- `screenshots/week3_total_delay_minutes_by_cause.png`",
        "- `screenshots/week3_delay_cause_share.png`",
        "- `screenshots/week3_top_airlines_carrier_delay.png`",
        "- `screenshots/week3_delay_cause_time_heatmap.png`",
    ]
    (REPORTS_DIR / "delay_cause_analysis.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    df = prepare_delay_data(load_cleaned_data())
    tables = build_summary_tables(df)
    save_tables(tables)
    save_charts(tables)
    write_report(tables)

    overview = dict(zip(tables["delay_cause_overview"]["metric"], tables["delay_cause_overview"]["value"], strict=False))
    print(f"Completed flights analyzed: {int(overview['completed_flights']):,}")
    print(f"Delayed arrivals: {int(overview['delayed_arrivals']):,}")
    print(f"Total reported cause minutes: {int(overview['total_reported_cause_delay_minutes']):,}")
    print(f"Wrote: {REPORTS_DIR / 'delay_cause_analysis.md'}")
    print(f"Wrote: {OUTPUT_DB}")


if __name__ == "__main__":
    main()
