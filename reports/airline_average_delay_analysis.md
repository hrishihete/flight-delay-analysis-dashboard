# Top 10 Airlines by Average Delay Time

Source: BTS Reporting Carrier On-Time Performance, January 2024.

## Method

- Used the cleaned January 2024 BTS flight delay dataset.
- Filtered to completed flights only, excluding cancelled and diverted records from average delay calculations.
- Ranked airlines with at least 500 completed flights.
- Primary metric: average arrival delay minutes (`ARR_DELAY`).
- Secondary context: arrival delay rate, departure delay average, and positive-only average arrival delay.

## Overview

- Airlines analyzed after volume filter: 15
- Weighted average arrival delay across included airlines: 10.35 minutes
- Highest average arrival delay airline: AA at 19.17 minutes
- AA arrival delay rate: 29.37%

## Top 10 Airlines

| OP_UNIQUE_CARRIER   | flights   | delayed_arrivals   | arrival_delay_rate_pct   | avg_arrival_delay_minutes   | avg_departure_delay_minutes   | avg_positive_arrival_delay_minutes   |
|:--------------------|:----------|:-------------------|:-------------------------|:----------------------------|:------------------------------|:-------------------------------------|
| AA                  | 75,889    | 22,292             | 29.37                    | 19.17                       | 22.53                         | 26.67                                |
| OO                  | 54,206    | 13,082             | 24.13                    | 15.20                       | 19.58                         | 24.29                                |
| OH                  | 15,539    | 3,924              | 25.25                    | 14.99                       | 18.51                         | 24.27                                |
| F9                  | 14,045    | 3,814              | 27.16                    | 14.72                       | 18.57                         | 24.35                                |
| B6                  | 19,172    | 5,565              | 29.03                    | 13.52                       | 18.98                         | 23.62                                |
| MQ                  | 19,740    | 5,473              | 27.73                    | 13.35                       | 15.12                         | 20.22                                |
| HA                  | 6,475     | 1,738              | 26.84                    | 10.66                       | 9.87                          | 14.05                                |
| 9E                  | 16,219    | 3,771              | 23.25                    | 10.56                       | 16.84                         | 21.71                                |
| G4                  | 8,366     | 1,869              | 22.34                    | 10.53                       | 15.24                         | 22.52                                |
| AS                  | 14,495    | 3,995              | 27.56                    | 10.38                       | 15.49                         | 18.95                                |

## Outputs

- `data/processed/airline_average_delay_summary_2024_01.csv`
- `data/processed/top10_airlines_average_delay_2024_01.csv`
- `data/processed/airline_average_delay_2024_01.sqlite`
- `screenshots/week4_top10_airlines_avg_delay_bar.png`
- `screenshots/week4_airline_avg_delay_scatter.png`