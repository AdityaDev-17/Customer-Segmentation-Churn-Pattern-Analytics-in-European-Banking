"""
kpi_calculator.py
OOP-style KPI calculation class for the Churn Analytics dashboard.
Encapsulates all 5 KPI formulas from Phase 6 so every page can reuse
the same, single source of truth for KPI logic.
"""

import pandas as pd


class ChurnKPICalculator:
    """Computes the 5 core churn KPIs on a given (optionally filtered) dataframe."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def overall_churn_rate(self) -> float:
        """KPI 1: % of customers who exited."""
        if len(self.df) == 0:
            return 0.0
        return round(self.df['Exited'].mean() * 100, 2)

    def segment_churn_rate(self, segment_col: str) -> pd.Series:
        """KPI 2: Churn % broken down by a given segment column."""
        return (self.df.groupby(segment_col, observed=True)['Exited'].mean() * 100).round(2)

    def high_value_churn_ratio(self, balance_threshold: float) -> float:
        """KPI 3: % of all churners who are high-value (Balance above threshold)."""
        churned = self.df[self.df['Exited'] == 1]
        if len(churned) == 0:
            return 0.0
        high_value_churned = churned[churned['Balance'] > balance_threshold]
        return round((len(high_value_churned) / len(churned)) * 100, 2)

    def geographic_risk_index(self) -> pd.Series:
        """KPI 4: Segment churn rate relative to overall churn rate, by Geography."""
        overall = self.overall_churn_rate()
        if overall == 0:
            return pd.Series(dtype=float)
        geo_rate = self.segment_churn_rate('Geography')
        return (geo_rate / overall).round(2)

    def engagement_drop_indicator(self) -> float:
        """KPI 5: Ratio of inactive-member churn rate to active-member churn rate."""
        active_rate = self.segment_churn_rate('IsActiveMember')
        if 1 not in active_rate.index or active_rate.get(1, 0) == 0:
            return 0.0
        return round(active_rate.get(0, 0) / active_rate[1], 2)

    def revenue_at_risk(self, balance_threshold: float) -> float:
        """Sum of Balance for churned high-value customers (from Phase 5)."""
        churned = self.df[self.df['Exited'] == 1]
        high_value_churned = churned[churned['Balance'] > balance_threshold]
        return round(high_value_churned['Balance'].sum(), 2)