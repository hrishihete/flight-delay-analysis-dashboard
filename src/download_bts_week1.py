from __future__ import annotations

import html
import re
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
URL = "https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ&QO_fu146_anzr=b0-gvzr"

YEAR = "2024"
MONTH = "1"

SELECTED_COLUMNS = [
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


def hidden_value(page: str, name: str) -> str:
    pattern = rf'name="{re.escape(name)}"[^>]*value="([^"]*)"'
    match = re.search(pattern, page)
    return html.unescape(match.group(1)) if match else ""


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    opener.addheaders = [("User-Agent", "Mozilla/5.0")]

    with opener.open(URL, timeout=60) as response:
        page = response.read().decode("utf-8", errors="replace")

    payload = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__LASTFOCUS": "",
        "__VIEWSTATE": hidden_value(page, "__VIEWSTATE"),
        "__VIEWSTATEGENERATOR": hidden_value(page, "__VIEWSTATEGENERATOR"),
        "__EVENTVALIDATION": hidden_value(page, "__EVENTVALIDATION"),
        "cboYear": YEAR,
        "cboPeriod": MONTH,
        "btnDownload": "Download",
    }
    for column in SELECTED_COLUMNS:
        payload[column] = "on"

    encoded = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(URL, data=encoded, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    request.add_header("User-Agent", "Mozilla/5.0")

    with opener.open(request, timeout=180) as response:
        body = response.read()
        content_type = response.headers.get("Content-Type", "")

    if body.startswith(b"PK"):
        output_path = RAW_DIR / f"bts_on_time_{YEAR}_{MONTH.zfill(2)}.zip"
    elif b"," in body[:500] and "text/html" not in content_type.lower():
        output_path = RAW_DIR / f"bts_on_time_{YEAR}_{MONTH.zfill(2)}.csv"
    else:
        output_path = RAW_DIR / "bts_download_response.html"

    output_path.write_bytes(body)
    print(f"Saved {output_path}")
    print(f"Content-Type: {content_type}")
    print(f"Bytes: {len(body):,}")
    if output_path.suffix == ".html":
        print("BTS returned HTML instead of data; open this file to inspect any validation message.")


if __name__ == "__main__":
    main()
