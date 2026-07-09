# Weekly Update

This week I analyzed delay causes in the cleaned BTS January 2024 flight delay dataset.
I compared the five BTS delay-cause categories: carrier, weather, NAS, security, and late aircraft.
I created summary tables by delay cause, airline, origin airport, and departure time block.
I generated charts showing total delay minutes by cause, cause share, top airlines by carrier delay, and cause patterns by time block.
I discovered which delay category contributed the largest share of reported delay minutes and which airlines/airports had the highest cause-specific delay totals.
I saved the outputs as CSV summaries, a SQLite database, screenshots, a notebook, and a Markdown report.
Next I will connect these delay-cause outputs to Tableau Public and build dashboard views for cause mix, airline comparison, airport impact, and time-of-day patterns.

## Work Artifacts

- Repo: https://github.com/hrishihete/flight-delay-analysis-dashboard
- Data source: BTS TranStats Reporting Carrier On-Time Performance, January 2024
- Analysis script: `src/analyze_delay_causes.py`
- Notebook: `notebooks/week3_delay_cause_analysis.ipynb`
- Report: `reports/delay_cause_analysis.md`
- Screenshots: `screenshots/week3_total_delay_minutes_by_cause.png`, `screenshots/week3_delay_cause_share.png`, `screenshots/week3_top_airlines_carrier_delay.png`, `screenshots/week3_delay_cause_time_heatmap.png`

## Risks / Blockers

- Tableau Public dashboard publishing still needs to be completed manually in Tableau.
- The current analysis uses January 2024 only; adding more months will make cause patterns more stable.
- Large processed CSV/SQLite outputs are not committed to GitHub, but they can be regenerated from the scripts.
