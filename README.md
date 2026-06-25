# Flight Delay Analysis & Dashboard

Analyze US flight delay patterns by airline, airport, and time using Python EDA, SQLite, and Tableau Public.

## Week 1 Scope

- Confirm Python EDA tooling: pandas, matplotlib, seaborn, SQLite.
- Identify a public US flight delay source from BTS TranStats / Kaggle.
- Explore 20+ fields relevant to delay analysis.
- Create an initial workspace structure for data, notebooks, scripts, reports, and Tableau assets.

## Project Structure

```text
data/
  raw/          # BTS/Kaggle downloads, kept out of git
  processed/    # cleaned samples and Tableau extracts
notebooks/      # EDA notebooks
src/            # reusable setup and EDA scripts
reports/        # Week notes, updates, exported charts
screenshots/    # setup or dashboard screenshots
tableau/        # Tableau Public workbook/export references
```

## Data Source

Primary source: BTS TranStats, `Reporting Carrier On-Time Performance (1987-present)`.

Official page:
https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ&QO_fu146_anzr=b0-gvzr

Kaggle alternative: `robikscube/flight-delay-dataset-20182022`.

Do not commit Kaggle API tokens. Keep credentials in your local Kaggle config or an untracked `.env` file.

## Tooling

Run the setup check with the bundled/runtime Python available on your machine:

```powershell
python src/week1_setup_check.py
```

In this Codex workspace, Python packages were confirmed with:

- pandas
- matplotlib
- seaborn
- sqlite3

Note: Git was not available on PATH in this shell, so repo publishing should be done through GitHub Desktop, the GitHub website, or after installing Git CLI.

## Repo Link

Add your GitHub repo link here once published:

`TODO: https://github.com/<username>/flight-delay-analysis-dashboard`
