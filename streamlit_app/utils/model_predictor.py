"""
model_predictor.py
Wraps the trained Random Forest model with the exact same feature
engineering used at training time (Phase 7), so batch scoring and
single-customer "what-if" predictions can never drift out of sync
with how the model was actually trained.
"""

import pandas as pd
from utils.data_loader import load_model, load_feature_columns


class ChurnPredictor:
    """Applies training-time feature engineering and scores customers with the RF model."""

    def __init__(self):
        self.model = load_model()
        self.feature_columns = load_feature_columns()

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Replicates Cell 23's feature engineering exactly:
        - Binary-encode Gender
        - One-hot encode Geography (France dropped as baseline)
        - HighProductRisk flag (NumOfProducts >= 3)
        - GermanyMidAge flag (Geography == Germany AND AgeGroup == 46-60)
        """
        df = df.copy()

        df['Gender'] = df['Gender'].map({'Male': 0, 'Female': 1})

        df['Geography_Germany'] = (df['Geography'] == 'Germany').astype(int)
        df['Geography_Spain'] = (df['Geography'] == 'Spain').astype(int)

        df['HighProductRisk'] = (df['NumOfProducts'] >= 3).astype(int)

        if 'AgeGroup' in df.columns:
            age_46_60 = df['AgeGroup'] == '46-60'
        else:
            age_46_60 = (df['Age'] >= 46) & (df['Age'] <= 60)
        df['GermanyMidAge'] = ((df['Geography'] == 'Germany') & age_46_60).astype(int)

        # Reindex to the exact column order the model was trained on;
        # fill any missing engineered column with 0 rather than erroring
        df_features = df.reindex(columns=self.feature_columns, fill_value=0)

        return df_features

    def predict_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """Score a dataframe of customers. Returns the original df with two new columns added."""
        X = self._engineer_features(df)
        probabilities = self.model.predict_proba(X)[:, 1]

        result = df.copy()
        result['ChurnProbability'] = (probabilities * 100).round(2)
        result['RiskTier'] = pd.cut(
            probabilities,
            bins=[-0.01, 0.30, 0.60, 1.01],
            labels=['Low', 'Medium', 'High']
        )
        return result

    def predict_single(self, customer_dict: dict) -> dict:
        """Score one manually-entered customer. Returns probability and risk tier."""
        df = pd.DataFrame([customer_dict])
        result = self.predict_batch(df)
        return {
            'probability': result['ChurnProbability'].iloc[0],
            'risk_tier': result['RiskTier'].iloc[0]
        }