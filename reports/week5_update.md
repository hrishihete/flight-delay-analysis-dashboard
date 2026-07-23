# Weekly Update

This week I completed airport-wise delay analysis using grouped aggregations on the cleaned BTS January 2024 flight dataset.
I grouped records separately by origin airport and destination airport to compare average delay, delay rates, flight volume, cancellations, diversions, and delay-cause minutes.
I filtered to airports with at least 500 completed flights so the rankings are based on meaningful traffic volume.
I created summary tables for origin airports, destination airports, top 10 average-delay airports, and top NAS-delay origin airports.
I generated bar and scatter charts showing top average-delay airports, airport volume vs delay, and NAS delay concentration.
I discovered which airports had the highest average arrival delays and which origin airports contributed the most NAS delay minutes.
Next I will add the airport visuals into Tableau and combine them with airline and delay-cause dashboard views.

## Work Artifacts

- Repo: https://github.com/hrishihete/flight-delay-analysis-dashboard
- Data source: BTS TranStats Reporting Carrier On-Time Performance, January 2024
- Analysis script: `src/analyze_airport_delays.py`
- Notebook: `notebooks/week5_airport_delay_analysis.ipynb`
- Report: `reports/airport_delay_analysis.md`
- Screenshots: `screenshots/week5_top10_origin_airports_avg_delay.png`, `screenshots/week5_top10_destination_airports_avg_delay.png`, `screenshots/week5_origin_airport_delay_scatter.png`, `screenshots/week5_top10_origin_airports_nas_delay.png`

## Risks / Blockers

- Tableau dashboard publishing still needs to be completed manually in Tableau Public.
- Current analysis uses January 2024 only; adding multiple months will make airport rankings more stable.
- Large processed CSV and SQLite outputs are kept local but can be regenerated using the provided scripts.
