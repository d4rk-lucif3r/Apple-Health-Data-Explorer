import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats
import numpy as np
from datetime import datetime, timedelta

def analyze_heart_rate_patterns(heart_df):
    """Analyze heart rate patterns and provide insights"""
    if not heart_df.empty:
        # Calculate daily statistics
        daily_stats = heart_df.groupby(heart_df['date'].dt.date).agg({
            'value': ['mean', 'min', 'max', 'std']
        })['value']
        
        # Time of day analysis
        heart_df['hour'] = heart_df['date'].dt.hour
        hourly_avg = heart_df.groupby('hour')['value'].mean()
        
        # Identify peak hours
        peak_hour = hourly_avg.idxmax()
        lowest_hour = hourly_avg.idxmin()
        
        # Calculate variability metrics
        overall_variability = daily_stats['std'].mean()
        
        # Display insights
        st.write("📊 Heart Rate Patterns:")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Peak Activity Hour", f"{peak_hour}:00")
            st.metric("Lowest Activity Hour", f"{lowest_hour}:00")
        with col2:
            st.metric("Daily Variability", f"{overall_variability:.1f} bpm")
        
        # Visualize hourly patterns
        fig = px.line(x=hourly_avg.index, y=hourly_avg.values,
                     title="Average Heart Rate by Hour of Day",
                     labels={"x": "Hour", "y": "Heart Rate (bpm)"})
        st.plotly_chart(fig, use_container_width=True)

def analyze_sleep_quality(sleep_df):
    """Analyze sleep patterns and quality"""
    if not sleep_df.empty:
        # Calculate sleep duration
        sleep_df['duration'] = (pd.to_datetime(sleep_df['endDate']) - 
                              pd.to_datetime(sleep_df['date'])).dt.total_seconds() / 3600
        
        # Daily sleep analysis
        daily_sleep = sleep_df.groupby(pd.to_datetime(sleep_df['date']).dt.date).agg({
            'duration': 'sum'
        }).reset_index()
        
        # Sleep consistency analysis
        sleep_df['start_hour'] = pd.to_datetime(sleep_df['date']).dt.hour
        sleep_df['end_hour'] = pd.to_datetime(sleep_df['endDate']).dt.hour
        
        # Calculate metrics
        avg_duration = daily_sleep['duration'].mean()
        sleep_consistency = daily_sleep['duration'].std()
        most_common_start = sleep_df['start_hour'].mode().iloc[0]
        
        # Display insights
        st.write("😴 Sleep Analysis:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Sleep Duration", f"{avg_duration:.1f} hours")
        with col2:
            st.metric("Sleep Consistency", f"±{sleep_consistency:.1f} hours")
        with col3:
            st.metric("Typical Bedtime", f"{most_common_start}:00")
        
        # Visualize sleep duration trend
        fig = px.line(daily_sleep, x='date', y='duration',
                     title="Sleep Duration Over Time",
                     labels={"duration": "Sleep Duration (hours)", "date": "Date"})
        fig.add_hline(y=8, line_dash="dash", line_color="green",
                     annotation_text="Recommended 8 hours")
        st.plotly_chart(fig, use_container_width=True)

def analyze_workout_effectiveness(workouts_df):
    """Analyze workout patterns and effectiveness"""
    if not workouts_df.empty:
        # Workout frequency analysis
        workout_counts = workouts_df['type'].value_counts()
        weekly_frequency = len(workouts_df) / (
            (workouts_df['date'].max() - workouts_df['date'].min()).days / 7)
        
        # Duration and calorie analysis
        avg_duration = workouts_df['duration'].mean() / 60  # Convert to minutes
        avg_calories = workouts_df['energy'].mean()
        
        # Progress analysis
        workouts_df['week'] = workouts_df['date'].dt.isocalendar().week
        weekly_stats = workouts_df.groupby('week').agg({
            'duration': 'sum',
            'energy': 'sum'
        })
        
        # Display insights
        st.write("💪 Workout Analysis:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Weekly Workout Frequency", f"{weekly_frequency:.1f}")
        with col2:
            st.metric("Average Duration", f"{avg_duration:.0f} min")
        with col3:
            st.metric("Average Calories", f"{avg_calories:.0f} kcal")
        
        # Visualize workout distribution
        fig = px.pie(values=workout_counts.values, names=workout_counts.index,
                    title="Workout Type Distribution")
        st.plotly_chart(fig, use_container_width=True)

