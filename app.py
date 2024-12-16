import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import base64

# Set page config
st.set_page_config(
    page_title="Apple Health Data Explorer",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_metadata():
    """Load metadata about processed data"""
    try:
        with open("processed_data/metadata.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(
            "Processed data not found. Please run preprocess_health_data.py first."
        )
        st.stop()


@st.cache_data
def load_data(data_type):
    """Load preprocessed data from CSV"""
    try:
        df = pd.read_csv(f"processed_data/{data_type}.csv")
        # Convert date columns to datetime using ISO8601 format
        date_columns = ["date", "endDate"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format="ISO8601")
        return df
    except FileNotFoundError:
        return pd.DataFrame()


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


def main():
    st.title("🍎 Apple Health Data Explorer")

    # Check if processed data exists
    if not os.path.exists("processed_data/metadata.json"):
        st.error(
            """
        Processed data not found! Please run the preprocessing script first:
        ```
        python preprocess_health_data.py
        ```
        """
        )
        st.stop()

    # Load metadata
    metadata = load_metadata()
    last_processed = datetime.fromisoformat(metadata["last_processed"])

    st.markdown(
        f"""
    This app allows you to explore your Apple Health data with interactive visualizations. 
    Data was last processed on: {last_processed.strftime('%Y-%m-%d %H:%M:%S')}
    """
    )

    # Sidebar date filters
    st.sidebar.header("📅 Filters")

    # Date range selection
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
    else:
        # Custom date range
        max_date = datetime.now().date()
        min_possible_date = max_date - timedelta(days=365*5)  # 5 years back
        
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
        st.info(
            "Analyze your heart rate patterns, including resting heart rate and heart rate variability."
        )

        if st.button("📊 Load Heart Data", key="heart"):
            with st.spinner("Loading heart health data..."):
                heart_rate_df = load_data("heart_rate")
                resting_hr_df = load_data("resting_heart_rate")
                hrv_df = load_data("heart_rate_variability")

                if not heart_rate_df.empty:
                    # Calculate date range and filter data
                    if use_custom_range:
                        mask = (heart_rate_df["date"].dt.date >= start_date) & (
                            heart_rate_df["date"].dt.date <= end_date
                        )
                    else:
                        max_date = heart_rate_df["date"].max()
                        if quick_ranges[selected_range]:
                            min_date = max_date - quick_ranges[selected_range]
                        else:
                            min_date = heart_rate_df["date"].min()
                        mask = (heart_rate_df["date"].dt.date >= min_date.date()) & (
                            heart_rate_df["date"].dt.date <= max_date.date()
                        )
                    filtered_hr_df = heart_rate_df[mask]

                    # Add download button
                    st.markdown(
                        get_csv_download_link(filtered_hr_df, "heart_rate_data.csv"),
                        unsafe_allow_html=True,
                    )

                    # Display metrics
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

                    # Heart Rate Over Time
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

    with tab2:
        st.header("Activity Metrics")
        st.info("Track your daily steps, distance, and active energy burned.")

        if st.button("📊 Load Activity Data", key="activity"):
            with st.spinner("Loading activity data..."):
                steps_df = load_data("steps")
                distance_df = load_data("distance")
                energy_df = load_data("active_energy")

                if not steps_df.empty:
                    # Calculate date range and filter data
                    if use_custom_range:
                        mask = (steps_df["date"].dt.date >= start_date) & (
                            steps_df["date"].dt.date <= end_date
                        )
                    else:
                        max_date = steps_df["date"].max()
                        if quick_ranges[selected_range]:
                            min_date = max_date - quick_ranges[selected_range]
                        else:
                            min_date = steps_df["date"].min()
                        mask = (steps_df["date"].dt.date >= min_date.date()) & (
                            steps_df["date"].dt.date <= max_date.date()
                        )
                    filtered_steps_df = steps_df[mask]

                    # Add download button
                    st.markdown(
                        get_csv_download_link(filtered_steps_df, "activity_data.csv"),
                        unsafe_allow_html=True,
                    )

                    # Calculate daily totals
                    daily_steps = filtered_steps_df.groupby(
                        filtered_steps_df["date"].dt.date
                    )["value"].sum()

                    # Display metrics
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

                    # Daily Steps Chart
                    daily_steps_df = daily_steps.reset_index()
                    fig = px.bar(
                        daily_steps_df,
                        x="date",
                        y="value",
                        title="Daily Steps",
                        labels={"value": "Steps", "date": "Date"},
                    )
                    fig.add_hline(
                        y=10000,
                        line_dash="dash",
                        line_color="green",
                        annotation_text="10,000 steps goal",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No activity data available for the selected period.")

    with tab3:
        st.header("Workout Analysis")
        st.info(
            "Review your workout history, including duration, distance, and calories burned."
        )

        if st.button("📊 Load Workout Data", key="workout"):
            with st.spinner("Loading workout data..."):
                workout_df = load_data("workouts")

                if not workout_df.empty:
                    # Calculate date range and filter data
                    if use_custom_range:
                        mask = (workout_df["date"].dt.date >= start_date) & (
                            workout_df["date"].dt.date <= end_date
                        )
                    else:
                        max_date = workout_df["date"].max()
                        if quick_ranges[selected_range]:
                            min_date = max_date - quick_ranges[selected_range]
                        else:
                            min_date = workout_df["date"].min()
                        mask = (workout_df["date"].dt.date >= min_date.date()) & (
                            workout_df["date"].dt.date <= max_date.date()
                        )
                    filtered_workout_df = workout_df[mask]

                    # Add download button
                    st.markdown(
                        get_csv_download_link(filtered_workout_df, "workout_data.csv"),
                        unsafe_allow_html=True,
                    )

                    if not filtered_workout_df.empty:
                        # Display metrics
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

                        # Workout Type Distribution
                        workout_counts = filtered_workout_df["type"].value_counts()
                        fig = px.pie(
                            values=workout_counts.values,
                            names=workout_counts.index,
                            title="Workout Type Distribution",
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No workout data available for the selected period.")

    with tab4:
        st.header("Sleep Analysis")
        st.info("Analyze your sleep patterns and duration.")

        if st.button("📊 Load Sleep Data", key="sleep"):
            with st.spinner("Loading sleep data..."):
                sleep_df = load_data("sleep")

                if not sleep_df.empty:
                    # Calculate date range and filter data
                    if use_custom_range:
                        mask = (sleep_df["date"].dt.date >= start_date) & (
                            sleep_df["date"].dt.date <= end_date
                        )
                    else:
                        max_date = sleep_df["date"].max()
                        if quick_ranges[selected_range]:
                            min_date = max_date - quick_ranges[selected_range]
                        else:
                            min_date = sleep_df["date"].min()
                        mask = (sleep_df["date"].dt.date >= min_date.date()) & (
                            sleep_df["date"].dt.date <= max_date.date()
                        )
                    filtered_sleep_df = sleep_df[mask]

                    # Add download button
                    st.markdown(
                        get_csv_download_link(filtered_sleep_df, "sleep_data.csv"),
                        unsafe_allow_html=True,
                    )

                    if not filtered_sleep_df.empty:
                        # Calculate sleep duration
                        filtered_sleep_df["duration"] = (
                            filtered_sleep_df["endDate"] - filtered_sleep_df["date"]
                        ).dt.total_seconds()
                        daily_sleep = filtered_sleep_df.groupby(
                            filtered_sleep_df["date"].dt.date
                        )["duration"].sum()

                        # Display metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            avg_sleep = daily_sleep.mean() / 3600  # Convert to hours
                            st.metric(
                                "Average Sleep Duration", f"{avg_sleep:.1f} hours"
                            )
                        with col2:
                            total_sleep_days = len(daily_sleep)
                            st.metric("Days with Sleep Data", total_sleep_days)
                        with col3:
                            days_over_8h = (daily_sleep / 3600 >= 8).sum()
                            st.metric("Days with 8+ Hours", days_over_8h)

                        # Daily Sleep Duration
                        daily_sleep_df = daily_sleep.reset_index()
                        daily_sleep_df["duration"] = (
                            daily_sleep_df["duration"] / 3600
                        )  # Convert to hours
                        fig = px.bar(
                            daily_sleep_df,
                            x="date",
                            y="duration",
                            title="Daily Sleep Duration",
                            labels={
                                "duration": "Sleep Duration (hours)",
                                "date": "Date",
                            },
                        )
                        fig.add_hline(
                            y=8,
                            line_dash="dash",
                            line_color="green",
                            annotation_text="Recommended 8 hours",
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No sleep data available for the selected period.")

    st.sidebar.markdown("---")
    # Add the new Insights tab content
    with tab5:
        st.header("Health Insights & Correlations")
        st.info(
            "Discover relationships between different health metrics and analyze trends."
        )

        if st.button("📊 Generate Insights", key="insights"):
            with st.spinner("Analyzing your health data..."):
                # Load required datasets
                heart_df = load_data("heart_rate")
                steps_df = load_data("steps")
                sleep_df = load_data("sleep")
                workouts_df = load_data("workouts")

                # Make all dataframes timezone-naive first
                for df in [heart_df, steps_df, sleep_df, workouts_df]:
                    if not df.empty and df["date"].dt.tz is not None:
                        df["date"] = df["date"].dt.tz_localize(None)
                    if (
                        "endDate" in df.columns
                        and not df.empty
                        and df["endDate"].dt.tz is not None
                    ):
                        df["endDate"] = df["endDate"].dt.tz_localize(None)

                # Calculate date range and filter data
                max_dates = [
                    df["date"].max()
                    for df in [heart_df, steps_df, sleep_df, workouts_df]
                    if not df.empty
                ]
                max_date = max(max_dates)

                if quick_ranges[selected_range]:
                    min_date = max_date - quick_ranges[selected_range]
                else:
                    min_dates = [
                        df["date"].min()
                        for df in [heart_df, steps_df, sleep_df, workouts_df]
                        if not df.empty
                    ]
                    min_date = min(min_dates)

                # 1. Activity Impact Analysis
                st.subheader("🎯 Activity Impact Analysis")
                if not steps_df.empty and not heart_df.empty:
                    # Calculate daily averages
                    daily_steps = (
                        steps_df.groupby(steps_df["date"].dt.date)["value"]
                        .sum()
                        .reset_index()
                    )
                    daily_heart = (
                        heart_df.groupby(heart_df["date"].dt.date)["value"]
                        .mean()
                        .reset_index()
                    )

                    # Merge data
                    merged_df = pd.merge(
                        daily_steps,
                        daily_heart,
                        on="date",
                        suffixes=("_steps", "_heart"),
                    )

                    # Create correlation plot
                    fig = px.scatter(
                        merged_df,
                        x="value_steps",
                        y="value_heart",
                        title="Steps vs Average Heart Rate",
                        labels={
                            "value_steps": "Daily Steps",
                            "value_heart": "Average Heart Rate (bpm)",
                        },
                        trendline="ols",
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # 2. Sleep Pattern Analysis
                st.subheader("😴 Sleep Pattern Analysis")
                if not sleep_df.empty:
                    sleep_df["duration"] = (
                        sleep_df["endDate"] - sleep_df["date"]
                    ).dt.total_seconds() / 3600
                    daily_sleep = (
                        sleep_df.groupby(sleep_df["date"].dt.date)["duration"]
                        .sum()
                        .reset_index()
                    )

                    # Calculate sleep consistency
                    sleep_std = daily_sleep["duration"].std()
                    sleep_mean = daily_sleep["duration"].mean()

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            "Sleep Consistency Score",
                            f"{max(0, min(100, 100 - (sleep_std * 10))):.1f}%",
                            help="Higher score means more consistent sleep duration",
                        )
                    with col2:
                        st.metric(
                            "Sleep Quality",
                            (
                                "Good"
                                if sleep_mean >= 7
                                else "Fair" if sleep_mean >= 6 else "Poor"
                            ),
                            help="Based on average sleep duration",
                        )

                # 3. Workout Effectiveness
                st.subheader("💪 Workout Effectiveness")
                if not workouts_df.empty:
                    # Calculate workout metrics
                    workout_metrics = (
                        workouts_df.groupby("type")
                        .agg(
                            {
                                "duration": ["count", "mean"],
                                "energy": "mean",
                                "distance": "mean",
                            }
                        )
                        .round(2)
                    )

                    workout_metrics.columns = [
                        "Count",
                        "Avg Duration (min)",
                        "Avg Calories",
                        "Avg Distance (km)",
                    ]
                    workout_metrics["Avg Duration (min)"] = (
                        workout_metrics["Avg Duration (min)"] / 60
                    )

                    st.dataframe(workout_metrics)

                # 4. Heart Rate Zone Analysis
                st.subheader("❤️ Heart Rate Zone Analysis")
                if not heart_df.empty:
                    # Define heart rate zones
                    def get_zone(hr):
                        if hr < 100:
                            return "Rest (< 100 bpm)"
                        elif hr < 120:
                            return "Light (100-120 bpm)"
                        elif hr < 140:
                            return "Moderate (120-140 bpm)"
                        elif hr < 160:
                            return "Vigorous (140-160 bpm)"
                        else:
                            return "Peak (> 160 bpm)"

                    heart_df["zone"] = heart_df["value"].apply(get_zone)
                    zone_dist = heart_df["zone"].value_counts()

                    fig = px.pie(
                        values=zone_dist.values,
                        names=zone_dist.index,
                        title="Heart Rate Zone Distribution",
                    )
                    st.plotly_chart(fig, use_container_width=True)

    st.sidebar.markdown(
        """
    ### About
    This app helps you visualize and analyze your Apple Health data. 
    Data is preprocessed for faster loading times.
    Each tab includes a download option for the filtered data.
    
    New: Added Insights tab for deeper analysis and correlations!
    """
    )


if __name__ == "__main__":
    main()
