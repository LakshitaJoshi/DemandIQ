"""
DemandIQ — Main Forecasting Pipeline
Runs SARIMA / SARIMAX / ARIMA / ARIMAX per product,
selects best model, saves all output CSVs, and logs
each run to runs/run_log.json for in-app version control.
"""

import os
import json
import uuid
import warnings
import numpy as np
import pandas as pd
from datetime import datetime

from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.ensemble import RandomForestRegressor

warnings.filterwarnings("ignore")

# ─── Paths ────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH  = os.path.join(BASE_DIR, "data", "dataset.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
RUNS_DIR   = os.path.join(BASE_DIR, "runs")
RUN_LOG    = os.path.join(RUNS_DIR, "run_log.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(RUNS_DIR,   exist_ok=True)


# ─── Data Loading ─────────────────────────────────────
def load_dataset(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(["Product_Name", "Date"]).reset_index(drop=True)
    return df


# ─── Feature Engineering ──────────────────────────────
def calculate_cost_margin(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    base_ratio  = np.where(df["Category"] == "Tractor", 0.70, 0.66)
    steel_adj   = (df["Steel_Price"]  - df["Steel_Price"].mean())  / df["Steel_Price"].mean()
    diesel_adj  = (df["Diesel_Price"] - df["Diesel_Price"].mean()) / df["Diesel_Price"].mean()
    cost_ratio  = np.clip(base_ratio + 0.08 * steel_adj + 0.04 * diesel_adj, 0.55, 0.85)

    df["Estimated_Unit_Cost"] = df["Unit_Price"] * cost_ratio
    df["Total_Cost"]          = df["Monthly_Sales"] * df["Estimated_Unit_Cost"]
    df["Gross_Margin"]        = df["Revenue"] - df["Total_Cost"]
    df["Margin_Percentage"]   = np.where(
        df["Revenue"] != 0,
        (df["Gross_Margin"] / df["Revenue"]) * 100, 0
    )
    return df


# ─── Metrics ──────────────────────────────────────────
def mape(y_true, y_pred) -> float:
    y_true = np.where(np.array(y_true) == 0, 1, np.array(y_true))
    return float(np.mean(np.abs((y_true - np.array(y_pred)) / y_true)) * 100)


# ─── Train / Test Split ───────────────────────────────
def train_test_split_ts(df: pd.DataFrame, test_size: int = 12):
    df = df.sort_index()
    return df.iloc[:-test_size].copy(), df.iloc[-test_size:].copy()


# ─── Model Fitting ────────────────────────────────────
def fit_sarima(train_s, test_s, seasonal: bool = True):
    try:
        order   = (1, 1, 1)
        s_order = (1, 1, 1, 12) if seasonal else (0, 0, 0, 0)
        model   = SARIMAX(train_s, order=order, seasonal_order=s_order,
                          enforce_stationarity=False, enforce_invertibility=False)
        result  = model.fit(disp=False)
        return result, result.forecast(steps=len(test_s))
    except Exception:
        return None, pd.Series([train_s.mean()] * len(test_s), index=test_s.index)


def fit_sarimax(train_df, test_df, exog_cols, seasonal: bool = True):
    try:
        s_order = (1, 1, 1, 12) if seasonal else (0, 0, 0, 0)
        model   = SARIMAX(train_df["Monthly_Sales"], exog=train_df[exog_cols],
                          order=(1, 1, 1), seasonal_order=s_order,
                          enforce_stationarity=False, enforce_invertibility=False)
        result  = model.fit(disp=False)
        return result, result.forecast(steps=len(test_df), exog=test_df[exog_cols])
    except Exception:
        return None, pd.Series([train_df["Monthly_Sales"].mean()] * len(test_df), index=test_df.index)


# ─── Future Exogenous Features ────────────────────────
EXOG_COLS = ["Rainfall_Index", "Industrial_Index", "Diesel_Price",
             "Steel_Price", "Govt_Subsidy_Flag", "Festival_Flag"]


def create_future_exog(last_row, steps: int = 12) -> pd.DataFrame:
    future_dates = pd.date_range(
        start=last_row.name + pd.offsets.MonthBegin(1), periods=steps, freq="MS"
    )
    fdf = pd.DataFrame(index=future_dates)
    for col in ["Rainfall_Index", "Industrial_Index", "Diesel_Price", "Steel_Price"]:
        fdf[col] = last_row[col]
    fdf["Govt_Subsidy_Flag"] = 0
    fdf["Festival_Flag"]     = 0

    fdf["Industrial_Index"] += np.linspace(0.2, 2.0, steps)
    fdf["Diesel_Price"]     += np.linspace(0.1, 1.2, steps)
    fdf["Steel_Price"]      += np.linspace(0.1, 1.5, steps)

    for i, dt in enumerate(fdf.index):
        if dt.month in [7, 8, 9]:
            fdf.at[dt, "Rainfall_Index"] += 15
        if dt.month in [10, 11]:
            fdf.at[dt, "Festival_Flag"] = 1
        if dt.month in [4, 5]:
            fdf.at[dt, "Govt_Subsidy_Flag"] = 1
    return fdf


# ─── Business Classifiers ─────────────────────────────
def classify_demand_levels(summary: pd.DataFrame) -> pd.DataFrame:
    summary = summary.copy()
    if len(summary) < 3:
        summary["Demand_Level"] = "Moderate"
        return summary
    q1 = summary["Avg_Forecast_Sales"].quantile(0.33)
    q2 = summary["Avg_Forecast_Sales"].quantile(0.66)
    summary["Demand_Level"] = summary["Avg_Forecast_Sales"].apply(
        lambda x: "Low" if x <= q1 else ("Moderate" if x <= q2 else "High")
    )
    return summary


def assign_margin_band(margin_pct: float) -> str:
    if margin_pct >= 30: return "High Margin"
    if margin_pct >= 18: return "Moderate Margin"
    return "Low Margin"


def assign_risk_level(final_mape: float) -> str:
    if final_mape <= 5:  return "Low Risk"
    if final_mape <= 10: return "Moderate Risk"
    return "High Risk"


def assign_inventory_action(demand_level, growth_pct, margin_pct, final_mape) -> str:
    if demand_level == "High" and growth_pct > 8 and margin_pct >= 20 and final_mape <= 8:
        return "Increase Production"
    if demand_level == "High" and margin_pct < 20:
        return "Increase Carefully"
    if demand_level == "Moderate" and growth_pct >= 0:
        return "Maintain Production"
    if final_mape > 10:
        return "Monitor Closely"
    return "Controlled Inventory"


def calculate_reorder_metrics(df_product: pd.DataFrame):
    avg = df_product["Monthly_Sales"].mean()
    std = df_product["Monthly_Sales"].std()
    safety_stock  = 1.65 * std * np.sqrt(1.0) if pd.notnull(std) else 0
    reorder_point = avg * 1.0 + safety_stock
    return round(safety_stock, 2), round(reorder_point, 2)


# ─── Driver / Feature Importance ──────────────────────
def driver_analysis(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for product in df["Product_Name"].unique():
        temp = df[df["Product_Name"] == product].copy()
        if len(temp) < 20:
            continue
        rf = RandomForestRegressor(n_estimators=200, random_state=42, max_depth=6)
        rf.fit(temp[EXOG_COLS], temp["Monthly_Sales"])
        for col, imp in zip(EXOG_COLS, rf.feature_importances_):
            rows.append({"Product_Name": product, "Feature": col, "Importance": round(float(imp), 4)})
    return pd.DataFrame(rows)


# ─── Run Logging (Version Control) ────────────────────
def load_run_log() -> list:
    if os.path.exists(RUN_LOG):
        with open(RUN_LOG, "r") as f:
            return json.load(f)
    return []


def save_run_log(log: list):
    with open(RUN_LOG, "w") as f:
        json.dump(log, f, indent=2)


def log_run(run_meta: dict):
    """Append a run record to runs/run_log.json."""
    log = load_run_log()
    log.append(run_meta)
    save_run_log(log)
    # Also save the run's output snapshot
    run_dir = os.path.join(RUNS_DIR, run_meta["run_id"])
    os.makedirs(run_dir, exist_ok=True)
    for fname in ["model_metrics.csv", "product_summary.csv",
                  "future_forecasts.csv", "final_business_report.csv"]:
        src = os.path.join(OUTPUT_DIR, fname)
        dst = os.path.join(run_dir, fname)
        if os.path.exists(src):
            import shutil
            shutil.copy2(src, dst)


# ─── Main Pipeline ────────────────────────────────────
def main(data_path: str = DATA_PATH, notes: str = ""):
    start_time = datetime.now()
    print(f"\n{'─'*55}")
    print(f"  DemandIQ Pipeline  |  {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'─'*55}\n")

    df = load_dataset(data_path)
    df = calculate_cost_margin(df)

    metrics_rows, forecast_rows, future_rows, summary_rows = [], [], [], []

    for product in df["Product_Name"].unique():
        print(f"  → Processing: {product}")
        temp     = df[df["Product_Name"] == product].copy()
        temp     = temp.sort_values("Date").set_index("Date")
        temp.index = pd.DatetimeIndex(temp.index).to_period("M").to_timestamp()
        category = temp["Category"].iloc[0]
        seasonal = (category == "Tractor")

        train, test = train_test_split_ts(temp, test_size=12)

        baseline_model, baseline_fc = fit_sarima(train["Monthly_Sales"], test["Monthly_Sales"], seasonal)
        baseline_mape_val = round(mape(test["Monthly_Sales"], baseline_fc), 3)

        exog_model, exog_fc = fit_sarimax(train, test, EXOG_COLS, seasonal)
        exog_mape_val = round(mape(test["Monthly_Sales"], exog_fc), 3)

        if exog_mape_val < baseline_mape_val:
            final_name, final_model, final_fc, final_mape_val = (
                ("SARIMAX" if seasonal else "ARIMAX"), exog_model, exog_fc, exog_mape_val
            )
            best_selected = "Exogenous"
        else:
            final_name, final_model, final_fc, final_mape_val = (
                ("SARIMA" if seasonal else "ARIMA"), baseline_model, baseline_fc, baseline_mape_val
            )
            best_selected = "Baseline"

        mae_val  = round(mean_absolute_error(test["Monthly_Sales"], final_fc), 3)
        rmse_val = round(np.sqrt(mean_squared_error(test["Monthly_Sales"], final_fc)), 3)

        for dt, actual, pred in zip(test.index, test["Monthly_Sales"], final_fc):
            forecast_rows.append({
                "Date": dt, "Product_Name": product, "Category": category,
                "Actual_Sales": round(float(actual), 2),
                "Forecast_Sales": round(float(pred), 2),
                "Model_Used": final_name
            })

        last_row     = temp.iloc[-1]
        future_exog  = create_future_exog(last_row, steps=12)

        try:
            if best_selected == "Exogenous":
                future_fc = final_model.forecast(steps=12, exog=future_exog[EXOG_COLS])
            else:
                future_fc = final_model.forecast(steps=12)
        except Exception:
            future_fc = pd.Series([temp["Monthly_Sales"].mean()] * 12, index=future_exog.index)

        future_fc = np.maximum(future_fc, 0)

        avg_future   = round(float(np.mean(future_fc)), 2)
        avg_hist     = round(float(temp["Monthly_Sales"].mean()), 2)
        growth_pct   = round(((avg_future - avg_hist) / avg_hist) * 100, 2) if avg_hist != 0 else 0
        avg_price    = temp["Unit_Price"].iloc[-6:].mean()
        avg_cost     = temp["Estimated_Unit_Cost"].iloc[-6:].mean()

        total_rev, total_cost_f, total_margin = 0.0, 0.0, 0.0
        for dt, pred in zip(future_exog.index, future_fc):
            pred = float(pred)
            rev  = pred * avg_price
            cst  = pred * avg_cost
            mgn  = rev - cst
            mgn_pct = (mgn / rev * 100) if rev != 0 else 0
            total_rev   += rev
            total_cost_f += cst
            total_margin += mgn
            future_rows.append({
                "Date": dt, "Product_Name": product, "Category": category,
                "Forecast_Sales": round(pred, 2),
                "Expected_Revenue": round(rev, 2),
                "Expected_Cost": round(cst, 2),
                "Expected_Gross_Margin": round(mgn, 2),
                "Expected_Margin_Percentage": round(mgn_pct, 2)
            })

        avg_margin_pct_val = round(float(temp["Margin_Percentage"].mean()), 2)
        safety_s, reorder_p = calculate_reorder_metrics(temp)

        summary_rows.append({
            "Product_Name": product, "Category": category,
            "Final_Model": final_name, "Final_MAPE": final_mape_val,
            "Avg_Historical_Sales": avg_hist, "Avg_Forecast_Sales": avg_future,
            "Forecast_Growth_Percent": growth_pct,
            "Demand_Level": None,
            "Avg_Margin_Percentage": avg_margin_pct_val,
            "Margin_Band": assign_margin_band(avg_margin_pct_val),
            "Risk_Level": assign_risk_level(final_mape_val),
            "Inventory_Action": None, "Priority_Score": None,
            "Safety_Stock": safety_s, "Reorder_Point": reorder_p,
            "Expected_Annual_Revenue": round(total_rev, 2),
            "Expected_Annual_Cost": round(total_cost_f, 2),
            "Expected_Annual_Gross_Margin": round(total_margin, 2),
            "Recommendation": None
        })

        metrics_rows.append({
            "Product_Name": product, "Category": category,
            "Baseline_Model": "SARIMA" if seasonal else "ARIMA",
            "Baseline_MAPE": baseline_mape_val,
            "Exogenous_Model": "SARIMAX" if seasonal else "ARIMAX",
            "Exogenous_MAPE": exog_mape_val,
            "Final_Model": final_name, "Final_MAPE": final_mape_val,
            "MAE": mae_val, "RMSE": rmse_val,
            "Best_Model_Selected": best_selected
        })

    # ── Assemble DataFrames ──
    metrics_df  = pd.DataFrame(metrics_rows)
    forecast_df = pd.DataFrame(forecast_rows)
    future_df   = pd.DataFrame(future_rows)
    summary_df  = pd.DataFrame(summary_rows)

    summary_df = classify_demand_levels(summary_df)
    summary_df["Inventory_Action"] = summary_df.apply(
        lambda r: assign_inventory_action(
            r["Demand_Level"], r["Forecast_Growth_Percent"],
            r["Avg_Margin_Percentage"], r["Final_MAPE"]
        ), axis=1
    )
    summary_df["Priority_Score"] = summary_df.apply(
        lambda r: round(
            r["Avg_Forecast_Sales"] * 0.5 +
            r["Forecast_Growth_Percent"] * 10 +
            r["Avg_Margin_Percentage"] * 3 -
            r["Final_MAPE"] * 5, 2
        ), axis=1
    )
    summary_df["Recommendation"] = summary_df["Inventory_Action"]

    driver_df = driver_analysis(df)

    final_report_df = future_df.merge(
        summary_df[[
            "Product_Name", "Category", "Final_Model", "Final_MAPE",
            "Demand_Level", "Margin_Band", "Risk_Level", "Inventory_Action",
            "Priority_Score", "Safety_Stock", "Reorder_Point", "Recommendation"
        ]],
        on=["Product_Name", "Category"], how="left"
    )

    # ── Save CSVs ──
    metrics_df.to_csv(     os.path.join(OUTPUT_DIR, "model_metrics.csv"),        index=False)
    forecast_df.to_csv(    os.path.join(OUTPUT_DIR, "forecast_results.csv"),     index=False)
    future_df.to_csv(      os.path.join(OUTPUT_DIR, "future_forecasts.csv"),     index=False)
    summary_df.to_csv(     os.path.join(OUTPUT_DIR, "product_summary.csv"),      index=False)
    driver_df.to_csv(      os.path.join(OUTPUT_DIR, "feature_importance.csv"),   index=False)
    final_report_df.to_csv(os.path.join(OUTPUT_DIR, "final_business_report.csv"),index=False)
    df.to_csv(             os.path.join(OUTPUT_DIR, "historical_with_margin.csv"),index=False)

    # ── Log this run ──
    duration  = round((datetime.now() - start_time).total_seconds(), 1)
    run_id    = f"run_{start_time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    avg_mape  = round(float(summary_df["Final_MAPE"].mean()), 3)
    run_meta  = {
        "run_id":           run_id,
        "timestamp":        start_time.isoformat(),
        "duration_seconds": duration,
        "data_path":        os.path.basename(data_path),
        "products":         summary_df["Product_Name"].tolist(),
        "n_products":       len(summary_df),
        "avg_mape":         avg_mape,
        "model_counts":     summary_df["Final_Model"].value_counts().to_dict(),
        "demand_counts":    summary_df["Demand_Level"].value_counts().to_dict(),
        "notes":            notes,
        "status":           "success"
    }
    log_run(run_meta)

    print(f"\n  Avg MAPE : {avg_mape}%")
    print(f"  Duration : {duration}s")
    print(f"  Run ID   : {run_id}")
    print(f"\n{'─'*55}")
    print("  Pipeline completed. Outputs saved.")
    print(f"{'─'*55}\n")

    return run_meta


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="DemandIQ Forecasting Pipeline")
    parser.add_argument("--data",  default=DATA_PATH, help="Path to dataset CSV")
    parser.add_argument("--notes", default="",        help="Optional run notes")
    args = parser.parse_args()
    main(data_path=args.data, notes=args.notes)
