# Weekly Update

This week I cleaned the BTS January 2024 flight delay dataset and filtered it to the columns needed for delay analysis.
I handled nulls in delay fields by filling BTS delay-cause blanks with 0, filling missing cancellation codes with `Not Cancelled`, and preserving null flags for key delay fields.
I created a cleaned CSV file and a SQLite database so the data can be used in both Python and SQL workflows.
I generated initial charts for airline delay rate, delay rate by departure time block, and total delay minutes by cause.
I discovered that delay-cause columns are intentionally blank for most non-delayed flights, so they should be treated as 0 minutes rather than removed.
I also found that cancelled/diverted flights need to be tracked separately from completed-flight delay analysis.
Next, I will connect the cleaned CSV to Tableau Public and build the first dashboard views by airline, airport, and time period.

## Work Artifacts

- Repo: https://github.com/hrishihete/flight-delay-analysis-dashboard
- Data source: BTS TranStats Reporting Carrier On-Time Performance
- Cleaning script: `src/clean_delay_data.py`
- Cleaning summary: `reports/data_cleaning_summary.md`
- Cleaned CSV: `data/processed/flight_delay_cleaned_2024_01.csv`
- SQLite DB: `data/processed/flight_delay_cleaned_2024_01.sqlite`
- Screenshots/charts: `screenshots/week2_airline_delay_rate.png`, `screenshots/week2_delay_by_time_block.png`, `screenshots/week2_delay_causes.png`

## Risks / Blockers

- Tableau Public dashboard publishing still needs to be completed manually in the Tableau app.
- Current analysis uses January 2024 only; more months should be downloaded to make the final dashboard stronger.
- Large raw and processed datasets are intentionally excluded from GitHub, so the repo should include scripts and notes while data is reproduced locally from BTS.
