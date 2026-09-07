"""
data_loader.py
Shared data and model loading utilities for the Churn Analytics dashboard.
Uses Streamlit's caching so the CSV/model are only loaded once per session,
not re-loaded on every widget interaction.
"""

import pandas as pd
import joblib
import streamlit as st
from pathlib import Path

# Paths relative to the streamlit_app/ root
DATA_PATH = Path("data/df_clean_for_dashboard.csv")
MODEL_PATH = Path("models/random_forest_churn_model.pkl")
SCALER_PATH = Path("models/scaler.pkl")
FEATURE_COLS_PATH = Path("models/feature_columns.pkl")


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load the cleaned, segmented dataset used across all dashboard pages."""
    df = pd.read_csv(DATA_PATH)
    return df


@st.cache_resource
def load_model():
    """Load the trained Random Forest model (used only on the Risk Score page)."""
    return joblib.load(MODEL_PATH)


@st.cache_resource
def load_scaler():
    """Load the fitted StandardScaler (kept for consistency, not used by RF directly)."""
    return joblib.load(SCALER_PATH)


@st.cache_resource
def load_feature_columns() -> list:
    """Load the exact feature column order the model was trained on."""
    return joblib.load(FEATURE_COLS_PATH)