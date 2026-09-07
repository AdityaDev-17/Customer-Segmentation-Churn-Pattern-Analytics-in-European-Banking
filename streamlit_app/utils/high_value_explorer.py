"""
high_value_explorer.py
High-Value Customer Explorer tab — revenue-at-risk quantification
and financial profile comparison (Phase 5 findings, dashboard-ified).
"""

import streamlit as st
import plotly.express as px


class HighValueExplorerTab:
    """Renders the High-Value Customer Explorer tab for a given (filtered) dataframe."""

    def __init__(self, df, balance_threshold):
        self.df = df.copy()
        self.balance_threshold = balance_threshold
        if not self.df.empty:
            self.df['HighValue'] = self.df['Balance'] > balance_threshold

    def render(self):
        st.markdown("<h2 style='text-align: center;'>High-Value Customer Churn Explorer</h2>", unsafe_allow_html=True)
        st.caption(f"High-value threshold: Balance > ${self.balance_threshold:,.2f} (75th percentile, full dataset)")

        if self.df.empty:
            st.warning("No customers match the selected filters.")
            return

        high_value_df = self.df[self.df['HighValue']]
        churned_hv = high_value_df[high_value_df['Exited'] == 1]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("High-Value Customers", f"{len(high_value_df):,}")
        col2.metric("High-Value Churned", f"{len(churned_hv):,}")
        hv_churn_rate = (len(churned_hv) / len(high_value_df) * 100) if len(high_value_df) > 0 else 0
        col3.metric("High-Value Churn Rate", f"{hv_churn_rate:.1f}%")
        col4.metric("Revenue at Risk", f"${churned_hv['Balance'].sum():,.0f}")

        st.divider()

        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Churn Rate: High-Value vs Others")
            hv_comparison = self.df.groupby('HighValue')['Exited'].mean() * 100
            hv_comparison.index = hv_comparison.index.map({True: 'High-Value', False: 'Others'})
            fig_bar = px.bar(
                x=hv_comparison.index, y=hv_comparison.values,
                labels={'x': '', 'y': 'Churn Rate (%)'},
                color=hv_comparison.values, color_continuous_scale='OrRd', text=hv_comparison.values
            )
            fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_right:
            st.subheader("Balance vs Estimated Salary")
            plot_df = self.df.rename(columns={'Exited': 'Status'})
            plot_df['Status'] = plot_df['Status'].map({0: 'Retained', 1: 'Churned'})
            fig_scatter = px.scatter(
                plot_df, x='EstimatedSalary', y='Balance', color='Status',
                opacity=0.4, color_discrete_map={'Retained': '#4C72B0', 'Churned': '#DD8452'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        st.divider()
        st.subheader("Profile Comparison: Retained vs Churned")
        persona = self.df.groupby('Exited')[
            ['CreditScore', 'Age', 'Tenure', 'Balance', 'NumOfProducts', 'EstimatedSalary']
        ].mean().round(1)
        persona.index = persona.index.map({0: 'Retained', 1: 'Churned'})
        st.dataframe(persona, use_container_width=True)