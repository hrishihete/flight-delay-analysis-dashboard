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
OUTPUT_DB = PROCESSED_DIR / "airline_average_delay_2024_01.sqlite"
OUTPUT_CSV = PROCESSED_DIR / "top10_airlines_average_delay_2024_01.csv"

MIN_FLIGHTS = 500


def load_cleaned_data() -> pd.DataFrame:
    if not CLEANED_CSV.exists():
        raise FileNotFoundError(
            f"Missing cleaned file: {CLEANED_CSV}. Run src/clean_delay_data.py first."
        )
    columns = [
        "OP_UNIQUE_CARRIER",
        "FLIGHTS",
        "ARR_DELAY",
        "DEP_DELAY",
        "ARR_DEL15",
        "DEP_DEL15",
        "CANCELLED",
        "DIVERTED",
        "IS_COMPLETED_FLIGHT",
    ]
    return pd.read_csv(CLEANED_CSV, usecols=columns, low_memory=False)


def summarize_airlines(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    working = df.copy()
    for column in [
        "FLIGHTS",
        "ARR_DELAY",
        "DEP_DELAY",
        "ARR_DEL15",
        "DEP_DEL15",
        "CANCELLED",
        "DIVERTED",
        "IS_COMPLETED_FLIGHT",
    ]:
        working[column] = pd.to_numeric(working[column], errors="coerce").fillna(0)

    completed = working[working["IS_COMPLETED_FLIGHT"] == 1].copy()
    completed["ARR_DELAY_POSITIVE"] = completed["ARR_DELAY"].clip(lower=0)
    completed["DEP_DELAY_POSITIVE"] = completed["DEP_DELAY"].clip(lower=0)

    summary = (
        completed.groupby("OP_UNIQUE_CARRIER", as_index=False)
        .agg(
            flights=("FLIGHTS", "sum"),
            delayed_arrivals=("ARR_DEL15", "sum"),
            delayed_departures=("DEP_DEL15", "sum"),
            avg_arrival_delay_minutes=("ARR_DELAY", "mean"),
            avg_departure_delay_minutes=("DEP_DELAY", "mean"),
            avg_positive_arrival_delay_minutes=("ARR_DELAY_POSITIVE", "mean"),
            avg_positive_departure_delay_minutes=("DEP_DELAY_POSITIVE", "mean"),
        )
        .assign(
            arrival_delay_rate_pct=lambda x: (x["delayed_arrivals"] / x["flights"] * 100).round(2),
            departure_delay_rate_pct=lambda x: (x["delayed_departures"] / x["flights"] * 100).round(2),
        )
    )
    summary = summary[summary["flights"] >= MIN_FLIGHTS].copy()
    for column in [
        "avg_arrival_delay_minutes",
        "avg_departure_delay_minutes",
        "avg_positive_arrival_delay_minutes",
        "avg_positive_departure_delay_minutes",
    ]:
        summary[column] = summary[column].round(2)

    top10 = summary.sort_values("avg_arrival_delay_minutes", ascending=False).head(10).copy()
    return summary.sort_values("avg_arrival_delay_minutes", ascending=False), top10


def save_tables(summary: pd.DataFrame, top10: pd.DataFrame) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    summary.to_csv(PROCESSED_DIR / "airline_average_delay_summary_2024_01.csv", index=False)
    top10.to_csv(OUTPUT_CSV, index=False)
    with sqlite3.connect(OUTPUT_DB) as conn:
        summary.to_sql("airline_average_delay_summary", conn, if_exists="replace", index=False)
        top10.to_sql("top10_airlines_average_delay", conn, if_exists="replace", index=False)


def save_charts(summary: pd.DataFrame, top10: pd.DataFrame) -> None:
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(11, 6))
    sns.barplot(
        data=top10,
        x="avg_arrival_delay_minutes",
        y="OP_UNIQUE_CARRIER",
        color="#2563eb",
    )
    plt.title("Top 10 Airlines by Average Arrival Delay - Jan 2024")
    plt.xlabel("Average arrival delay minutes")
    plt.ylabel("Airline")
    for index, row in top10.reset_index(drop=True).iterrows():
        plt.text(
            row["avg_arrival_delay_minutes"] + 0.15,
            index,
            f"{row['avg_arrival_delay_minutes']:.2f}",
            va="center",
            fontsize=9,
        )
    plt.tight_layout()
    plt.savefig(SCREENSHOTS_DIR / "week4_top10_airlines_avg_delay_bar.png", dpi=150)
    plt.close()

    plt.figure(figsize=(11, 6))
    scatter = sns.scatterplot(
        data=summary,
        x="flights",
        y="avg_arrival_delay_minutes",
        size="arrival_delay_rate_pct",
        hue="arrival_delay_rate_pct",
        palette="YlOrRd",
        sizes=(60, 450),
        edgecolor="#111827",
        linewidth=0.4,
        legend="brief",
    )
    for _, row in top10.iterrows():
        plt.text(
            row["flights"],
            row["avg_arrival_delay_minutes"] + 0.35,
            row["OP_UNIQUE_CARRIER"],
            ha="center",
            fontsize=9,
            weight="bold",
        )
    plt.title("Airline Flight Volume vs Average Arrival Delay - Jan 2024")
    plt.xlabel("Completed flights")
    plt.ylabel("Average arrival delay minutes")
    scatter.legend(loc="upper right", bbox_to_anchor=(1.22, 1), title="Delay rate %")
    plt.tight_layout()
    plt.savefig(SCREENSHOTS_DIR / "week4_airline_avg_delay_scatter.png", dpi=150)
    plt.close()


