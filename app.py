import os
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from data_loader import load_data, load_metadata
from insights import (analyze_activity_patterns, analyze_health_correlations,
                      analyze_heart_rate_patterns, analyze_sleep_quality,
                      analyze_workout_effectiveness)
from utils import (format_duration, get_csv_download_link, get_date_range_mask,
                   make_timezone_naive)

# Set page config
st.set_page_config(
    page_title="Apple Health Data Explorer",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
    }
    .download-btn {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

def display_heart_metrics(heart_rate_df, use_custom_range, start_date=None, end_date=None, selected_range=None, quick_ranges=None, selected_sources=None):
    """Display heart rate metrics and visualizations"""
    if not heart_rate_df.empty:
        # Apply date range filter
        mask = get_date_range_mask(heart_rate_df, use_custom_range, start_date, end_date, selected_range, quick_ranges)
        
        # Apply source filter
        if selected_sources:
            mask &= heart_rate_df['source'].isin(selected_sources)
        filtered_hr_df = heart_rate_df[mask]

        st.markdown(get_csv_download_link(filtered_hr_df, "heart_rate_data.csv"), unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            avg_hr = filtered_hr_df["value"].mean()
            st.metric("Average Heart Rate", f"{avg_hr:.0f} bpm")
        with col2:
            max_hr = filtered_hr_df["value"].max()
            st.metric("Max Heart Rate", f"{max_hr:.0f} bpm")
        with col3:
            min_hr = filtered_hr_df["value"].min()
            st.metric("Min Heart Rate", f"{min_hr:.0f} bpm")

        fig = px.scatter(
            filtered_hr_df,
            x="date",
            y="value",
            title="Heart Rate Over Time",
            labels={"value": "Heart Rate (bpm)", "date": "Date"},
        )
        fig.update_traces(marker=dict(size=3))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No heart rate data available for the selected period.")

def display_activity_metrics(steps_df, active_energy_df, use_custom_range, start_date=None, end_date=None, selected_range=None, quick_ranges=None, selected_sources=None):
    """Display activity metrics and visualizations"""
    if not steps_df.empty or not active_energy_df.empty:
        # Create copies to avoid SettingWithCopyWarning
        steps_df = steps_df.copy()
        active_energy_df = active_energy_df.copy()
        
        # Apply filters to steps data
        steps_mask = get_date_range_mask(steps_df, use_custom_range, start_date, end_date, selected_range, quick_ranges)
        if selected_sources:
            steps_mask &= steps_df['source'].isin(selected_sources)
        filtered_steps_df = steps_df[steps_mask].copy()

        # Apply filters to active energy data
        energy_mask = get_date_range_mask(active_energy_df, use_custom_range, start_date, end_date, selected_range, quick_ranges)
        if selected_sources:
            energy_mask &= active_energy_df['source'].isin(selected_sources)
        filtered_energy_df = active_energy_df[energy_mask].copy()

        # Download links
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(get_csv_download_link(filtered_steps_df, "steps_data.csv"), unsafe_allow_html=True)
        with col2:
            st.markdown(get_csv_download_link(filtered_energy_df, "active_energy_data.csv"), unsafe_allow_html=True)

        # Steps metrics
        st.subheader("📶 Steps Analysis")
        if not filtered_steps_df.empty:
            daily_steps = filtered_steps_df.groupby(filtered_steps_df["date"].dt.date)["value"].sum()

            col1, col2, col3 = st.columns(3)
            with col1:
                avg_steps = daily_steps.mean()
                st.metric("Average Daily Steps", f"{avg_steps:,.0f}")
            with col2:
                total_steps = daily_steps.sum()
                st.metric("Total Steps", f"{total_steps:,.0f}")
            with col3:
                days_over_10k = (daily_steps >= 10000).sum()
                st.metric("Days Over 10,000 Steps", days_over_10k)

            daily_steps_df = daily_steps.reset_index()
            fig = px.bar(
                daily_steps_df,
                x="date",
                y="value",
                title="Daily Steps",
                labels={"value": "Steps", "date": "Date"},
            )
            fig.add_hline(y=10000, line_dash="dash", line_color="green", annotation_text="10,000 steps goal")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No steps data available for the selected period.")

        # Active Energy metrics
        st.subheader("🔥 Active Energy Analysis")
        if not filtered_energy_df.empty:
            daily_energy = filtered_energy_df.groupby(filtered_energy_df["date"].dt.date)["value"].sum()

            col1, col2, col3 = st.columns(3)
            with col1:
                avg_energy = daily_energy.mean()
                st.metric("Average Daily Active Calories", f"{avg_energy:,.0f} kcal")
            with col2:
                total_energy = daily_energy.sum()
                st.metric("Total Active Calories", f"{total_energy:,.0f} kcal")
            with col3:
                days_over_500 = (daily_energy >= 500).sum()
                st.metric("Days Over 500 kcal", days_over_500)

            daily_energy_df = daily_energy.reset_index()
            fig = px.bar(
                daily_energy_df,
                x="date",
                y="value",
                title="Daily Active Energy",
                labels={"value": "Active Energy (kcal)", "date": "Date"},
            )
            fig.add_hline(y=500, line_dash="dash", line_color="green", annotation_text="500 kcal goal")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No active energy data available for the selected period.")
    else:
        st.warning("No activity data available for the selected period.")

def display_workout_metrics(workout_df, use_custom_range, start_date=None, end_date=None, selected_range=None, quick_ranges=None, selected_sources=None):
    """Display workout metrics and visualizations"""
    if not workout_df.empty:
        # Apply date range filter
        mask = get_date_range_mask(workout_df, use_custom_range, start_date, end_date, selected_range, quick_ranges)
        
        # Apply source filter
        if selected_sources:
            mask &= workout_df['source'].isin(selected_sources)
        filtered_workout_df = workout_df[mask]

        st.markdown(get_csv_download_link(filtered_workout_df, "workout_data.csv"), unsafe_allow_html=True)

        if not filtered_workout_df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                total_workouts = len(filtered_workout_df)
                st.metric("Total Workouts", total_workouts)
            with col2:
                total_duration = filtered_workout_df["duration"].sum()
                st.metric("Total Duration", format_duration(total_duration))
            with col3:
                total_calories = filtered_workout_df["energy"].sum()
                st.metric("Total Calories", f"{total_calories:,.0f} kcal")

            workout_counts = filtered_workout_df["type"].value_counts()
            fig = px.pie(
                values=workout_counts.values,
                names=workout_counts.index,
                title="Workout Type Distribution",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No workout data available for the selected period.")

def display_metric_over_time(df, metric_name, unit, use_custom_range, start_date=None, end_date=None, selected_range=None, quick_ranges=None, selected_sources=None):
    """Display a generic metric over time with basic statistics"""
    if not df.empty:
        # Apply date range filter
        mask = get_date_range_mask(df, use_custom_range, start_date, end_date, selected_range, quick_ranges)
        
        # Apply source filter
        if selected_sources:
            mask &= df['source'].isin(selected_sources)
        filtered_df = df[mask].copy()

        if not filtered_df.empty:
            # Basic statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_value = filtered_df["value"].mean()
                st.metric(f"Average {metric_name}", f"{avg_value:.1f} {unit}")
            with col2:
                max_value = filtered_df["value"].max()
                st.metric(f"Max {metric_name}", f"{max_value:.1f} {unit}")
            with col3:
                min_value = filtered_df["value"].min()
                st.metric(f"Min {metric_name}", f"{min_value:.1f} {unit}")

            # Time series plot
            fig = px.scatter(
                filtered_df,
                x="date",
                y="value",
                title=f"{metric_name} Over Time",
                labels={"value": f"{metric_name} ({unit})", "date": "Date"},
            )
            fig.update_traces(marker=dict(size=3))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"No {metric_name.lower()} data available for the selected period.")

def display_body_metrics(df, use_custom_range, start_date=None, end_date=None, selected_range=None, quick_ranges=None, selected_sources=None):
    """Display body metrics with trends and analysis"""
    if not df.empty:
        # Apply filters
        mask = get_date_range_mask(df, use_custom_range, start_date, end_date, selected_range, quick_ranges)
        if selected_sources:
            mask &= df['source'].isin(selected_sources)
        filtered_df = df[mask].copy()

        if not filtered_df.empty:
            # Group metrics by type
            metrics = filtered_df.groupby('metric_type')
            
            # Display each metric type
            for metric_type, data in metrics:
                metric_name = metric_type.replace('HKQuantityTypeIdentifier', '')
                st.subheader(f"📊 {metric_name}")
                
                # Basic statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    latest_value = data.sort_values('date').iloc[-1]['value']
                    st.metric("Latest Value", f"{latest_value:.1f} {data.iloc[0]['unit']}")
                with col2:
                    avg_value = data['value'].mean()
                    st.metric("Average", f"{avg_value:.1f} {data.iloc[0]['unit']}")
                with col3:
                    if len(data) > 1:
                        change = latest_value - data.sort_values('date').iloc[0]['value']
                        st.metric("Total Change", f"{change:+.1f} {data.iloc[0]['unit']}")
                
                # Time series plot
                fig = px.scatter(
                    data.sort_values('date'),
                    x="date",
                    y="value",
                    title=f"{metric_name} Over Time",
                    labels={"value": f"{metric_name} ({data.iloc[0]['unit']})", "date": "Date"},
                )
                fig.update_traces(marker=dict(size=3))
                # Add trendline
                if len(data) > 1:
                    fig.add_traces(px.scatter(data.sort_values('date'), x="date", y="value", trendline="lowess").data[1])
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No body metrics data available for the selected period.")

def display_dietary_metrics(df, use_custom_range, start_date=None, end_date=None, selected_range=None, quick_ranges=None, selected_sources=None):
    """Display dietary metrics with nutritional analysis"""
    if not df.empty:
        # Apply filters
        mask = get_date_range_mask(df, use_custom_range, start_date, end_date, selected_range, quick_ranges)
        if selected_sources:
            mask &= df['source'].isin(selected_sources)
        filtered_df = df[mask].copy()

        if not filtered_df.empty:
            # Group metrics by type
            metrics = filtered_df.groupby('metric_type')
            
            # Create tabs for different nutrient categories
            macro_metrics = []
            micro_metrics = []
            other_metrics = []
            
            for metric_type, data in metrics:
                metric_name = metric_type.replace('HKQuantityTypeIdentifierDietary', '')
                if metric_name in ['Protein', 'Carbohydrates', 'FatTotal']:
                    macro_metrics.append((metric_name, data))
                elif metric_name in ['VitaminC', 'Iron', 'Calcium', 'Potassium']:
                    micro_metrics.append((metric_name, data))
                else:
                    other_metrics.append((metric_name, data))
            
            # Display macronutrients
            if macro_metrics:
                st.subheader("💪 Macronutrients")
                cols = st.columns(len(macro_metrics))
                for i, (name, data) in enumerate(macro_metrics):
                    with cols[i]:
                        avg_value = data['value'].mean()
                        st.metric(f"Average Daily {name}", f"{avg_value:.1f} {data.iloc[0]['unit']}")
            
            # Display micronutrients
            if micro_metrics:
                st.subheader("🥗 Micronutrients")
                cols = st.columns(len(micro_metrics))
                for i, (name, data) in enumerate(micro_metrics):
                    with cols[i]:
                        avg_value = data['value'].mean()
                        st.metric(f"Average Daily {name}", f"{avg_value:.1f} {data.iloc[0]['unit']}")
            
            # Display other nutrients
            if other_metrics:
                st.subheader("📊 Other Nutrients")
                cols = st.columns(min(3, len(other_metrics)))
                for i, (name, data) in enumerate(other_metrics):
                    with cols[i % 3]:
                        avg_value = data['value'].mean()
                        st.metric(f"Average Daily {name}", f"{avg_value:.1f} {data.iloc[0]['unit']}")
        else:
            st.warning("No dietary data available for the selected period.")

def display_environmental_metrics(df, use_custom_range, start_date=None, end_date=None, selected_range=None, quick_ranges=None, selected_sources=None):
    """Display environmental metrics and exposure analysis"""
    if not df.empty:
        # Apply filters
        mask = get_date_range_mask(df, use_custom_range, start_date, end_date, selected_range, quick_ranges)
        if selected_sources:
            mask &= df['source'].isin(selected_sources)
        filtered_df = df[mask].copy()

        if not filtered_df.empty:
            # Group metrics by type
            metrics = filtered_df.groupby('metric_type')
            
            for metric_type, data in metrics:
                metric_name = metric_type.replace('HKQuantityTypeIdentifier', '')
                
                if 'AudioExposure' in metric_type:
                    st.subheader("🔊 Audio Exposure")
                    
                    # Calculate exposure statistics
                    high_exposure = data[data['value'] > 85]['value'].count()  # Above 85 dB
                    total_readings = len(data)
                    exposure_percent = (high_exposure / total_readings * 100) if total_readings > 0 else 0
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        avg_exposure = data['value'].mean()
                        st.metric("Average Exposure", f"{avg_exposure:.1f} dB")
                    with col2:
                        max_exposure = data['value'].max()
                        st.metric("Max Exposure", f"{max_exposure:.1f} dB")
                    with col3:
                        st.metric("High Exposure Time", f"{exposure_percent:.1f}%")
                    
                    # Time series plot with safety threshold
                    fig = px.scatter(
                        data.sort_values('date'),
                        x="date",
                        y="value",
                        title="Audio Exposure Over Time",
                        labels={"value": "Audio Level (dB)", "date": "Date"},
                    )
                    fig.add_hline(y=85, line_dash="dash", line_color="red", 
                                annotation_text="Safety Threshold (85 dB)")
                    st.plotly_chart(fig, use_container_width=True)
                
                elif 'TimeInDaylight' in metric_type:
                    st.subheader("☀️ Time in Daylight")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        avg_time = data['value'].mean()
                        st.metric("Average Daily Time", f"{avg_time:.1f} minutes")
                    with col2:
                        max_time = data['value'].max()
                        st.metric("Max Daily Time", f"{max_time:.1f} minutes")
                    with col3:
                        good_days = (data['value'] >= 30).sum()  # Days with 30+ minutes
                        st.metric("Days with 30+ min", good_days)
                    
                    # Time series plot
                    fig = px.bar(
                        data.sort_values('date'),
                        x="date",
                        y="value",
                        title="Daily Time in Daylight",
                        labels={"value": "Time (minutes)", "date": "Date"},
                    )
                    fig.add_hline(y=30, line_dash="dash", line_color="green", 
                                annotation_text="Recommended minimum (30 min)")
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No environmental data available for the selected period.")

def display_sleep_metrics(sleep_df, use_custom_range, start_date=None, end_date=None, selected_range=None, quick_ranges=None, selected_sources=None):
    """Display sleep metrics and visualizations"""
    if not sleep_df.empty:
        # Apply date range filter
        mask = get_date_range_mask(sleep_df, use_custom_range, start_date, end_date, selected_range, quick_ranges)
        
        # Apply source filter
        if selected_sources:
            mask &= sleep_df['source'].isin(selected_sources)
        # Create a copy to avoid SettingWithCopyWarning
        filtered_sleep_df = sleep_df[mask].copy()

        st.markdown(get_csv_download_link(filtered_sleep_df, "sleep_data.csv"), unsafe_allow_html=True)

        if not filtered_sleep_df.empty:
            # Use loc to set values
            filtered_sleep_df.loc[:, "duration"] = (pd.to_datetime(filtered_sleep_df["endDate"]) - pd.to_datetime(filtered_sleep_df["date"])).dt.total_seconds()
            daily_sleep = filtered_sleep_df.groupby(pd.to_datetime(filtered_sleep_df["date"]).dt.date)["duration"].sum()

            col1, col2, col3 = st.columns(3)
            with col1:
                avg_sleep = daily_sleep.mean() / 3600
                st.metric("Average Sleep Duration", f"{avg_sleep:.1f} hours")
            with col2:
                total_sleep_days = len(daily_sleep)
                st.metric("Days with Sleep Data", total_sleep_days)
            with col3:
                days_over_8h = (daily_sleep / 3600 >= 8).sum()
                st.metric("Days with 8+ Hours", days_over_8h)

            daily_sleep_df = daily_sleep.reset_index()
            daily_sleep_df["duration"] = daily_sleep_df["duration"] / 3600
            fig = px.bar(
                daily_sleep_df,
                x="date",
                y="duration",
                title="Daily Sleep Duration",
                labels={"duration": "Sleep Duration (hours)", "date": "Date"},
            )
            fig.add_hline(y=8, line_dash="dash", line_color="green", annotation_text="Recommended 8 hours")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No sleep data available for the selected period.")

def load_all_data():
    """Load all datasets into session state if not already loaded"""
    if 'data_loaded' not in st.session_state:
        # Load and make timezone-naive immediately
        # Heart & Fitness
        st.session_state.heart_rate_df = make_timezone_naive(load_data("heart_rate"))
        st.session_state.resting_heart_rate_df = make_timezone_naive(load_data("resting_heart_rate"))
        st.session_state.heart_rate_variability_df = make_timezone_naive(load_data("heart_rate_variability"))
        st.session_state.vo2_max_df = make_timezone_naive(load_data("vo2_max"))
        st.session_state.walking_heart_rate_df = make_timezone_naive(load_data("walking_heart_rate"))
        
        # Activity
        st.session_state.steps_df = make_timezone_naive(load_data("steps"))
        st.session_state.active_energy_df = make_timezone_naive(load_data("active_energy"))
        st.session_state.basal_energy_df = make_timezone_naive(load_data("basal_energy"))
        st.session_state.distance_walking_running_df = make_timezone_naive(load_data("distance_walking_running"))
        st.session_state.distance_cycling_df = make_timezone_naive(load_data("distance_cycling"))
        st.session_state.flights_climbed_df = make_timezone_naive(load_data("flights_climbed"))
        st.session_state.exercise_time_df = make_timezone_naive(load_data("exercise_time"))
        st.session_state.stand_time_df = make_timezone_naive(load_data("stand_time"))
        st.session_state.walking_metrics_df = make_timezone_naive(load_data("walking_metrics"))
        
        # Others
        st.session_state.workouts_df = make_timezone_naive(load_data("workouts"))
        st.session_state.sleep_df = make_timezone_naive(load_data("sleep"))
        
        # Body Metrics
        st.session_state.body_metrics_df = make_timezone_naive(load_data("body_metrics"))
        
        # Vitals
        st.session_state.oxygen_saturation_df = make_timezone_naive(load_data("oxygen_saturation"))
        st.session_state.respiratory_rate_df = make_timezone_naive(load_data("respiratory_rate"))
        
        # Nutrition
        st.session_state.water_df = make_timezone_naive(load_data("water"))
        st.session_state.caffeine_df = make_timezone_naive(load_data("caffeine"))
        st.session_state.dietary_metrics_df = make_timezone_naive(load_data("dietary_metrics"))
        
        # Environmental
        st.session_state.environmental_df = make_timezone_naive(load_data("environmental"))
        
        st.session_state.data_loaded = True

def main():
    st.title("🍎 Apple Health Data Explorer")

    if not os.path.exists("processed_data/metadata.json"):
        st.error("""
        Processed data not found! Please run the preprocessing script first:
        ```
        python preprocess_health_data.py
        ```
        """)
        st.stop()

    metadata = load_metadata()
    last_processed = datetime.fromisoformat(metadata["last_processed"])

    st.markdown(f"""
    This app allows you to explore your Apple Health data with interactive visualizations. 
    Data was last processed on: {last_processed.strftime('%Y-%m-%d %H:%M:%S')}
    """)

    # Load all data at startup
    with st.spinner("Loading health data..."):
        load_all_data()

    # Sidebar filters
    st.sidebar.header("📅 Filters")
    
    # Source filter
    available_sources = sorted(pd.concat([
        st.session_state.heart_rate_df['source'].dropna(),
        st.session_state.steps_df['source'].dropna(),
        st.session_state.active_energy_df['source'].dropna(),
        st.session_state.sleep_df['source'].dropna(),
        st.session_state.workouts_df['source'].dropna()
    ]).unique())
    
    selected_sources = st.sidebar.multiselect(
        "Data Sources",
        options=available_sources,
        default=available_sources,
        help="Filter data by source (e.g., Apple Watch, iPhone)"
    )
    
    # Date range filter
    range_type = st.sidebar.radio(
        "Date Range Type",
        ["Quick Select", "Custom Range"],
        help="Choose between preset ranges or custom dates"
    )

    if range_type == "Quick Select":
        quick_ranges = {
            "Last 7 Days": timedelta(days=7),
            "Last 30 Days": timedelta(days=30),
            "Last 90 Days": timedelta(days=90),
            "Last Year": timedelta(days=365),
            "All Time": None,
        }
        selected_range = st.sidebar.selectbox(
            "Select Quick Range",
            list(quick_ranges.keys()),
            help="Choose a preset time period to analyze your health data",
        )
        use_custom_range = False
        start_date = end_date = None
    else:
        quick_ranges = selected_range = None
        max_date = datetime.now().date()
        min_possible_date = max_date - timedelta(days=365*5)
        
        start_date = st.sidebar.date_input(
            "Start Date",
            value=max_date - timedelta(days=30),
            min_value=min_possible_date,
            max_value=max_date
        )
        end_date = st.sidebar.date_input(
            "End Date",
            value=max_date,
            min_value=start_date,
            max_value=max_date
        )
        use_custom_range = True

    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "❤️ Heart & Fitness",
        "🏃‍♂️ Activity",
        "🏋️‍♂️ Workouts",
        "😴 Sleep",
        "⚖️ Body Metrics",
        "🫁 Vitals",
        "🥗 Nutrition",
        "🌍 Environmental"
    ])

    with tab1:
        st.header("Heart & Fitness Metrics")
        st.info("Analyze your heart rate patterns and fitness metrics.")
        
        # Heart Rate
        st.subheader("📈 Heart Rate")
        display_heart_metrics(st.session_state.heart_rate_df, use_custom_range, start_date, end_date, selected_range, quick_ranges, selected_sources)
        
        # Resting Heart Rate
        if not st.session_state.resting_heart_rate_df.empty:
            st.subheader("💝 Resting Heart Rate")
            display_metric_over_time(st.session_state.resting_heart_rate_df, "Resting Heart Rate", "bpm",
                                  use_custom_range, start_date, end_date, selected_range, quick_ranges, selected_sources)
        
        # Heart Rate Variability
        if not st.session_state.heart_rate_variability_df.empty:
            st.subheader("💓 Heart Rate Variability")
            display_metric_over_time(st.session_state.heart_rate_variability_df, "HRV (SDNN)", "ms",
                                  use_custom_range, start_date, end_date, selected_range, quick_ranges, selected_sources)
        
        # VO2 Max
        if not st.session_state.vo2_max_df.empty:
            st.subheader("🫁 VO2 Max")
            display_metric_over_time(st.session_state.vo2_max_df, "VO2 Max", "mL/kg/min",
                                  use_custom_range, start_date, end_date, selected_range, quick_ranges, selected_sources)

    with tab2:
        st.header("Activity Metrics")
        st.info("Track your daily activity metrics.")
        
        # Steps and Energy
        display_activity_metrics(st.session_state.steps_df, st.session_state.active_energy_df, 
                               use_custom_range, start_date, end_date, selected_range, quick_ranges, selected_sources)
        
        # Distance
        st.subheader("📏 Distance")
        col1, col2 = st.columns(2)
        with col1:
            if not st.session_state.distance_walking_running_df.empty:
                display_metric_over_time(st.session_state.distance_walking_running_df, "Walking/Running Distance", "km",
                                      use_custom_range, start_date, end_date, selected_range, quick_ranges, selected_sources)
        with col2:
            if not st.session_state.distance_cycling_df.empty:
                display_metric_over_time(st.session_state.distance_cycling_df, "Cycling Distance", "km",
                                      use_custom_range, start_date, end_date, selected_range, quick_ranges, selected_sources)
        
        # Other Activity Metrics
        st.subheader("🎯 Other Activity Metrics")
        col1, col2 = st.columns(2)
        with col1:
            if not st.session_state.flights_climbed_df.empty:
                display_metric_over_time(st.session_state.flights_climbed_df, "Flights Climbed", "flights",
                                      use_custom_range, start_date, end_date, selected_range, quick_ranges, selected_sources)
            if not st.session_state.exercise_time_df.empty:
                display_metric_over_time(st.session_state.exercise_time_df, "Exercise Time", "minutes",
                                      use_custom_range, start_date, end_date, selected_range, quick_ranges, selected_sources)
        with col2:
            if not st.session_state.stand_time_df.empty:
                display_metric_over_time(st.session_state.stand_time_df, "Stand Time", "minutes",
                                      use_custom_range, start_date, end_date, selected_range, quick_ranges, selected_sources)

    with tab3:
        st.header("Workout Analysis")
        st.info("Review your workout history.")
        display_workout_metrics(st.session_state.workouts_df, use_custom_range, start_date, end_date, selected_range, quick_ranges, selected_sources)

    with tab4:
        st.header("Sleep Analysis")
        st.info("Analyze your sleep patterns.")
        display_sleep_metrics(st.session_state.sleep_df, use_custom_range, start_date, end_date, selected_range, quick_ranges, selected_sources)

    with tab5:
        st.header("Body Metrics")
        st.info("Track your body measurements and composition.")
        if not st.session_state.body_metrics_df.empty:
            display_body_metrics(st.session_state.body_metrics_df, use_custom_range, start_date, end_date, selected_range, quick_ranges, selected_sources)
        else:
            st.warning("No body metrics data available.")

    with tab6:
        st.header("Vitals")
        st.info("Monitor your vital signs.")
        
        col1, col2 = st.columns(2)
        with col1:
            if not st.session_state.oxygen_saturation_df.empty:
                st.subheader("🫁 Blood Oxygen")
                display_metric_over_time(st.session_state.oxygen_saturation_df, "Blood Oxygen", "%",
                                      use_custom_range, start_date, end_date, selected_range, quick_ranges, selected_sources)
        with col2:
            if not st.session_state.respiratory_rate_df.empty:
                st.subheader("🫁 Respiratory Rate")
                display_metric_over_time(st.session_state.respiratory_rate_df, "Respiratory Rate", "breaths/min",
                                      use_custom_range, start_date, end_date, selected_range, quick_ranges, selected_sources)

    with tab7:
        st.header("Nutrition")
        st.info("Track your nutrition and hydration.")
        
        col1, col2 = st.columns(2)
        with col1:
            if not st.session_state.water_df.empty:
                st.subheader("💧 Water Intake")
                display_metric_over_time(st.session_state.water_df, "Water", "mL",
                                      use_custom_range, start_date, end_date, selected_range, quick_ranges, selected_sources)
        with col2:
            if not st.session_state.caffeine_df.empty:
                st.subheader("☕ Caffeine Intake")
                display_metric_over_time(st.session_state.caffeine_df, "Caffeine", "mg",
                                      use_custom_range, start_date, end_date, selected_range, quick_ranges, selected_sources)
        
        if not st.session_state.dietary_metrics_df.empty:
            st.subheader("🍎 Dietary Metrics")
            display_dietary_metrics(st.session_state.dietary_metrics_df, use_custom_range, start_date, end_date, selected_range, quick_ranges, selected_sources)

    with tab8:
        st.header("Environmental")
        st.info("Track environmental factors affecting your health.")
        if not st.session_state.environmental_df.empty:
            display_environmental_metrics(st.session_state.environmental_df, use_custom_range, start_date, end_date, selected_range, quick_ranges, selected_sources)
        else:
            st.warning("No environmental data available.")

    with tab5:
        st.header("Health Insights & Correlations")
        st.info("Discover relationships between different health metrics and analyze trends.")
        
        # Create deep copies and make timezone-naive
        heart_df = make_timezone_naive(st.session_state.heart_rate_df.copy(deep=True))
        steps_df = make_timezone_naive(st.session_state.steps_df.copy(deep=True))
        sleep_df = make_timezone_naive(st.session_state.sleep_df.copy(deep=True))
        workouts_df = make_timezone_naive(st.session_state.workouts_df.copy(deep=True))

        # Display detailed insights
        st.subheader("❤️ Heart Rate Insights")
        analyze_heart_rate_patterns(heart_df)
        
        st.subheader("😴 Sleep Insights")
        analyze_sleep_quality(sleep_df)
        
        st.subheader("💪 Workout Insights")
        analyze_workout_effectiveness(workouts_df)
        
        st.subheader("🏃‍♂️ Activity Insights")
        analyze_activity_patterns(steps_df)
        
        st.subheader("🔄 Health Correlations")
        analyze_health_correlations(heart_df, steps_df, sleep_df)

    st.sidebar.markdown("""
    ### About
    This app helps you visualize and analyze your Apple Health data. 
    Data is preprocessed for faster loading times.
    Each tab includes a download option for the filtered data.
    
    New: Added detailed insights and correlations!
    """)

if __name__ == "__main__":
    main()