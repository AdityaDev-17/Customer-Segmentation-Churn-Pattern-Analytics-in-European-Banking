"""
4_Risk_Score_Predictor.py
Bonus module: Random Forest churn risk scoring.
Tab 1 — Batch scoring of the (filtered) customer base, with a downloadable
         ranked list of highest-risk customers for retention targeting.
Tab 2 — Manual "what-if" single-customer predictor for exploration.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.filters import SidebarFilterManager
from utils.model_predictor import ChurnPredictor

st.set_page_config(page_title="Risk Score Predictor", layout="wide")
st.title("Churn Risk Score Predictor")
st.caption("Random Forest model — bonus predictive module")

df = load_data()
filter_manager = SidebarFilterManager(df)
filtered_df = filter_manager.render_and_apply()

predictor = ChurnPredictor()

tab_batch, tab_whatif = st.tabs(["Batch Risk Scoring", "What-If Predictor"])

# ---------------- TAB 1: BATCH SCORING ----------------
with tab_batch:
    if filtered_df.empty:
        st.warning("No customers match the selected filters.")
    else:
        scored_df = predictor.predict_batch(filtered_df)

        col1, col2, col3 = st.columns(3)
        tier_counts = scored_df['RiskTier'].value_counts()
        col1.metric("High Risk", int(tier_counts.get('High', 0)))
        col2.metric("Medium Risk", int(tier_counts.get('Medium', 0)))
        col3.metric("Low Risk", int(tier_counts.get('Low', 0)))

        st.subheader("Risk Tier Distribution")
        fig = px.histogram(
            scored_df, x='ChurnProbability', color='RiskTier',
            nbins=30, color_discrete_map={'Low': '#4C72B0', 'Medium': '#DDA452', 'High': '#DD5452'}
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Highest-Risk Customers")
        top_risk = scored_df.sort_values('ChurnProbability', ascending=False)[
            ['CustomerId', 'Geography', 'Age', 'Balance', 'NumOfProducts',
             'IsActiveMember', 'ChurnProbability', 'RiskTier']
        ]
        st.dataframe(top_risk.head(50), use_container_width=True)

        csv = top_risk.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download Full Risk-Scored List (CSV)",
            data=csv,
            file_name="churn_risk_scores.csv",
            mime="text/csv"
        )

# ---------------- TAB 2: WHAT-IF PREDICTOR ----------------
with tab_whatif:
    st.subheader("Manually enter a customer profile")

    col1, col2, col3 = st.columns(3)
    with col1:
        geography = st.selectbox("Geography", ["France", "Germany", "Spain"])
        gender = st.selectbox("Gender", ["Male", "Female"])
        age = st.slider("Age", 18, 92, 40)
    with col2:
        credit_score = st.slider("Credit Score", 350, 850, 650)
        tenure = st.slider("Tenure (years)", 0, 10, 5)
        balance = st.number_input("Balance", min_value=0.0, max_value=250000.0, value=75000.0)
    with col3:
        num_products = st.selectbox("Number of Products", [1, 2, 3, 4])
        has_cr_card = st.selectbox("Has Credit Card", ["Yes", "No"])
        is_active = st.selectbox("Active Member", ["Yes", "No"])
        salary = st.number_input("Estimated Salary", min_value=0.0, max_value=200000.0, value=100000.0)

    if st.button("Predict Churn Risk", type="primary"):
        age_group = '<30' if age < 30 else '30-45' if age <= 45 else '46-60' if age <= 60 else '60+'

        customer = {
            'Geography': geography,
            'Gender': gender,
            'Age': age,
            'AgeGroup': age_group,
            'CreditScore': credit_score,
            'Tenure': tenure,
            'Balance': balance,
            'NumOfProducts': num_products,
            'HasCrCard': 1 if has_cr_card == "Yes" else 0,
            'IsActiveMember': 1 if is_active == "Yes" else 0,
            'EstimatedSalary': salary
        }

        result = predictor.predict_single(customer)

        st.divider()
        col_a, col_b = st.columns(2)
        col_a.metric("Predicted Churn Probability", f"{result['probability']}%")
        col_b.metric("Risk Tier", result['risk_tier'])

        if result['risk_tier'] == 'High':
            st.error("High churn risk — recommend proactive retention outreach.")
        elif result['risk_tier'] == 'Medium':
            st.warning("Moderate churn risk — monitor engagement.")
        else:
            st.success("Low churn risk.")