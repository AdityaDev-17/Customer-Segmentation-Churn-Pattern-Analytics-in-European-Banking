"""
app.py
Single-page Customer Churn Analytics dashboard.
Tabs: App (KPI overview), Geography, Age & Tenure, High-Value Explorer, Predictor.
"""

import streamlit as st
import plotly.express as px

from utils.data_loader import load_data
from utils.kpi_calculator import ChurnKPICalculator
from utils.filters import SidebarFilterManager
from utils.model_predictor import ChurnPredictor
from utils.geography_analysis import GeographyAnalysisTab
from utils.age_tenure_analysis import AgeTenureAnalysisTab
from utils.high_value_explorer import HighValueExplorerTab

st.set_page_config(
    page_title="Customer Segmentation & Churn Pattern Analytics",
    layout="wide"
)

# ---------------- Centered main title ----------------
st.markdown(
    "<h1 style='text-align: center;'>Customer-Segmentaion-Churn-Patern-Analystics-in-European-Banking</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align: center; color: gray;'>European Banking — Churn Analytics & Risk Prediction</p>",
    unsafe_allow_html=True
)
st.divider()

# ---------------- Shared data + sidebar filters ----------------
df = load_data()
filter_manager = SidebarFilterManager(df)
filtered_df = filter_manager.render_and_apply()
balance_p75 = df['Balance'].quantile(0.75)  # threshold from FULL dataset, not filtered

# ---------------- Top-level tabs ----------------
tab_app, tab_geo, tab_age_tenure, tab_highvalue, tab_predictor = st.tabs(
    ["App", "Geography", "Age & Tenure", "High-Value Explorer", "Predictor"]
)

# =====================================================================
# TAB: APP  (Overview KPI Dashboard)
# =====================================================================
with tab_app:
    st.markdown("<h2 style='text-align: center;'>Overview Dashboard</h2>", unsafe_allow_html=True)

    if filtered_df.empty:
        st.warning("No customers match the selected filters. Adjust filters in the sidebar.")
    else:
        kpi = ChurnKPICalculator(filtered_df)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Overall Churn Rate", f"{kpi.overall_churn_rate()}%")
        col2.metric("High-Value Churn Ratio", f"{kpi.high_value_churn_ratio(balance_p75)}%")
        col3.metric("Engagement Drop Indicator", f"{kpi.engagement_drop_indicator()}x")
        col4.metric("Revenue at Risk", f"${kpi.revenue_at_risk(balance_p75):,.0f}")

        st.divider()

        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Churn Distribution")
            churn_counts = filtered_df['Exited'].value_counts().rename({0: 'Retained', 1: 'Churned'})
            fig_pie = px.pie(
                values=churn_counts.values,
                names=churn_counts.index,
                color=churn_counts.index,
                color_discrete_map={'Retained': '#4C72B0', 'Churned': '#DD8452'}
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_right:
            st.subheader("Geographic Risk Index")
            geo_risk = kpi.geographic_risk_index()
            fig_bar = px.bar(
                x=geo_risk.index, y=geo_risk.values,
                labels={'x': 'Geography', 'y': 'Risk Index (vs overall)'},
                color=geo_risk.values, color_continuous_scale='OrRd'
            )
            fig_bar.add_hline(y=1.0, line_dash="dash", line_color="gray", annotation_text="Bank average")
            st.plotly_chart(fig_bar, use_container_width=True)

# =====================================================================
# TAB: GEOGRAPHY ANALYSIS
# =====================================================================
with tab_geo:
    GeographyAnalysisTab(filtered_df).render()

# =====================================================================
# TAB: AGE & TENURE ANALYSIS
# =====================================================================
with tab_age_tenure:
    AgeTenureAnalysisTab(filtered_df).render()

# =====================================================================
# TAB: HIGH-VALUE EXPLORER
# =====================================================================
with tab_highvalue:
    HighValueExplorerTab(filtered_df, balance_p75).render()

# =====================================================================
# TAB: PREDICTOR  (Batch Risk Scoring + What-If)
# =====================================================================
with tab_predictor:
    st.markdown("<h2 style='text-align: center;'>Churn Risk Score Predictor</h2>", unsafe_allow_html=True)
    st.caption("Random Forest model — bonus predictive module. Risk scores are relative rankings, not calibrated probabilities.")

    predictor = ChurnPredictor()
    sub_batch, sub_whatif = st.tabs(["Batch Risk Scoring", "What-If Predictor"])

    with sub_batch:
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

    with sub_whatif:
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
            col_a.metric("Predicted Risk Score", f"{result['probability']}%")
            col_b.metric("Risk Tier", result['risk_tier'])

            if result['risk_tier'] == 'High':
                st.error("High churn risk — recommend proactive retention outreach.")
            elif result['risk_tier'] == 'Medium':
                st.warning("Moderate churn risk — monitor engagement.")
            else:
                st.success("Low churn risk.")