def analyze_activity_patterns(steps_df):
    """Analyze daily activity patterns"""
    if not steps_df.empty:
        # Daily steps analysis
        daily_steps = steps_df.groupby(steps_df['date'].dt.date)['value'].sum()
        
        # Weekly pattern analysis
        steps_df['weekday'] = steps_df['date'].dt.day_name()
        weekday_avg = steps_df.groupby('weekday')['value'].mean()
        
        # Achievement analysis
        days_over_10k = (daily_steps >= 10000).sum()
        achievement_rate = (days_over_10k / len(daily_steps)) * 100
        
        # Trend analysis
        weekly_trend = daily_steps.rolling(window=7).mean()
        
        # Display insights
        st.write("🏃‍♂️ Activity Patterns:")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("10k Steps Achievement Rate", f"{achievement_rate:.1f}%")
            most_active_day = weekday_avg.idxmax()
            st.metric("Most Active Day", most_active_day)
        with col2:
            streak = calculate_streak(daily_steps >= 10000)
            st.metric("Best Active Streak", f"{streak} days")
            least_active_day = weekday_avg.idxmin()
            st.metric("Least Active Day", least_active_day)
        
        # Visualize weekly pattern
        fig = px.bar(x=weekday_avg.index, y=weekday_avg.values,
                    title="Average Steps by Day of Week",
                    labels={"x": "Day", "y": "Steps"})
        st.plotly_chart(fig, use_container_width=True)

