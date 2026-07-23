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
OUTPUT_DB = PROCESSED_DIR / "airport_delay_analysis_2024_01.sqlite"

MIN_FLIGHTS = 500

CAUSE_COLUMNS = [
    "CARRIER_DELAY",
    "WEATHER_DELAY",
    "NAS_DELAY",
    "SECURITY_DELAY",
    "LATE_AIRCRAFT_DELAY",
]


def load_cleaned_data() -> pd.DataFrame:
    if not CLEANED_CSV.exists():
        raise FileNotFoundError(
            f"Missing cleaned file: {CLEANED_CSV}. Run src/clean_delay_data.py first."
        )
    columns = [
        "ORIGIN",
        "ORIGIN_CITY_NAME",
        "ORIGIN_STATE_ABR",
        "DEST",
        "DEST_CITY_NAME",
        "DEST_STATE_ABR",
        "FLIGHTS",
        "ARR_DELAY",
        "DEP_DELAY",
        "ARR_DEL15",
        "DEP_DEL15",
        "CANCELLED",
        "DIVERTED",
        "DISTANCE",
        "IS_COMPLETED_FLIGHT",
        *CAUSE_COLUMNS,
    ]
    return pd.read_csv(CLEANED_CSV, usecols=columns, low_memory=False)


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df.copy()
    numeric_columns = [
        "FLIGHTS",
        "ARR_DELAY",
        "DEP_DELAY",
        "ARR_DEL15",
        "DEP_DEL15",
        "CANCELLED",
        "DIVERTED",
        "DISTANCE",
        "IS_COMPLETED_FLIGHT",
        *CAUSE_COLUMNS,
    ]
    for column in numeric_columns:
        prepared[column] = pd.to_numeric(prepared[column], errors="coerce").fillna(0)

    prepared["ARR_DELAY_POSITIVE"] = prepared["ARR_DELAY"].clip(lower=0)
    prepared["DEP_DELAY_POSITIVE"] = prepared["DEP_DELAY"].clip(lower=0)
    prepared["TOTAL_CAUSE_DELAY"] = prepared[CAUSE_COLUMNS].sum(axis=1)
    return prepared


def aggregate_airports(
    df: pd.DataFrame,
    airport_col: str,
    city_col: str,
    state_col: str,
    airport_role: str,
) -> pd.DataFrame:
    completed = df[df["IS_COMPLETED_FLIGHT"] == 1].copy()
    grouped = (
        completed.groupby([airport_col, city_col, state_col], as_index=False)
        .agg(
            flights=("FLIGHTS", "sum"),
            avg_arrival_delay_minutes=("ARR_DELAY", "mean"),
            avg_departure_delay_minutes=("DEP_DELAY", "mean"),
            avg_positive_arrival_delay_minutes=("ARR_DELAY_POSITIVE", "mean"),
            arrival_delay_rate_pct=("ARR_DEL15", "mean"),
            departure_delay_rate_pct=("DEP_DEL15", "mean"),
            avg_distance_miles=("DISTANCE", "mean"),
            carrier_delay_minutes=("CARRIER_DELAY", "sum"),
            weather_delay_minutes=("WEATHER_DELAY", "sum"),
            nas_delay_minutes=("NAS_DELAY", "sum"),
            security_delay_minutes=("SECURITY_DELAY", "sum"),
            late_aircraft_delay_minutes=("LATE_AIRCRAFT_DELAY", "sum"),
            total_cause_delay_minutes=("TOTAL_CAUSE_DELAY", "sum"),
        )
        .rename(
            columns={
                airport_col: "airport",
                city_col: "city_name",
                state_col: "state",
            }
        )
    )
    grouped["airport_role"] = airport_role
    grouped["arrival_delay_rate_pct"] = (grouped["arrival_delay_rate_pct"] * 100).round(2)
    grouped["departure_delay_rate_pct"] = (grouped["departure_delay_rate_pct"] * 100).round(2)

    cancelled = (
        df.groupby([airport_col], as_index=False)
        .agg(cancelled_flights=("CANCELLED", "sum"), diverted_flights=("DIVERTED", "sum"))
        .rename(columns={airport_col: "airport"})
    )
    grouped = grouped.merge(cancelled, on="airport", how="left")

    round_columns = [
        "avg_arrival_delay_minutes",
        "avg_departure_delay_minutes",
        "avg_positive_arrival_delay_minutes",
        "avg_distance_miles",
    ]
    for column in round_columns:
        grouped[column] = grouped[column].round(2)

    return grouped[grouped["flights"] >= MIN_FLIGHTS].sort_values(
        "avg_arrival_delay_minutes", ascending=False
    )


