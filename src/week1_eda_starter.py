from __future__ import annotations

import os
import sqlite3
import zipfile
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


KEY_COLUMNS = [
    "YEAR",
    "QUARTER",
    "MONTH",
    "DAY_OF_MONTH",
    "DAY_OF_WEEK",
    "FL_DATE",
    "OP_UNIQUE_CARRIER",
    "OP_CARRIER_AIRLINE_ID",
    "OP_CARRIER",
    "TAIL_NUM",
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


def find_first_data_file() -> Path | None:
    for pattern in ("*.csv", "*.zip"):
        files = sorted(RAW_DIR.glob(pattern))
        if files:
            return files[0]
    return None


def read_sample(path: Path, rows: int = 100_000) -> pd.DataFrame:
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not csv_names:
                raise ValueError(f"No CSV found inside {path.name}")
            with archive.open(csv_names[0]) as handle:
                return pd.read_csv(handle, nrows=rows, low_memory=False)
    return pd.read_csv(path, nrows=rows, low_memory=False)


def main() -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / "reports" / ".mplconfig"))
    Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    data_file = find_first_data_file()
    if data_file is None:
        print("No BTS/Kaggle CSV or ZIP found in data/raw yet.")
        print("Download a BTS TranStats CSV/ZIP, place it in data/raw, then rerun this script.")
        return

    df = read_sample(data_file)
    print(f"Loaded sample: {data_file.name}")
    print(f"Rows sampled: {len(df):,}")
    print(f"Columns found: {len(df.columns):,}")
    print("First 30 columns:")
    print(", ".join(df.columns[:30]))

    available_key_columns = [col for col in KEY_COLUMNS if col in df.columns]
    print(f"Key delay-analysis columns available: {len(available_key_columns)}")
    print(", ".join(available_key_columns))

    sample_path = PROCESSED_DIR / "week1_sample_for_tableau.csv"
    df.to_csv(sample_path, index=False)

    db_path = PROCESSED_DIR / "flight_delay_week1.sqlite"
    with sqlite3.connect(db_path) as conn:
        df.to_sql("flight_delay_sample", conn, if_exists="replace", index=False)

    print(f"Wrote Tableau sample: {sample_path}")
    print(f"Wrote SQLite sample: {db_path}")


if __name__ == "__main__":
    main()
