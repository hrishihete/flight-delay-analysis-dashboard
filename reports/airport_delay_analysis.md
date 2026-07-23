# Airport-Wise Delay Analysis

Source: BTS Reporting Carrier On-Time Performance, January 2024.

## Method

- Used the cleaned January 2024 BTS flight delay dataset.
- Grouped records by origin airport and destination airport separately.
- Filtered to airports with at least 500 completed flights to avoid unstable small-volume rankings.
- Calculated grouped metrics for flight count, average arrival/departure delay, delay rate, cancellations, diversions, distance, and delay-cause minutes.

## Overview

- Origin airports analyzed after volume filter: 122
- Destination airports analyzed after volume filter: 123
- Highest average-delay origin airport: CID (Cedar Rapids/Iowa City, IA) at 43.30 minutes.
- Highest average-delay destination airport: PGD (Punta Gorda, FL) at 28.04 minutes.
- Highest NAS-delay origin airport: ORD (Chicago, IL) with 91,249 NAS-delay minutes.

## Top 10 Origin Airports by Average Arrival Delay

| airport   | city_name                  | state   | flights   | avg_arrival_delay_minutes   | arrival_delay_rate_pct   | cancelled_flights   | nas_delay_minutes   | weather_delay_minutes   |
|:----------|:---------------------------|:--------|:----------|:----------------------------|:-------------------------|:--------------------|:--------------------|:------------------------|
| CID       | Cedar Rapids/Iowa City, IA | IA      | 523       | 43.30                       | 35.76                    | 63                  | 2,952               | 7,249                   |
| SGF       | Springfield, MO            | MO      | 574       | 35.92                       | 31.18                    | 31                  | 4,462               | 8,456                   |
| EGE       | Eagle, CO                  | CO      | 622       | 29.91                       | 34.08                    | 7                   | 2,798               | 887                     |
| DSM       | Des Moines, IA             | IA      | 1,151     | 29.73                       | 32.84                    | 101                 | 7,360               | 8,350                   |
| ASE       | Aspen, CO                  | CO      | 863       | 23.87                       | 34.07                    | 107                 | 4,196               | 6,294                   |
| GRR       | Grand Rapids, MI           | MI      | 1,467     | 23.02                       | 33.27                    | 99                  | 9,161               | 8,899                   |
| XNA       | Fayetteville, AR           | AR      | 944       | 22.89                       | 30.83                    | 33                  | 6,569               | 6,866                   |
| BZN       | Bozeman, MT                | MT      | 815       | 22.63                       | 23.68                    | 26                  | 2,899               | 4,136                   |
| MSN       | Madison, WI                | WI      | 794       | 21.82                       | 30.73                    | 41                  | 3,713               | 1,951                   |
| HPN       | White Plains, NY           | NY      | 1,034     | 20.85                       | 30.66                    | 36                  | 4,774               | 4,509                   |

## Top 10 Destination Airports by Average Arrival Delay

| airport   | city_name                  | state   | flights   | avg_arrival_delay_minutes   | arrival_delay_rate_pct   | cancelled_flights   | nas_delay_minutes   | weather_delay_minutes   |
|:----------|:---------------------------|:--------|:----------|:----------------------------|:-------------------------|:--------------------|:--------------------|:------------------------|
| PGD       | Punta Gorda, FL            | FL      | 525       | 28.04                       | 32.57                    | 11                  | 3,187               | 7,133                   |
| CID       | Cedar Rapids/Iowa City, IA | IA      | 517       | 23.07                       | 29.01                    | 61                  | 1,440               | 5,614                   |
| DFW       | Dallas/Fort Worth, TX      | TX      | 22,850    | 22.93                       | 30.98                    | 694                 | 120,158             | 72,815                  |
| ASE       | Aspen, CO                  | CO      | 849       | 18.38                       | 35.10                    | 55                  | 5,816               | 3,661                   |
| GRR       | Grand Rapids, MI           | MI      | 1,465     | 17.93                       | 29.56                    | 97                  | 3,609               | 8,515                   |
| DSM       | Des Moines, IA             | IA      | 1,161     | 17.81                       | 30.40                    | 93                  | 4,832               | 3,494                   |
| HPN       | White Plains, NY           | NY      | 1,029     | 17.80                       | 26.63                    | 32                  | 3,139               | 3,122                   |
| BUF       | Buffalo, NY                | NY      | 1,363     | 17.15                       | 28.32                    | 212                 | 4,048               | 5,480                   |
| MIA       | Miami, FL                  | FL      | 9,945     | 16.82                       | 30.76                    | 256                 | 54,034              | 12,892                  |
| SGF       | Springfield, MO            | MO      | 569       | 16.41                       | 30.23                    | 28                  | 3,051               | 3,679                   |

## Top 10 Origin Airports by NAS Delay Minutes

| airport   | city_name             | state   | flights   | arrival_delay_rate_pct   | nas_delay_minutes   | weather_delay_minutes   | total_cause_delay_minutes   |
|:----------|:----------------------|:--------|:----------|:-------------------------|:--------------------|:------------------------|:----------------------------|
| ORD       | Chicago, IL           | IL      | 18,816    | 32.30                    | 91,249              | 77,647                  | 500,197                     |
| DFW       | Dallas/Fort Worth, TX | TX      | 22,808    | 30.39                    | 81,732              | 64,712                  | 519,882                     |
| ATL       | Atlanta, GA           | GA      | 25,963    | 20.97                    | 60,371              | 45,126                  | 354,153                     |
| MCO       | Orlando, FL           | FL      | 13,844    | 26.74                    | 53,794              | 10,270                  | 260,074                     |
| DEN       | Denver, CO            | CO      | 22,309    | 26.00                    | 51,281              | 26,431                  | 360,846                     |
| LGA       | New York, NY          | NY      | 12,086    | 21.73                    | 47,407              | 12,578                  | 221,742                     |
| DTW       | Detroit, MI           | MI      | 9,126     | 30.85                    | 47,055              | 57,124                  | 247,702                     |
| BOS       | Boston, MA            | MA      | 9,775     | 25.18                    | 46,906              | 20,028                  | 196,441                     |
| PHL       | Philadelphia, PA      | PA      | 6,735     | 26.43                    | 46,339              | 19,070                  | 160,984                     |
| DCA       | Washington, DC        | VA      | 10,811    | 23.23                    | 45,948              | 32,491                  | 221,080                     |

## Outputs

- `data/processed/airport_delay_analysis_2024_01.sqlite`
- `data/processed/origin_airport_delay_summary_2024_01.csv`
- `data/processed/destination_airport_delay_summary_2024_01.csv`
- `data/processed/top10_origin_airports_by_avg_delay_2024_01.csv`
- `data/processed/top10_destination_airports_by_avg_delay_2024_01.csv`
- `data/processed/top10_origin_airports_by_nas_delay_2024_01.csv`
- `screenshots/week5_top10_origin_airports_avg_delay.png`
- `screenshots/week5_top10_destination_airports_avg_delay.png`
- `screenshots/week5_origin_airport_delay_scatter.png`
- `screenshots/week5_top10_origin_airports_nas_delay.png`