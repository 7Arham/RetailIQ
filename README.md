Smart Retail Demand Forecasting & Inventory Optimization
Project Overview
This academic project demonstrates retail demand forecasting and inventory planning. It uses historical sales data with weather and social-trend features, produces demand predictions, and recommends inventory orders under a purchasing budget.
Data note: The weather and social-trend demo features were synthetic demonstration data—not actual historical weather or real search/social-media trends.

Main Features
- Machine-learning demand forecasting.
- Daily sales trend and forecast analytics.
- Weather and trend feature integration.
- Inventory optimization with a budget constraint.
- Dashboard for forecast metrics and inventory recommendations.
Project Structure
retail/
├── data/
│   ├── retail_merged.csv
│   ├── retail_external_features.csv
│   ├── train.csv
│   ├── stores.csv
│   └── holidays_events.csv
├── notebooks/
│   ├── eda.ipynb
│   └── model.ipynb
├── outputs/
│   ├── demand_model.joblib
│   ├── validation_predictions.csv
│   └── inventory_plan.csv
├── optimize.py
└── web/
    ├── backend.py
    └── frontend/
        ├── index.html
        ├── style.css
        └── script.js
Requirements
Use a compatible Python version (Python 3.10+ recommended). Install the packages used by the notebook and API:
pip install pandas numpy scikit-learn xgboost scipy fastapi uvicorn joblib
On Windows, activate your virtual environment (adjust its name/path if needed):
.\venv2\Scripts\activate
Run commands from the retail project directory unless specified.
Workflow
1. Data
The model notebook uses:
data/retail_external_features.csv
This file already includes the merged sales, weather, and trend columns. You do not need to run a merge script every time.
2. Train and validate the model
Open notebooks/model.ipynb in VS Code/Jupyter and run all cells in order.

Expected outputs:
- outputs/demand_model.joblib
- outputs/validation_predictions.csv
3. Generate the inventory plan
From the retail directory:
python optimize.py
Expected output:
- outputs/inventory_plan.csv
The optimizer uses assumptions defined in optimize.py (planning horizon, unit cost, stock, penalties, and budget). The budget is a maximum limit; actual recommended purchase cost can be lower.
4. Start the dashboard
From retail/web:
uvicorn backend:app --reload
Open http://127.0.0.1:8000.

API endpoints:
- /api/summary
- /api/predictions
- /api/inventory
- /api/data
Dashboard Sections
- Overview: summary metrics.
- Forecast Analytics: forecast error metrics and sales/category charts.
- Inventory Planner: recommended orders, projected inventory, unmet demand, and estimated cost.
- Data Explorer: sample sales records.
Interpretation Notes
- The current workflow is daily.
- The inventory planning horizon is 7 days when PLANNING_DAYS = 7.
- Validation predictions are not genuine future forecasts. Inventory recommendations based on them are for academic demonstration, not real purchasing.
- Weather/trend features are synthetic unless replaced with authentic sourced data.
- Forecast metrics reflect the notebook's validation data.
Rebuilding Outputs
1. Run all cells in notebooks/model.ipynb.
2. Run python optimize.py.
3. Restart the backend if needed.
Recreate the merged external-feature CSV only if you update the underlying data or merge logic. Keep stores.csv and holidays_events.csv if you may retrain or add features later.
Disclaimer
This is an academic demonstration. Do not use its forecasts or order recommendations for actual purchasing without proper validation, authentic external data, and realistic inventory/cost assumptions.
