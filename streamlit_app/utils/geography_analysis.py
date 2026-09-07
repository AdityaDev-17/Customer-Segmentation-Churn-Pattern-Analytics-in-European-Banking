"""
geography_analysis.py
Geography Analysis tab — country-wise churn rates and interaction
effects with AgeGroup and Gender (Phase 4 findings, dashboard-ified).
"""

import streamlit as st
import plotly.express as px
from utils.kpi_calculator import ChurnKPICalculator


class GeographyAnalysisTab:
    """Renders the Geography Analysis tab content for a given (filtered) dataframe."""

    def __init__(self, df):
        self.df = df

    def render(self):
        st.markdown("<h2 style='text-align: center;'>Geography-Wise Churn Analysis</h2>", unsafe_allow_html=True)

        if self.df.empty:
            st.warning("No customers match the selected filters.")
            return

        kpi = ChurnKPICalculator(self.df)
        geo_churn = kpi.segment_churn_rate('Geography')

        col1, col2, col3 = st.columns(3)
        for col, country in zip([col1, col2, col3], ['France', 'Germany', 'Spain']):
            if country in geo_churn.index:
                col.metric(f"{country} Churn Rate", f"{geo_churn[country]}%")
            else:
                col.metric(f"{country} Churn Rate", "N/A")

        st.divider()

        st.subheader("Churn Rate by Geography")
        fig_bar = px.bar(
            x=geo_churn.index, y=geo_churn.values,
            labels={'x': 'Geography', 'y': 'Churn Rate (%)'},
            color=geo_churn.values, color_continuous_scale='OrRd', text=geo_churn.values
        )
        fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Geography × Age Group")
            pivot_age = self.df.pivot_table(
                values='Exited', index='AgeGroup', columns='Geography',
                aggfunc='mean', observed=True
            ) * 100
            fig_heat_age = px.imshow(
                pivot_age, text_auto='.1f', color_continuous_scale='OrRd',
                labels=dict(color="Churn Rate (%)")
            )
            st.plotly_chart(fig_heat_age, use_container_width=True)

        with col_right:
            st.subheader("Geography × Gender")
            pivot_gender = self.df.pivot_table(
                values='Exited', index='Gender', columns='Geography',
                aggfunc='mean', observed=True
            ) * 100
            fig_heat_gender = px.imshow(
                pivot_gender, text_auto='.1f', color_continuous_scale='OrRd',
                labels=dict(color="Churn Rate (%)")
            )
            st.plotly_chart(fig_heat_gender, use_container_width=True)

        st.divider()
        st.subheader("Segment Sizes by Geography")
        size_by_geo = self.df['Geography'].value_counts()
        fig_size = px.bar(
            x=size_by_geo.index, y=size_by_geo.values,
            labels={'x': 'Geography', 'y': 'Customer Count'}
        )
        st.plotly_chart(fig_size, use_container_width=True)