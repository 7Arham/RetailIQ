
from pathlib import Path
import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
DATA = PROJECT / "data" / "retail_external_features.csv"
PRED = PROJECT / "outputs" / "validation_predictions.csv"
PLAN = PROJECT / "outputs" / "inventory_plan.csv"

app = FastAPI(title="RetailIQ API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def load(path):
    df = pd.read_csv(path)
    if "date" in df:
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    return df

def records(df):
    return df.replace({np.nan: None}).to_dict("records")

def predictions():
    df = load(PRED)
    return df.rename(columns={"sales": "actual"}) if "sales" in df and "actual" not in df else df

@app.get("/api/summary")
def summary():
    p, i, d = predictions(), load(PLAN), load(DATA)
    e = p["actual"].to_numpy() - p["prediction"].to_numpy()
    return {
        "mae": float(np.mean(np.abs(e))),
        "rmse": float(np.sqrt(np.mean(e**2))),
        "wape": float(np.sum(np.abs(e)) / max(np.sum(np.abs(p["actual"])), 1e-9) * 100),
        "order_units": int(i["recommended_order"].sum()),
        "purchase_cost": float(i["estimated_purchase_cost"].sum()),
        "unmet_demand": float(i["unmet_demand"].sum()),
        "trend": records(d.groupby("date", as_index=False)["sales"].sum().sort_values("date").tail(120)),
        "categories": [
            {"family": r.family, "units": int(r.recommended_order)}
            for r in i.groupby("family", as_index=False)["recommended_order"].sum()
              .sort_values("recommended_order", ascending=False).head(8).itertuples()
              if r.recommended_order > 0
        ]
    }

@app.get("/api/predictions")
def get_predictions():
    return {"rows": records(predictions().tail(100))}

@app.get("/api/inventory")
def inventory():
    return {"rows": records(load(PLAN))}

@app.get("/api/data")
def data():
    d = load(DATA).tail(100)
    return {"columns": d.columns.tolist(), "rows": records(d)}

app.mount("/", StaticFiles(directory=ROOT / "frontend", html=True), name="frontend")
