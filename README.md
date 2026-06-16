# DemandIQ — Manufacturing Demand Forecasting & Decision Support

> Final Year Project | B.Tech / MBA | Manufacturing Intelligence Platform

A production-grade demand forecasting dashboard for manufacturing companies. Combines statistical time-series models (SARIMA, SARIMAX, ARIMA, ARIMAX) with exogenous economic drivers to forecast 12-month demand, profitability, and inventory requirements across a multi-product portfolio.

---

## Live Demo

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://demandiq-tdnrvdyeytuxj9wxvstgwk.streamlit.app/)

---

## Features

| Module | Description |
|---|---|
| **Executive Overview** | Portfolio KPIs, demand trend, category share, model distribution |
| **Product Deep-Dive** | Per-product forecast chart, accuracy comparison, inventory metrics |
| **Portfolio Insights** | Efficiency quadrant, MAPE heatmap, category trend, model comparison |
| **Decision Support** | Growth alerts, priority ranking, decision matrix, strategic recommendation |
| **Profitability Analysis** | Revenue vs cost vs margin by product and category, low-margin warnings |
| **Run History** | Full version control — every pipeline run logged, MAPE trend, restore any run |

---

## Tech Stack

- **Forecasting**: `statsmodels` SARIMA / SARIMAX / ARIMA / ARIMAX
- **Feature Importance**: `scikit-learn` Random Forest
- **Dashboard**: `streamlit` + `plotly`
- **Version Control**: Git + JSON run log with snapshot restore
- **Deployment**: Streamlit Community Cloud

---

## Project Structure

```
demandiq/
├── app.py                    # Streamlit dashboard (single file)
├── src/
│   └── pipeline.py           # Forecasting pipeline with run logging
├── outputs/                  # Generated CSVs (latest run)
│   ├── model_metrics.csv
│   ├── forecast_results.csv
│   ├── future_forecasts.csv
│   ├── product_summary.csv
│   ├── feature_importance.csv
│   └── final_business_report.csv
├── runs/
│   ├── run_log.json          # All run metadata (version history)
│   └── run_YYYYMMDD_HHMMSS_*/  # CSV snapshot per run
├── data/
│   └── dataset.csv           # Input dataset (not tracked in git)
├── .streamlit/
│   └── config.toml           # Dark theme config
├── requirements.txt
└── .gitignore
```

---

## Forecasting Methodology

For each product, the pipeline:

1. **Splits data** into train (all but last 12 months) and test (last 12 months)
2. **Fits two models**: Baseline SARIMA/ARIMA and Exogenous SARIMAX/ARIMAX
3. **Selects the winner** by MAPE on the test set
4. **Projects 12 months forward** with trend-adjusted exogenous features
5. **Computes business metrics**: demand level, margin band, safety stock, reorder point, priority score
6. **Logs the run** to `runs/run_log.json` with a full CSV snapshot

Exogenous features used:
- `Rainfall_Index` — seasonal demand driver (Tractors)
- `Industrial_Index` — economic activity (CNC machines)
- `Diesel_Price`, `Steel_Price` — input cost drivers
- `Govt_Subsidy_Flag`, `Festival_Flag` — demand event flags

---

## Running Locally

```bash
# 1. Clone
git clone https://github.com/yourusername/demandiq.git
cd demandiq

# 2. Install
pip install -r requirements.txt

# 3. Add your dataset
cp your_dataset.csv data/dataset.csv

# 4. Run pipeline
python src/pipeline.py --notes "Initial run"

# 5. Launch dashboard
streamlit run app.py
```

**CLI options for the pipeline:**

```bash
python src/pipeline.py --data path/to/data.csv --notes "Updated steel prices Q2"
```

---

## Deploying to Streamlit Cloud

1. Push this repo to GitHub (make sure `outputs/` and `runs/` are committed)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file path** to `app.py`
5. Deploy — done

> **Note**: Streamlit Cloud runs are ephemeral. Pre-commit your `outputs/` CSVs so the dashboard has data on first load.

---

## Dataset Schema

| Column | Description |
|---|---|
| `Date` | Month start date (YYYY-MM-DD) |
| `Product_Name` | Product identifier |
| `Category` | Product category (e.g., Tractor, CNC) |
| `Monthly_Sales` | Units sold |
| `Unit_Price` | Price per unit |
| `Revenue` | Monthly revenue |
| `Rainfall_Index` | Monthly rainfall index |
| `Industrial_Index` | Industrial activity index |
| `Diesel_Price` | Diesel price index |
| `Steel_Price` | Steel price index |
| `Govt_Subsidy_Flag` | 1 if govt subsidy active |
| `Festival_Flag` | 1 if festival season |
