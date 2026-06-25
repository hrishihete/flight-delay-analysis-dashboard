# Week 1 Notes

## Setup Status

Python EDA tooling is confirmed in this workspace using the available Codex Python runtime:

- pandas 3.0.1
- matplotlib 3.11.0
- seaborn 0.13.2
- SQLite via Python `sqlite3` 3.50.4

Git is not available on PATH in this shell. Publish the repo using GitHub Desktop, the GitHub website, or install Git CLI and rerun `git status`.

Tableau Public was not discoverable as a command-line executable. Confirm manually by opening Tableau Public and connecting to a CSV from `data/processed`.

## Data Source

Primary dataset: BTS TranStats `Reporting Carrier On-Time Performance (1987-present)`.

Official source page saved locally at:

`data/raw/bts_transtats_download_page.html`

Downloaded Week 1 slice:

`data/raw/bts_on_time_2024_01.zip`

Processed outputs:

- `data/processed/week1_sample_for_tableau.csv`
- `data/processed/flight_delay_week1.sqlite`

Use BTS fields related to flight date, airline, origin/destination airports, departure/arrival delays, cancellation/diversion flags, distance, and delay cause minutes.

## 20+ Columns To Explore

1. Year
2. Quarter
3. Month
4. DayofMonth
5. DayOfWeek
6. FlightDate
7. Reporting_Airline
8. DOT_ID_Reporting_Airline
9. IATA_CODE_Reporting_Airline
10. Tail_Number
11. Flight_Number_Reporting_Airline
12. Origin
13. OriginCityName
14. OriginState
15. Dest
16. DestCityName
17. DestState
18. CRSDepTime
19. DepTime
20. DepDelay
21. DepDel15
22. DepTimeBlk
23. CRSArrTime
24. ArrTime
25. ArrDelay
26. ArrDel15
27. ArrTimeBlk
28. Cancelled
29. CancellationCode
30. Diverted
31. CRSElapsedTime
32. ActualElapsedTime
33. AirTime
34. Flights
35. Distance
36. DistanceGroup
37. CarrierDelay
38. WeatherDelay
39. NASDelay
40. SecurityDelay
41. LateAircraftDelay

## Initial Questions For EDA

- Which airlines have the highest share of arrival delays of 15+ minutes?
- Which origin and destination airports show the strongest delay patterns?
- Do delays vary more by month, day of week, or departure time block?
- Which delay causes dominate: carrier, weather, NAS, security, or late aircraft?
- Are cancellation and diversion patterns concentrated by airport or season?

## Security Note

The reference notebook in Downloads appears to include a hard-coded Kaggle API credential. Do not copy credentials into this repo. Rotate that Kaggle token if it is active.
