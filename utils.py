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
    # Dates are already timezone-naive from preprocessing
    dates = pd.to_datetime(df["date"])
    
    if use_custom_range:
        mask = (dates.dt.date >= start_date) & (dates.dt.date <= end_date)
    else:
        max_date = dates.max()
        if quick_ranges[selected_range]:
            min_date = max_date - quick_ranges[selected_range]
        else:
            min_date = dates.min()
        mask = (dates.dt.date >= min_date.date()) & (dates.dt.date <= max_date.date())
    
    # Add debug output
    print(f"Date range: {dates.min()} to {dates.max()}")
    print(f"Filter range: {min_date if not use_custom_range else start_date} to {max_date if not use_custom_range else end_date}")
    print(f"Number of records: {len(df)}")
    print(f"Number of records after filter: {mask.sum()}")
    
    return mask




def calculate_trend(values):
    """Calculate trend direction and percentage change"""
    if len(values) < 2:
        return "No trend data available", 0

    first_half = values[: len(values) // 2].mean()
    second_half = values[len(values) // 2 :].mean()

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
