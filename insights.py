import pandas as pd
import plotly.express as px
import streamlit as st
from utils import calculate_trend, get_day_part

def analyze_heart_rate_patterns(heart_df):
    """Analyze heart rate patterns and variations"""
    if not heart_df.empty:
        # Time of day analysis
        heart_df['hour'] = heart_df['date'].dt.hour
        heart_df['day_part'] = heart_df['hour'].apply(get_day_part)
        time_analysis = heart_df.groupby('day_part')['value'].agg(['mean', 'std']).round(1)
        
        st.subheader("📊 Heart Rate by Time of Day")
        st.dataframe(time_analysis)
        
        # Variability analysis
        daily_variation = heart_df.groupby(heart_df['date'].dt.date)['value'].std().mean()
        st.metric("Daily Heart Rate Variation", f"{daily_variation:.1f} bpm")
        
        # Recovery analysis
        resting_periods = heart_df[heart_df['value'] < heart_df['value'].quantile(0.25)]
        avg_recovery = resting_periods['value'].mean()
        st.metric("Average Recovery Heart Rate", f"{avg_recovery:.1f} bpm")

def analyze_sleep_quality(sleep_df):
    """Analyze sleep quality and patterns"""
    if not sleep_df.empty:
        sleep_df['duration'] = (sleep_df['endDate'] - sleep_df['date']).dt.total_seconds() / 3600
        sleep_df['start_hour'] = sleep_df['date'].dt.hour
        
        # Sleep timing analysis
        avg_sleep_start = sleep_df['start_hour'].mean()
        st.subheader("⏰ Sleep Timing Analysis")
        st.metric("Average Sleep Start Time", f"{int(avg_sleep_start):02d}:{int((avg_sleep_start % 1) * 60):02d}")
        
        # Sleep consistency
        daily_sleep = sleep_df.groupby(sleep_df['date'].dt.date)['duration'].sum()
        consistency_score = 100 - (daily_sleep.std() * 10)
        st.metric("Sleep Consistency Score", f"{max(0, min(100, consistency_score)):.1f}%")
        
        # Sleep debt analysis
        sleep_debt = (8 - daily_sleep).clip(lower=0).sum()
        st.metric("Accumulated Sleep Debt", f"{sleep_debt:.1f} hours")

def analyze_workout_effectiveness(workouts_df):
    """Analyze workout effectiveness and trends"""
    if not workouts_df.empty:
        # Workout intensity distribution
        workouts_df['intensity'] = workouts_df['energy'] / workouts_df['duration']
        intensity_dist = workouts_df.groupby('type')['intensity'].mean().sort_values(ascending=False)
        
        st.subheader("🔥 Workout Intensity Analysis")
        fig = px.bar(
            intensity_dist.reset_index(),
            x='type',
            y='intensity',
            title="Average Intensity by Workout Type",
            labels={"intensity": "Calories/Minute", "type": "Workout Type"}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Progress tracking
        weekly_workouts = workouts_df.groupby(pd.Grouper(key='date', freq='W'))['duration'].count()
        trend_direction, trend_pct = calculate_trend(weekly_workouts.values)
        st.metric(
            "Workout Frequency Trend", 
            trend_direction,
            f"{abs(trend_pct):.1f}% change"
        )

def analyze_activity_patterns(steps_df):
    """Analyze activity patterns and trends"""
    if not steps_df.empty:
        # Daily pattern analysis
        steps_df['hour'] = steps_df['date'].dt.hour
        hourly_steps = steps_df.groupby('hour')['value'].mean()
        
        st.subheader("👣 Activity Patterns")
        fig = px.line(
            hourly_steps.reset_index(),
            x='hour',
            y='value',
            title="Average Steps by Hour",
            labels={"value": "Steps", "hour": "Hour of Day"}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Active days analysis
        daily_steps = steps_df.groupby(steps_df['date'].dt.date)['value'].sum()
        active_days = (daily_steps >= 10000).mean() * 100
        st.metric("Active Days", f"{active_days:.1f}%", help="Days with 10,000+ steps")
        
        # Activity consistency
        consistency = 100 - (daily_steps.std() / daily_steps.mean() * 100)
        st.metric("Activity Consistency", f"{max(0, min(100, consistency)):.1f}%")

def analyze_health_correlations(heart_df, steps_df, sleep_df):
    """Analyze correlations between different health metrics"""
    if not any(df.empty for df in [heart_df, steps_df, sleep_df]):
        st.subheader("🔄 Health Metric Correlations")
        
        # Prepare daily metrics
        daily_heart = heart_df.groupby(heart_df['date'].dt.date)['value'].mean()
        daily_steps = steps_df.groupby(steps_df['date'].dt.date)['value'].sum()
        daily_sleep = sleep_df.groupby(sleep_df['date'].dt.date).apply(
            lambda x: (x['endDate'].max() - x['date'].min()).total_seconds() / 3600
        )
        
        # Merge metrics
        daily_metrics = pd.DataFrame({
            'heart_rate': daily_heart,
            'steps': daily_steps,
            'sleep': daily_sleep
        }).dropna()
        
        # Calculate correlations
        correlations = daily_metrics.corr()
        
        # Display correlation insights
        col1, col2 = st.columns(2)
        with col1:
            steps_hr_corr = correlations.loc['steps', 'heart_rate']
            st.metric(
                "Steps vs Heart Rate",
                f"{abs(steps_hr_corr):.2f}",
                help="Correlation coefficient (-1 to 1)"
            )
        with col2:
            sleep_hr_corr = correlations.loc['sleep', 'heart_rate']
            st.metric(
                "Sleep vs Heart Rate",
                f"{abs(sleep_hr_corr):.2f}",
                help="Correlation coefficient (-1 to 1)"
            )