def analyze_health_correlations(heart_df, steps_df, sleep_df):
    """Analyze correlations between different health metrics"""
    if not heart_df.empty and not steps_df.empty and not sleep_df.empty:
        # Prepare daily aggregates
        daily_heart = heart_df.groupby(heart_df['date'].dt.date)['value'].mean()
        daily_steps = steps_df.groupby(steps_df['date'].dt.date)['value'].sum()
        
        sleep_df['duration'] = (pd.to_datetime(sleep_df['endDate']) - 
                              pd.to_datetime(sleep_df['date'])).dt.total_seconds() / 3600
        daily_sleep = sleep_df.groupby(pd.to_datetime(sleep_df['date']).dt.date)['duration'].sum()
        
        # Merge metrics
        metrics_df = pd.DataFrame({
            'heart_rate': daily_heart,
            'steps': daily_steps,
            'sleep': daily_sleep
        }).dropna()
        
        # Calculate correlations
        correlations = metrics_df.corr()
        
        # Display insights
        st.write("🔄 Health Correlations:")
        
        # Correlation matrix heatmap
        fig = px.imshow(correlations,
                       labels=dict(color="Correlation"),
                       x=['Heart Rate', 'Steps', 'Sleep'],
                       y=['Heart Rate', 'Steps', 'Sleep'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Interpret correlations
        interpret_correlations(correlations)

def analyze_comprehensive_health(heart_df, steps_df, sleep_df, workouts_df):
    """Provide comprehensive health analysis using all available metrics"""
    st.header("🎯 Comprehensive Health Analysis")
    
    # Overall health score components
    scores = {}
    
    # Activity Score (based on steps and workouts)
    if not steps_df.empty:
        daily_steps = steps_df.groupby(steps_df['date'].dt.date)['value'].sum()
        steps_score = min(100, (daily_steps.mean() / 10000) * 100)
        scores['Activity'] = steps_score
    
    # Sleep Score
    if not sleep_df.empty:
        sleep_df['duration'] = (pd.to_datetime(sleep_df['endDate']) - 
                              pd.to_datetime(sleep_df['date'])).dt.total_seconds() / 3600
        daily_sleep = sleep_df.groupby(pd.to_datetime(sleep_df['date']).dt.date)['duration'].sum()
        sleep_score = min(100, (daily_sleep.mean() / 8) * 100)
        scores['Sleep'] = sleep_score
    
    # Heart Health Score
    if not heart_df.empty:
        daily_hr_var = heart_df.groupby(heart_df['date'].dt.date)['value'].std()
        hr_var_score = min(100, (daily_hr_var.mean() / 20) * 100)
        scores['Heart Health'] = hr_var_score
    
    # Workout Score
    if not workouts_df.empty:
        weekly_workouts = len(workouts_df) / ((workouts_df['date'].max() - 
                                             workouts_df['date'].min()).days / 7)
        workout_score = min(100, (weekly_workouts / 5) * 100)
        scores['Exercise'] = workout_score
    
    # Display overall health score
    if scores:
        overall_score = sum(scores.values()) / len(scores)
        st.metric("Overall Health Score", f"{overall_score:.0f}/100")
        
        # Display component scores
        cols = st.columns(len(scores))
        for i, (component, score) in enumerate(scores.items()):
            with cols[i]:
                st.metric(component, f"{score:.0f}/100")
    
    # Health trends
    st.subheader("📈 Health Trends")
    
    # Activity consistency
    if not steps_df.empty:
        daily_steps = steps_df.groupby(steps_df['date'].dt.date)['value'].sum()
        consistency = calculate_consistency_score(daily_steps, target=10000)
        st.metric("Activity Consistency", f"{consistency:.0f}%")
    
    # Sleep regularity
    if not sleep_df.empty:
        sleep_df['start_hour'] = pd.to_datetime(sleep_df['date']).dt.hour
        sleep_regularity = calculate_sleep_regularity(sleep_df)
        st.metric("Sleep Regularity", f"{sleep_regularity:.0f}%")
    
    # Recovery patterns
    if not heart_df.empty and not workouts_df.empty:
        recovery_score = analyze_recovery_patterns(heart_df, workouts_df)
        st.metric("Recovery Quality", f"{recovery_score:.0f}%")

def calculate_streak(series):
    """Calculate the longest streak of True values"""
    streak = 0
    max_streak = 0
    for value in series:
        if value:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return max_streak

def interpret_correlations(corr_matrix):
    """Interpret and explain correlation results"""
    interpretations = []
    
    # Steps vs Heart Rate
    steps_hr_corr = corr_matrix.loc['steps', 'heart_rate']
    if abs(steps_hr_corr) > 0.3:
        interpretations.append(
            f"{'Strong' if abs(steps_hr_corr) > 0.5 else 'Moderate'} "
            f"{'positive' if steps_hr_corr > 0 else 'negative'} correlation "
            f"between daily steps and heart rate "
            f"({steps_hr_corr:.2f})"
        )
    
    # Sleep vs Steps
    sleep_steps_corr = corr_matrix.loc['sleep', 'steps']
    if abs(sleep_steps_corr) > 0.3:
        interpretations.append(
            f"{'Strong' if abs(sleep_steps_corr) > 0.5 else 'Moderate'} "
            f"{'positive' if sleep_steps_corr > 0 else 'negative'} correlation "
            f"between sleep duration and daily steps "
            f"({sleep_steps_corr:.2f})"
        )
    
    # Sleep vs Heart Rate
    sleep_hr_corr = corr_matrix.loc['sleep', 'heart_rate']
    if abs(sleep_hr_corr) > 0.3:
        interpretations.append(
            f"{'Strong' if abs(sleep_hr_corr) > 0.5 else 'Moderate'} "
            f"{'positive' if sleep_hr_corr > 0 else 'negative'} correlation "
            f"between sleep duration and heart rate "
            f"({sleep_hr_corr:.2f})"
        )
    
    if interpretations:
        st.write("Key Findings:")
        for interpretation in interpretations:
            st.write(f"• {interpretation}")
    else:
        st.write("No strong correlations found between metrics.")

def calculate_consistency_score(series, target):
    """Calculate consistency score based on how close values are to a target"""
    deviations = abs(series - target) / target
    scores = (1 - deviations).clip(0, 1) * 100
    return scores.mean()

def calculate_sleep_regularity(sleep_df):
    """Calculate sleep schedule regularity"""
    start_times = sleep_df['start_hour']
    std_dev = start_times.std()
    # Convert std dev hours to a 0-100 score (lower std dev = higher score)
    score = max(0, 100 - (std_dev * 20))  # 5 hours std dev = 0 score
    return score

def analyze_recovery_patterns(heart_df, workouts_df):
    """Analyze recovery patterns after workouts"""
    if heart_df.empty or workouts_df.empty:
        return 0
    
    # Get resting heart rate for each day
    daily_rhr = heart_df.groupby(heart_df['date'].dt.date)['value'].quantile(0.1)
    
    # Analyze heart rate recovery after workout days
    workout_dates = workouts_df['date'].dt.date.unique()
    
    recovery_scores = []
    for workout_date in workout_dates:
        next_day = workout_date + timedelta(days=1)
        if workout_date in daily_rhr.index and next_day in daily_rhr.index:
            rhr_change = daily_rhr[next_day] - daily_rhr[workout_date]
            # Lower RHR next day indicates good recovery
            recovery_score = max(0, 100 - (rhr_change * 5))  # 20 bpm increase = 0 score
            recovery_scores.append(recovery_score)
    
    return np.mean(recovery_scores) if recovery_scores else 0