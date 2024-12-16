# 🍎 Apple Health Data Explorer

A powerful and intuitive dashboard for visualizing and analyzing your Apple Health data with advanced insights and correlations.

## ✨ Features

### 📊 Interactive Visualizations
- **Heart Rate Analysis**: Track patterns, variations, and recovery metrics
- **Activity Monitoring**: Steps, distance, and energy expenditure
- **Workout Analysis**: Duration, intensity, and type distribution
- **Sleep Patterns**: Duration, quality, and consistency tracking

### 🔍 Advanced Insights
- Heart rate patterns by time of day
- Sleep quality and debt analysis
- Workout effectiveness and progress tracking
- Activity consistency and patterns
- Cross-metric correlations and trends

### 🎛️ Flexible Date Filtering
- Quick presets (7 days, 30 days, 90 days, 1 year)
- Custom date range selection
- Historical data up to 5 years

### 📥 Data Export
- Download filtered data as CSV
- Available for all metrics and time ranges

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- Apple Health data export (export.xml from Apple Health app)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/apple_health_explorer.git
cd apple_health_explorer
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Export your Apple Health data:
   - Open the Health app on your iPhone
   - Tap your profile picture
   - Tap "Export All Health Data"
   - Extract the zip file
   - Place the `export.xml` file in the `apple_health_export` directory

### Usage

Run the application using the main script:
```bash
python main.py
```

This will:
1. Preprocess your health data
2. Launch the interactive dashboard
3. Open your default browser automatically

## 📁 Project Structure

```
apple_health_explorer/
├── app.py              # Main Streamlit application
├── main.py            # Entry point script
├── data_loader.py     # Data loading utilities
├── insights.py        # Advanced health analytics
├── utils.py           # Common utility functions
├── requirements.txt   # Project dependencies
├── processed_data/    # Preprocessed CSV files
└── apple_health_export/
    └── export.xml     # Your health data export
```

## 📊 Available Metrics

### Heart Health
- Heart rate over time
- Resting heart rate
- Heart rate variability
- Recovery patterns
- Time-of-day analysis

### Activity
- Daily steps
- Distance covered
- Active energy burned
- Activity patterns
- Consistency scores

### Workouts
- Duration and frequency
- Calorie expenditure
- Workout type distribution
- Intensity analysis
- Progress tracking

### Sleep
- Sleep duration
- Sleep quality score
- Sleep debt tracking
- Consistency analysis
- Sleep timing patterns

### Insights & Correlations
- Steps vs Heart Rate
- Sleep vs Recovery
- Activity vs Sleep Quality
- Workout Impact Analysis
- Long-term Trends

## 🛠️ Customization

### Date Ranges
- Use quick select for common ranges
- Custom date picker for specific periods
- Filter any metric by date range

### Data Export
Each visualization includes a download button for the filtered data in CSV format.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Streamlit
- Powered by Pandas and Plotly
- Inspired by the Apple Health app

## 📬 Support

If you encounter any issues or have questions, please open an issue on GitHub.