def write_report(summary: pd.DataFrame, top10: pd.DataFrame) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    total_airlines = len(summary)
    top_airline = top10.iloc[0]
    weighted_avg_delay = (
        (summary["avg_arrival_delay_minutes"] * summary["flights"]).sum() / summary["flights"].sum()
    )

    display_top10 = top10[
        [
            "OP_UNIQUE_CARRIER",
            "flights",
            "delayed_arrivals",
            "arrival_delay_rate_pct",
            "avg_arrival_delay_minutes",
            "avg_departure_delay_minutes",
            "avg_positive_arrival_delay_minutes",
        ]
    ].copy()
    for column in ["flights", "delayed_arrivals"]:
        display_top10[column] = display_top10[column].map(lambda value: f"{int(value):,}")
    for column in [
        "arrival_delay_rate_pct",
        "avg_arrival_delay_minutes",
        "avg_departure_delay_minutes",
        "avg_positive_arrival_delay_minutes",
    ]:
        display_top10[column] = display_top10[column].map(lambda value: f"{float(value):.2f}")
    display_top10 = display_top10.astype(str)

    lines = [
        "# Top 10 Airlines by Average Delay Time",
        "",
        "Source: BTS Reporting Carrier On-Time Performance, January 2024.",
        "",
        "## Method",
        "",
        "- Used the cleaned January 2024 BTS flight delay dataset.",
        "- Filtered to completed flights only, excluding cancelled and diverted records from average delay calculations.",
        f"- Ranked airlines with at least {MIN_FLIGHTS:,} completed flights.",
        "- Primary metric: average arrival delay minutes (`ARR_DELAY`).",
        "- Secondary context: arrival delay rate, departure delay average, and positive-only average arrival delay.",
        "",
        "## Overview",
        "",
        f"- Airlines analyzed after volume filter: {total_airlines}",
        f"- Weighted average arrival delay across included airlines: {weighted_avg_delay:.2f} minutes",
        f"- Highest average arrival delay airline: {top_airline['OP_UNIQUE_CARRIER']} at {top_airline['avg_arrival_delay_minutes']:.2f} minutes",
        f"- {top_airline['OP_UNIQUE_CARRIER']} arrival delay rate: {top_airline['arrival_delay_rate_pct']:.2f}%",
        "",
        "## Top 10 Airlines",
        "",
        display_top10.to_markdown(index=False, disable_numparse=True),
        "",
        "## Outputs",
        "",
        "- `data/processed/airline_average_delay_summary_2024_01.csv`",
        "- `data/processed/top10_airlines_average_delay_2024_01.csv`",
        "- `data/processed/airline_average_delay_2024_01.sqlite`",
        "- `screenshots/week4_top10_airlines_avg_delay_bar.png`",
        "- `screenshots/week4_airline_avg_delay_scatter.png`",
    ]
    (REPORTS_DIR / "airline_average_delay_analysis.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    summary, top10 = summarize_airlines(load_cleaned_data())
    save_tables(summary, top10)
    save_charts(summary, top10)
    write_report(summary, top10)

    top_airline = top10.iloc[0]
    print(f"Airlines analyzed: {len(summary)}")
    print(
        "Top airline by average arrival delay: "
        f"{top_airline['OP_UNIQUE_CARRIER']} ({top_airline['avg_arrival_delay_minutes']:.2f} minutes)"
    )
    print(f"Wrote: {REPORTS_DIR / 'airline_average_delay_analysis.md'}")
    print(f"Wrote: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
