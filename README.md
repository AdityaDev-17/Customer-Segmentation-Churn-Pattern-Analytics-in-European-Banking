# Customer Segmentation & Churn Pattern Analytics — Dashboard

Streamlit dashboard for the Customer Segmentation & Churn Pattern Analytics
in European Banking project (Unified Mentor capstone).

**Live demo:** https://adityadev-17-customer-segmentation-chur-streamlit-appapp-oaizhf.streamlit.app/
*(Free-tier hosting — the app may take 30–60 seconds to wake up if it has been idle.)*

## Setup

1. Ensure Python 3.9+ is installed.
2. From the project root, create and activate a virtual environment (recommended): 
python -m venv .venv
.venv\Scripts\Activate.ps1
3. Install dependencies: pip install -r streamlit_app\requirements.txt

## Running the app

From the **project root** (not inside `streamlit_app/`), run: streamlit run streamlit_app\app.py


The app will open automatically in your browser at `http://localhost:8501`.

## Project structure
streamlit_app/
├── app.py # Main entry point — all tabs assembled here
├── requirements.txt
├── README.md
├── data/
│ └── df_clean_for_dashboard.csv # Cleaned, segmented dataset (from notebook Phase 2)
├── models/
│ ├── random_forest_churn_model.pkl
│ ├── scaler.pkl
│ └── feature_columns.pkl
└── utils/
├── data_loader.py # Cached data/model loading
├── kpi_calculator.py # 5 core KPI calculations (OOP)
├── filters.py # Shared sidebar filters (persist across tabs)
├── model_predictor.py # Feature engineering + RF prediction wrapper
├── geography_analysis.py # Geography tab
├── age_tenure_analysis.py # Age & Tenure tab
└── high_value_explorer.py # High-Value Explorer tab


## Dashboard tabs

- **App** — Overview KPIs: overall churn rate, high-value churn ratio, engagement drop indicator, revenue at risk
- **Geography** — Country-wise churn rates, Geography×AgeGroup and Geography×Gender interactions
- **Age & Tenure** — Age/Tenure group churn comparisons, Age×Tenure interaction
- **High-Value Explorer** — High-value customer churn analysis, revenue at risk, retained vs churned profile comparison
- **Predictor** — Bonus Random Forest risk scoring (batch + single "what-if" prediction)

Note: Predictor risk scores are relative rankings, not calibrated probabilities
(model trained with `class_weight='balanced'` to improve recall on the
minority churn class, which shifts raw probability outputs upward).