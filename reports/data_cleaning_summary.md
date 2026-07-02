# Data Cleaning Summary

Source: BTS Reporting Carrier On-Time Performance, January 2024.

- Rows loaded: 547,271
- Source columns retained after filtering: 39
- Output columns after derived flags: 44
- Completed flights: 525,370
- Cancelled flights: 20,389
- Diverted flights: 1,512
- Arrival delay rate for completed flights: 24.06%
- Departure delay rate for completed flights: 23.09%

## Null Handling

- Delay-cause nulls were filled with `0` because BTS leaves these fields blank when no qualifying delay cause exists.
- `CANCELLATION_CODE` nulls were filled with `Not Cancelled`.
- Missing arrival/departure delay indicators for completed flights were filled with `0`.
- Null flags were added for original departure and arrival delay nulls.

## Top Null Fields Before/After Cleaning

|                     |   nulls_before |   nulls_after |   nulls_removed |
|:--------------------|---------------:|--------------:|----------------:|
| CANCELLATION_CODE   |         526882 |             0 |          526882 |
| CARRIER_DELAY       |         420861 |             0 |          420861 |
| SECURITY_DELAY      |         420861 |             0 |          420861 |
| WEATHER_DELAY       |         420861 |             0 |          420861 |
| LATE_AIRCRAFT_DELAY |         420861 |             0 |          420861 |
| NAS_DELAY           |         420861 |             0 |          420861 |
| ACTUAL_ELAPSED_TIME |          21901 |         21901 |               0 |
| AIR_TIME            |          21901 |         21901 |               0 |
| ARR_DELAY           |          21901 |         21901 |               0 |
| ARR_DEL15           |          21901 |         21901 |               0 |
| ARR_TIME            |          20633 |         20633 |               0 |
| DEP_DEL15           |          19858 |         19858 |               0 |

## Outputs

- `data/processed/flight_delay_cleaned_2024_01.csv`
- `data/processed/flight_delay_cleaned_2024_01.sqlite`
- `screenshots/week2_airline_delay_rate.png`
- `screenshots/week2_delay_by_time_block.png`
- `screenshots/week2_delay_causes.png`
