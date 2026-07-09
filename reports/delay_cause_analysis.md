# Delay Cause Analysis

Source: BTS Reporting Carrier On-Time Performance, January 2024.

## Overview

- Completed flights analyzed: 525,370
- Delayed arrivals: 126,410
- Arrival delay rate: 24.06%
- Flights with reported delay-cause minutes: 126,410
- Total reported delay-cause minutes: 9,538,664

## Main Findings

- Largest delay cause: Late Aircraft with 3,715,582 minutes (38.95% of reported cause minutes).
- Highest carrier-delay airline by minutes: AA with 610,041 carrier-delay minutes.
- Highest NAS-delay origin airport by minutes: ORD (Chicago, IL) with 91,249 NAS-delay minutes.
- Peak time block by total cause minutes: 1800-1859 with 759,237 reported delay minutes.

## Delay Cause Summary

| cause_code          | cause         |   total_delay_minutes |   flights_with_cause |   share_of_cause_minutes_pct |   avg_minutes_per_affected_flight |
|:--------------------|:--------------|----------------------:|---------------------:|-----------------------------:|----------------------------------:|
| LATE_AIRCRAFT_DELAY | Late Aircraft |             3,715,582 |               63,485 |                        38.95 |                             58.53 |
| CARRIER_DELAY       | Carrier       |             3,111,412 |               66,482 |                        32.62 |                             46.8  |
| NAS_DELAY           | NAS           |             1,709,694 |               66,322 |                        17.92 |                             25.78 |
| WEATHER_DELAY       | Weather       |               979,360 |               12,282 |                        10.27 |                             79.74 |
| SECURITY_DELAY      | Security      |                22,616 |                  864 |                         0.24 |                             26.18 |

## Top 10 Airlines by Carrier Delay Minutes

| OP_UNIQUE_CARRIER   |   flights |   delayed_arrivals |   arrival_delay_rate_pct |   carrier_delay_minutes |   late_aircraft_delay_minutes |
|:--------------------|----------:|-------------------:|-------------------------:|------------------------:|------------------------------:|
| AA                  |    75,889 |             22,292 |                    29.37 |                 610,041 |                       889,904 |
| OO                  |    54,206 |             13,082 |                    24.13 |                 581,854 |                       249,238 |
| DL                  |    73,722 |             13,930 |                    18.9  |                 423,363 |                       288,500 |
| WN                  |   111,613 |             26,310 |                    23.57 |                 379,809 |                       668,111 |
| UA                  |    54,003 |             11,659 |                    21.59 |                 283,178 |                       413,094 |
| B6                  |    19,172 |              5,565 |                    29.03 |                 173,848 |                       157,993 |
| OH                  |    15,539 |              3,924 |                    25.25 |                 100,741 |                       161,728 |
| 9E                  |    16,219 |              3,771 |                    23.25 |                  90,471 |                       138,168 |
| NK                  |    20,081 |              5,274 |                    26.26 |                  89,128 |                        96,935 |
| F9                  |    14,045 |              3,814 |                    27.16 |                  87,728 |                       171,298 |

## Top 10 Origin Airports by NAS Delay Minutes

| ORIGIN   | ORIGIN_CITY_NAME      |   flights |   delayed_arrivals |   arrival_delay_rate_pct |   nas_delay_minutes |   weather_delay_minutes |
|:---------|:----------------------|----------:|-------------------:|-------------------------:|--------------------:|------------------------:|
| ORD      | Chicago, IL           |    18,816 |              6,077 |                    32.3  |              91,249 |                  77,647 |
| DFW      | Dallas/Fort Worth, TX |    22,808 |              6,931 |                    30.39 |              81,732 |                  64,712 |
| ATL      | Atlanta, GA           |    25,963 |              5,445 |                    20.97 |              60,371 |                  45,126 |
| MCO      | Orlando, FL           |    13,844 |              3,702 |                    26.74 |              53,794 |                  10,270 |
| DEN      | Denver, CO            |    22,309 |              5,800 |                    26    |              51,281 |                  26,431 |
| LGA      | New York, NY          |    12,086 |              2,626 |                    21.73 |              47,407 |                  12,578 |
| DTW      | Detroit, MI           |     9,126 |              2,815 |                    30.85 |              47,055 |                  57,124 |
| BOS      | Boston, MA            |     9,775 |              2,461 |                    25.18 |              46,906 |                  20,028 |
| PHL      | Philadelphia, PA      |     6,735 |              1,780 |                    26.43 |              46,339 |                  19,070 |
| DCA      | Washington, DC        |    10,811 |              2,511 |                    23.23 |              45,948 |                  32,491 |

## Outputs

- `data/processed/delay_cause_analysis_2024_01.sqlite`
- `data/processed/delay_cause_summary_2024_01.csv`
- `data/processed/delay_cause_by_airline_2024_01.csv`
- `data/processed/delay_cause_by_origin_2024_01.csv`
- `data/processed/delay_cause_by_time_block_2024_01.csv`
- `screenshots/week3_total_delay_minutes_by_cause.png`
- `screenshots/week3_delay_cause_share.png`
- `screenshots/week3_top_airlines_carrier_delay.png`
- `screenshots/week3_delay_cause_time_heatmap.png`