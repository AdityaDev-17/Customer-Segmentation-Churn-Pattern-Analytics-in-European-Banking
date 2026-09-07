"""
filters.py
Shared sidebar filter component for the Churn Analytics dashboard.
Uses st.session_state so filter selections persist as the user
navigates between pages (Streamlit re-runs each page script independently).
"""

import streamlit as st
import pandas as pd


class SidebarFilterManager:
    """Renders sidebar filter widgets and applies them to a dataframe."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def render_and_apply(self) -> pd.DataFrame:
        """Render filter widgets in the sidebar and return the filtered dataframe."""
        st.sidebar.header("Filters")

        geography = st.sidebar.multiselect(
            "Geography",
            options=sorted(self.df['Geography'].unique()),
            default=st.session_state.get('filter_geography', sorted(self.df['Geography'].unique())),
            key='filter_geography'
        )

        gender = st.sidebar.multiselect(
            "Gender",
            options=sorted(self.df['Gender'].unique()),
            default=st.session_state.get('filter_gender', sorted(self.df['Gender'].unique())),
            key='filter_gender'
        )

        age_group = st.sidebar.multiselect(
            "Age Group",
            options=['<30', '30-45', '46-60', '60+'],
            default=st.session_state.get('filter_age_group', ['<30', '30-45', '46-60', '60+']),
            key='filter_age_group'
        )

        tenure_group = st.sidebar.multiselect(
            "Tenure Group",
            options=['New', 'Mid-term', 'Long-term'],
            default=st.session_state.get('filter_tenure_group', ['New', 'Mid-term', 'Long-term']),
            key='filter_tenure_group'
        )

        balance_segment = st.sidebar.multiselect(
            "Balance Segment",
            options=['Zero-balance', 'Low-balance', 'High-balance'],
            default=st.session_state.get('filter_balance_segment', ['Zero-balance', 'Low-balance', 'High-balance']),
            key='filter_balance_segment'
        )

        active_status = st.sidebar.multiselect(
            "Active Member Status",
            options=[0, 1],
            format_func=lambda x: "Active" if x == 1 else "Inactive",
            default=st.session_state.get('filter_active_status', [0, 1]),
            key='filter_active_status'
        )

        if st.sidebar.button("Reset Filters"):
            for key in ['filter_geography', 'filter_gender', 'filter_age_group',
                        'filter_tenure_group', 'filter_balance_segment', 'filter_active_status']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        filtered = self.df[
            (self.df['Geography'].isin(geography)) &
            (self.df['Gender'].isin(gender)) &
            (self.df['AgeGroup'].isin(age_group)) &
            (self.df['TenureGroup'].isin(tenure_group)) &
            (self.df['BalanceSegment'].isin(balance_segment)) &
            (self.df['IsActiveMember'].isin(active_status))
        ]

        st.sidebar.markdown(f"**Showing {len(filtered):,} of {len(self.df):,} customers**")

        return filtered