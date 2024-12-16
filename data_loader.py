import pandas as pd
import streamlit as st
import json

@st.cache_data
def load_metadata():
    """Load metadata about processed data"""
    try:
        with open('processed_data/metadata.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Processed data not found. Please run preprocess_health_data.py first.")
        st.stop()

@st.cache_data
def load_data(data_type):
    """Load preprocessed data from CSV"""
    try:
        df = pd.read_csv(f'processed_data/{data_type}.csv')
        # Convert date columns to datetime using ISO8601 format
        date_columns = ['date', 'endDate']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format='ISO8601')
        return df
    except FileNotFoundError:
        return pd.DataFrame()