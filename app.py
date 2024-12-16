import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
import os

from data_loader import load_metadata, load_data
from utils import (
    get_csv_download_link, 
    format_duration, 
    get_date_range_mask,
    make_timezone_naive
)
from insights import (
    analyze_heart_rate_patterns,
    analyze_sleep_quality,
    analyze_workout_effectiveness,
    analyze_activity_patterns,
    analyze_health_correlations
)

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

def display_heart_metrics(heart_rate_df, use_custom_range, start_date=None, end_date=None, selected_range=None, quick_ranges=None):
    """Display heart rate metrics and visualizations"""
    if not heart_rate_df.empty:
        mask = get_date_range_mask(heart_rate_df, use_custom_range, start_date, end_date, selected_range, quick_ranges)
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

def display_activity_metrics(steps_df, use_custom_range, start_date=None, end_date=None, selected_range=None, quick_ranges=None):
    """Display activity metrics and visualizations"""
    if not steps_df.empty:
        mask = get_date_range_mask(steps_df, use_custom_range, start_date, end_date, selected_range, quick_ranges)
        filtered_steps_df = steps_df[mask]

        st.markdown(get_csv_download_link(filtered_steps_df, "activity_data.csv"), unsafe_allow_html=True)

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
        st.warning("No activity data available for the selected period.")

def display_workout_metrics(workout_df, use_custom_range, start_date=None, end_date=None, selected_range=None, quick_ranges=None):
    """Display workout metrics and visualizations"""
    if not workout_df.empty:
        mask = get_date_range_mask(workout_df, use_custom_range, start_date, end_date, selected_range, quick_ranges)
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

def display_sleep_metrics(sleep_df, use_custom_range, start_date=None, end_date=None, selected_range=None, quick_ranges=None):
    """Display sleep metrics and visualizations"""
    if not sleep_df.empty:
        mask = get_date_range_mask(sleep_df, use_custom_range, start_date, end_date, selected_range, quick_ranges)
        filtered_sleep_df = sleep_df[mask]

        st.markdown(get_csv_download_link(filtered_sleep_df, "sleep_data.csv"), unsafe_allow_html=True)

        if not filtered_sleep_df.empty:
            filtered_sleep_df["duration"] = (filtered_sleep_df["endDate"] - filtered_sleep_df["date"]).dt.total_seconds()
            daily_sleep = filtered_sleep_df.groupby(filtered_sleep_df["date"].dt.date)["duration"].sum()

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
        st.session_state.heart_rate_df = load_data("heart_rate")
        st.session_state.steps_df = load_data("steps")
        st.session_state.sleep_df = load_data("sleep")
        st.session_state.workouts_df = load_data("workouts")
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

    # Sidebar date filters
    st.sidebar.header("📅 Filters")
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["❤️ Heart", "🏃‍♂️ Activity", "🏋️‍♂️ Workouts", "😴 Sleep", "📊 Insights"]
    )

    with tab1:
        st.header("Heart Health Metrics")
        st.info("Analyze your heart rate patterns, including resting heart rate and heart rate variability.")
        display_heart_metrics(st.session_state.heart_rate_df, use_custom_range, start_date, end_date, selected_range, quick_ranges)

    with tab2:
        st.header("Activity Metrics")
        st.info("Track your daily steps, distance, and active energy burned.")
        display_activity_metrics(st.session_state.steps_df, use_custom_range, start_date, end_date, selected_range, quick_ranges)

    with tab3:
        st.header("Workout Analysis")
        st.info("Review your workout history, including duration, distance, and calories burned.")
        display_workout_metrics(st.session_state.workouts_df, use_custom_range, start_date, end_date, selected_range, quick_ranges)

    with tab4:
        st.header("Sleep Analysis")
        st.info("Analyze your sleep patterns and duration.")
        display_sleep_metrics(st.session_state.sleep_df, use_custom_range, start_date, end_date, selected_range, quick_ranges)

    with tab5:
        st.header("Health Insights & Correlations")
        st.info("Discover relationships between different health metrics and analyze trends.")
        
        # Prepare timezone-naive copies for analysis
        heart_df = make_timezone_naive(st.session_state.heart_rate_df.copy())
        steps_df = make_timezone_naive(st.session_state.steps_df.copy())
        sleep_df = make_timezone_naive(st.session_state.sleep_df.copy())
        workouts_df = make_timezone_naive(st.session_state.workouts_df.copy())

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