def build_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    origin = aggregate_airports(
        df,
        airport_col="ORIGIN",
        city_col="ORIGIN_CITY_NAME",
        state_col="ORIGIN_STATE_ABR",
        airport_role="origin",
    )
    destination = aggregate_airports(
        df,
        airport_col="DEST",
        city_col="DEST_CITY_NAME",
        state_col="DEST_STATE_ABR",
        airport_role="destination",
    )

    overview = pd.DataFrame(
        [
            {"metric": "origin_airports_analyzed", "value": len(origin)},
            {"metric": "destination_airports_analyzed", "value": len(destination)},
            {"metric": "minimum_completed_flights_filter", "value": MIN_FLIGHTS},
            {"metric": "top_origin_avg_arrival_delay_minutes", "value": origin.iloc[0]["avg_arrival_delay_minutes"]},
            {"metric": "top_destination_avg_arrival_delay_minutes", "value": destination.iloc[0]["avg_arrival_delay_minutes"]},
        ]
    )

    return {
        "airport_delay_overview": overview,
        "origin_airport_delay_summary": origin,
        "destination_airport_delay_summary": destination,
        "top10_origin_airports_by_avg_delay": origin.head(10).copy(),
        "top10_destination_airports_by_avg_delay": destination.head(10).copy(),
        "top10_origin_airports_by_nas_delay": origin.sort_values("nas_delay_minutes", ascending=False).head(10).copy(),
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

    origin_top = tables["top10_origin_airports_by_avg_delay"]
    plt.figure(figsize=(11, 6))
    sns.barplot(data=origin_top, x="avg_arrival_delay_minutes", y="airport", color="#2563eb")
    plt.title("Top 10 Origin Airports by Average Arrival Delay - Jan 2024")
    plt.xlabel("Average arrival delay minutes")
    plt.ylabel("Origin airport")
    for index, row in origin_top.reset_index(drop=True).iterrows():
        plt.text(row["avg_arrival_delay_minutes"] + 0.15, index, f"{row['avg_arrival_delay_minutes']:.2f}", va="center")
    plt.tight_layout()
    plt.savefig(SCREENSHOTS_DIR / "week5_top10_origin_airports_avg_delay.png", dpi=150)
    plt.close()

    destination_top = tables["top10_destination_airports_by_avg_delay"]
    plt.figure(figsize=(11, 6))
    sns.barplot(data=destination_top, x="avg_arrival_delay_minutes", y="airport", color="#0f766e")
    plt.title("Top 10 Destination Airports by Average Arrival Delay - Jan 2024")
    plt.xlabel("Average arrival delay minutes")
    plt.ylabel("Destination airport")
    for index, row in destination_top.reset_index(drop=True).iterrows():
        plt.text(row["avg_arrival_delay_minutes"] + 0.15, index, f"{row['avg_arrival_delay_minutes']:.2f}", va="center")
    plt.tight_layout()
    plt.savefig(SCREENSHOTS_DIR / "week5_top10_destination_airports_avg_delay.png", dpi=150)
    plt.close()

    scatter = tables["origin_airport_delay_summary"].copy()
    plt.figure(figsize=(11, 6))
    ax = sns.scatterplot(
        data=scatter,
        x="flights",
        y="avg_arrival_delay_minutes",
        size="arrival_delay_rate_pct",
        hue="arrival_delay_rate_pct",
        palette="YlOrRd",
        sizes=(40, 420),
        edgecolor="#111827",
        linewidth=0.3,
    )
    for _, row in origin_top.iterrows():
        plt.text(row["flights"], row["avg_arrival_delay_minutes"] + 0.35, row["airport"], ha="center", fontsize=9, weight="bold")
    plt.title("Origin Airport Volume vs Average Arrival Delay - Jan 2024")
    plt.xlabel("Completed flights")
    plt.ylabel("Average arrival delay minutes")
    ax.legend(loc="upper right", bbox_to_anchor=(1.22, 1), title="Delay rate %")
    plt.tight_layout()
    plt.savefig(SCREENSHOTS_DIR / "week5_origin_airport_delay_scatter.png", dpi=150)
    plt.close()

    nas_top = tables["top10_origin_airports_by_nas_delay"]
    plt.figure(figsize=(11, 6))
    sns.barplot(data=nas_top, x="nas_delay_minutes", y="airport", color="#dc2626")
    plt.title("Top 10 Origin Airports by NAS Delay Minutes - Jan 2024")
    plt.xlabel("NAS delay minutes")
    plt.ylabel("Origin airport")
    plt.tight_layout()
    plt.savefig(SCREENSHOTS_DIR / "week5_top10_origin_airports_nas_delay.png", dpi=150)
    plt.close()


def format_table(table: pd.DataFrame, columns: list[str]) -> str:
    display = table[columns].copy()
    count_columns = [
        "flights",
        "cancelled_flights",
        "diverted_flights",
        "carrier_delay_minutes",
        "weather_delay_minutes",
        "nas_delay_minutes",
        "late_aircraft_delay_minutes",
        "total_cause_delay_minutes",
    ]
    for column in count_columns:
        if column in display.columns:
            display[column] = display[column].map(lambda value: f"{int(value):,}")
    for column in [
        "avg_arrival_delay_minutes",
        "avg_departure_delay_minutes",
        "arrival_delay_rate_pct",
        "departure_delay_rate_pct",
        "avg_distance_miles",
    ]:
        if column in display.columns:
            display[column] = display[column].map(lambda value: f"{float(value):.2f}")
    return display.astype(str).to_markdown(index=False, disable_numparse=True)


def write_report(tables: dict[str, pd.DataFrame]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    origin = tables["origin_airport_delay_summary"]
    destination = tables["destination_airport_delay_summary"]
    top_origin = origin.iloc[0]
    top_destination = destination.iloc[0]
    top_nas = tables["top10_origin_airports_by_nas_delay"].iloc[0]

    lines = [
        "# Airport-Wise Delay Analysis",
        "",
        "Source: BTS Reporting Carrier On-Time Performance, January 2024.",
        "",
        "## Method",
        "",
        "- Used the cleaned January 2024 BTS flight delay dataset.",
        "- Grouped records by origin airport and destination airport separately.",
        "- Filtered to airports with at least 500 completed flights to avoid unstable small-volume rankings.",
        "- Calculated grouped metrics for flight count, average arrival/departure delay, delay rate, cancellations, diversions, distance, and delay-cause minutes.",
        "",
        "## Overview",
        "",
        f"- Origin airports analyzed after volume filter: {len(origin):,}",
        f"- Destination airports analyzed after volume filter: {len(destination):,}",
        f"- Highest average-delay origin airport: {top_origin['airport']} ({top_origin['city_name']}) at {top_origin['avg_arrival_delay_minutes']:.2f} minutes.",
        f"- Highest average-delay destination airport: {top_destination['airport']} ({top_destination['city_name']}) at {top_destination['avg_arrival_delay_minutes']:.2f} minutes.",
        f"- Highest NAS-delay origin airport: {top_nas['airport']} ({top_nas['city_name']}) with {int(top_nas['nas_delay_minutes']):,} NAS-delay minutes.",
        "",
        "## Top 10 Origin Airports by Average Arrival Delay",
        "",
        format_table(
            tables["top10_origin_airports_by_avg_delay"],
            [
                "airport",
                "city_name",
                "state",
                "flights",
                "avg_arrival_delay_minutes",
                "arrival_delay_rate_pct",
                "cancelled_flights",
                "nas_delay_minutes",
                "weather_delay_minutes",
            ],
        ),
        "",
        "## Top 10 Destination Airports by Average Arrival Delay",
        "",
        format_table(
            tables["top10_destination_airports_by_avg_delay"],
            [
                "airport",
                "city_name",
                "state",
                "flights",
                "avg_arrival_delay_minutes",
                "arrival_delay_rate_pct",
                "cancelled_flights",
                "nas_delay_minutes",
                "weather_delay_minutes",
            ],
        ),
        "",
        "## Top 10 Origin Airports by NAS Delay Minutes",
        "",
        format_table(
            tables["top10_origin_airports_by_nas_delay"],
            [
                "airport",
                "city_name",
                "state",
                "flights",
                "arrival_delay_rate_pct",
                "nas_delay_minutes",
                "weather_delay_minutes",
                "total_cause_delay_minutes",
            ],
        ),
        "",
        "## Outputs",
        "",
        "- `data/processed/airport_delay_analysis_2024_01.sqlite`",
        "- `data/processed/origin_airport_delay_summary_2024_01.csv`",
        "- `data/processed/destination_airport_delay_summary_2024_01.csv`",
        "- `data/processed/top10_origin_airports_by_avg_delay_2024_01.csv`",
        "- `data/processed/top10_destination_airports_by_avg_delay_2024_01.csv`",
        "- `data/processed/top10_origin_airports_by_nas_delay_2024_01.csv`",
        "- `screenshots/week5_top10_origin_airports_avg_delay.png`",
        "- `screenshots/week5_top10_destination_airports_avg_delay.png`",
        "- `screenshots/week5_origin_airport_delay_scatter.png`",
        "- `screenshots/week5_top10_origin_airports_nas_delay.png`",
    ]
    (REPORTS_DIR / "airport_delay_analysis.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    tables = build_tables(prepare_data(load_cleaned_data()))
    save_tables(tables)
    save_charts(tables)
    write_report(tables)

    origin = tables["origin_airport_delay_summary"].iloc[0]
    destination = tables["destination_airport_delay_summary"].iloc[0]
    print(f"Origin airports analyzed: {len(tables['origin_airport_delay_summary']):,}")
    print(f"Destination airports analyzed: {len(tables['destination_airport_delay_summary']):,}")
    print(f"Top origin airport by average delay: {origin['airport']} ({origin['avg_arrival_delay_minutes']:.2f} minutes)")
    print(f"Top destination airport by average delay: {destination['airport']} ({destination['avg_arrival_delay_minutes']:.2f} minutes)")
    print(f"Wrote: {REPORTS_DIR / 'airport_delay_analysis.md'}")


if __name__ == "__main__":
    main()
