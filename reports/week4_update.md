# Weekly Update

This week I analyzed the top 10 airlines by average delay time using the cleaned BTS January 2024 flight dataset.
I filtered the analysis to completed flights only so cancelled and diverted records would not distort average delay calculations.
I ranked airlines by average arrival delay minutes and added context using flight volume, delayed arrival count, and arrival delay rate.
I created a bar chart for the top 10 airlines by average delay and a scatter chart comparing flight volume against average delay.
I discovered which airlines had the highest average arrival delay among carriers with meaningful January 2024 flight volume.
I saved the results as CSV summaries, a SQLite database, screenshots, a notebook, and a Markdown report.
Next I will add these visuals into Tableau and combine them with the earlier delay-cause dashboard views.

## Work Artifacts

- Repo: https://github.com/hrishihete/flight-delay-analysis-dashboard
- Data source: BTS TranStats Reporting Carrier On-Time Performance, January 2024
- Analysis script: `src/analyze_airline_average_delay.py`
- Notebook: `notebooks/week4_airline_average_delay.ipynb`
- Report: `reports/airline_average_delay_analysis.md`
- Screenshots: `screenshots/week4_top10_airlines_avg_delay_bar.png`, `screenshots/week4_airline_avg_delay_scatter.png`

## Risks / Blockers

- Tableau dashboard publishing still needs to be completed manually in Tableau Public.
- The current analysis uses January 2024 only; expanding to multiple months will make airline rankings more stable.
- Large processed CSV and SQLite outputs are kept local but can be regenerated using the provided scripts.
