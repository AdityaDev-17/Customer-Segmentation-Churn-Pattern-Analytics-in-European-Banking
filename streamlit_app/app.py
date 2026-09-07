"""
app.py
Home page of the Customer Churn Analytics dashboard.
Entry point — Streamlit uses this as the main page, with the pages/
folder auto-populating the sidebar navigation.
"""

import streamlit as st
import plotly.express as px

from utils.data_loader import load_data
from utils.kpi_calculator import ChurnKPICalculator
from utils.filters import SidebarFilterManager

st.set_page_config(page_title="Churn Analytics — Overview", layout="wide")

st.title("Customer Segmentation & Churn Pattern Analytics")
st.caption("European Banking — Overview Dashboard")

# Load data and apply shared sidebar filters
df = load_data()
filter_manager = SidebarFilterManager(df)
filtered_df = filter_manager.render_and_apply()

if filtered_df.empty:
    st.warning("No customers match the selected filters. Adjust filters in the sidebar.")
    st.stop()

# Compute KPIs on the filtered data
kpi = ChurnKPICalculator(filtered_df)
balance_p75 = df['Balance'].quantile(0.75)  # threshold computed on FULL dataset, not filtered

col1, col2, col3, col4 = st.columns(4)
col1.metric("Overall Churn Rate", f"{kpi.overall_churn_rate()}%")
col2.metric("High-Value Churn Ratio", f"{kpi.high_value_churn_ratio(balance_p75)}%")
col3.metric("Engagement Drop Indicator", f"{kpi.engagement_drop_indicator()}x")
col4.metric("Revenue at Risk", f"${kpi.revenue_at_risk(balance_p75):,.0f}")

st.divider()

# Churn distribution pie chart
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

st.divider()
st.info("Use the sidebar to navigate to Geography Analysis, Age & Tenure Analysis, High-Value Explorer, and the Risk Score Predictor pages.")