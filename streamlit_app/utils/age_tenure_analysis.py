"""
age_tenure_analysis.py
Age & Tenure Analysis tab — segment churn comparisons and the
AgeGroup 46-60 spike interaction (Phase 3 & 4 findings, dashboard-ified).
"""

import streamlit as st
import plotly.express as px
from utils.kpi_calculator import ChurnKPICalculator


class AgeTenureAnalysisTab:
    """Renders the Age & Tenure Analysis tab content for a given (filtered) dataframe."""

    def __init__(self, df):
        self.df = df

    def render(self):
        st.markdown("<h2 style='text-align: center;'>Age & Tenure Churn Analysis</h2>", unsafe_allow_html=True)

        if self.df.empty:
            st.warning("No customers match the selected filters.")
            return

        kpi = ChurnKPICalculator(self.df)

        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Churn Rate by Age Group")
            age_order = ['<30', '30-45', '46-60', '60+']
            age_churn = kpi.segment_churn_rate('AgeGroup').reindex(age_order)
            fig_age = px.bar(
                x=age_churn.index, y=age_churn.values,
                labels={'x': 'Age Group', 'y': 'Churn Rate (%)'},
                color=age_churn.values, color_continuous_scale='OrRd', text=age_churn.values
            )
            fig_age.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig_age, use_container_width=True)

        with col_right:
            st.subheader("Churn Rate by Tenure Group")
            tenure_order = ['New', 'Mid-term', 'Long-term']
            tenure_churn = kpi.segment_churn_rate('TenureGroup').reindex(tenure_order)
            fig_tenure = px.bar(
                x=tenure_churn.index, y=tenure_churn.values,
                labels={'x': 'Tenure Group', 'y': 'Churn Rate (%)'},
                color=tenure_churn.values, color_continuous_scale='OrRd', text=tenure_churn.values
            )
            fig_tenure.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig_tenure, use_container_width=True)

        st.divider()

        st.subheader("Age Group × Tenure Group Interaction")
        pivot_age_tenure = self.df.pivot_table(
            values='Exited', index='AgeGroup', columns='TenureGroup',
            aggfunc='mean', observed=True
        ).reindex(index=['<30', '30-45', '46-60', '60+'],
                  columns=['New', 'Mid-term', 'Long-term']) * 100
        fig_heat = px.imshow(
            pivot_age_tenure, text_auto='.1f', color_continuous_scale='OrRd',
            labels=dict(color="Churn Rate (%)")
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        st.divider()
        st.subheader("Age Distribution: Retained vs Churned")
        fig_hist = px.histogram(
            self.df, x='Age', color='Exited', barmode='overlay', nbins=30,
            color_discrete_map={0: '#4C72B0', 1: '#DD8452'},
            labels={'Exited': 'Status'}
        )
        fig_hist.for_each_trace(lambda t: t.update(name={'0': 'Retained', '1': 'Churned'}.get(t.name, t.name)))
        st.plotly_chart(fig_hist, use_container_width=True)