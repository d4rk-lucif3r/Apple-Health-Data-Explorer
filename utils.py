import pandas as pd
import base64
from datetime import datetime, timedelta

def get_csv_download_link(df, filename):
    """Generate a download link for a dataframe"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="download-btn">📥 Download {filename}</a>'
    return href

def format_duration(seconds):
    """Format duration in seconds to human-readable string"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"

def get_date_range_mask(df, use_custom_range, start_date=None, end_date=None, selected_range=None, quick_ranges=None):
    """Generate date range mask for filtering dataframes"""
    if use_custom_range:
        return (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
    else:
        max_date = df["date"].max()
        if quick_ranges[selected_range]:
            min_date = max_date - quick_ranges[selected_range]
        else:
            min_date = df["date"].min()
        return (df["date"].dt.date >= min_date.date()) & (df["date"].dt.date <= max_date.date())

def make_timezone_naive(df):
    """Convert timezone-aware datetime columns to naive"""
    if not df.empty and df["date"].dt.tz is not None:
        df["date"] = df["date"].dt.tz_localize(None)
    if "endDate" in df.columns and not df.empty and df["endDate"].dt.tz is not None:
        df["endDate"] = df["endDate"].dt.tz_localize(None)
    return df

def calculate_trend(values):
    """Calculate trend direction and percentage change"""
    if len(values) < 2:
        return "No trend data available", 0
    
    first_half = values[:len(values)//2].mean()
    second_half = values[len(values)//2:].mean()
    
    if first_half == 0:
        return "Stable", 0
        
    change = ((second_half - first_half) / first_half) * 100
    
    if change > 5:
        return "Increasing", change
    elif change < -5:
        return "Decreasing", change
    else:
        return "Stable", change

def get_day_part(hour):
    """Get part of day based on hour"""
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 22:
        return "Evening"
    else:
        return "Night"