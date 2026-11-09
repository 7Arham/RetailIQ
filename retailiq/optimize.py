
import os
import numpy as np
import pandas as pd
from scipy.optimize import linprog

ROOT = os.path.dirname(os.path.abspath(__file__))
PRED = os.path.join(ROOT, "outputs", "validation_predictions.csv")
OUT = os.path.join(ROOT, "outputs", "inventory_plan.csv")

# Settings
BUDGET = 250_000
UNIT_COST = 10
HOLDING_COST = 2
STOCKOUT_PENALTY = 25
INITIAL_STOCK = 0
PLANNING_DAYS = 7

# Load retrained model predictions
pred = pd.read_csv(PRED)
pred["prediction"] = pred["prediction"].clip(lower=0)

demand = (
    pred.groupby(["store_nbr", "family"], as_index=False)["prediction"]
    .mean()
    .rename(columns={"prediction": "daily_demand"})
)

demand["forecast_demand"] = demand["daily_demand"] * PLANNING_DAYS
demand["unit_cost"] = UNIT_COST
demand["holding_cost"] = HOLDING_COST
demand["stockout_penalty"] = STOCKOUT_PENALTY
demand["available_stock"] = INITIAL_STOCK

n = len(demand)
cost = demand["unit_cost"].to_numpy()
holding = demand["holding_cost"].to_numpy()
penalty = demand["stockout_penalty"].to_numpy()
stock = demand["available_stock"].to_numpy()
forecast = demand["forecast_demand"].to_numpy()

# Variables: purchases x, unmet demand u
c = np.r_[cost + holding, penalty]
A, b = [], []

for i in range(n):
    row = np.zeros(2 * n)
    row[i] = -1
    row[n + i] = -1
    A.append(row)
    b.append(stock[i] - forecast[i])

budget = np.zeros(2 * n)
budget[:n] = cost
A.append(budget)
b.append(BUDGET)

result = linprog(
    c,
    A_ub=np.array(A),
    b_ub=np.array(b),
    bounds=[(0, None)] * (2 * n),
    method="highs"
)

if not result.success:
    raise RuntimeError(result.message)

demand["recommended_order"] = np.floor(result.x[:n]).astype(int)
demand["unmet_demand"] = np.ceil(result.x[n:]).astype(int)
demand["projected_inventory"] = stock + demand["recommended_order"]
demand["estimated_purchase_cost"] = (
    demand["recommended_order"] * cost
)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
demand.to_csv(OUT, index=False)

print("Inventory optimization complete")
print("Total order:", demand["recommended_order"].sum())
print("Purchase cost:", demand["estimated_purchase_cost"].sum())
print("Unmet demand:", demand["unmet_demand"].sum())
print("Saved:", OUT)
