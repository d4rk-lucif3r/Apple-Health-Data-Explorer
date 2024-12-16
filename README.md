# Apple Health Data Explorer 🍎

An interactive Streamlit application to visualize and analyze your Apple Health data. This app provides insights into your:
- Heart rate patterns and variability
- Daily activity metrics (steps, distance)
- Workout statistics and trends
- Sleep patterns and duration

## Features

- **On-demand Data Loading**: Each health metric is loaded separately for optimal performance
- **Interactive Visualizations**: Explore your health data through interactive charts and graphs
- **Flexible Date Filtering**: Analyze data for different time periods
- **Key Health Metrics**: View important statistics and trends for each health category

## Setup

1. Export your Apple Health data from your iPhone:
   - Open the Health app
   - Tap your profile picture
   - Select "Export All Health Data"
   - Save the exported zip file
   - Extract the zip file

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

3. Place your exported Apple Health data in the `apple_health_export` directory:
   - Copy `export.xml` to the `apple_health_export` directory
   - Copy the `electrocardiograms` folder (if any)
   - Copy the `workout-routes` folder (if any)

4. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Select a tab for the health metric you want to analyze:
   - ❤️ Heart: Heart rate patterns and variability
   - 🏃‍♂️ Activity: Steps and distance
   - 🏋️‍♂️ Workouts: Exercise sessions and calories
   - 😴 Sleep: Sleep patterns and duration

2. Use the sidebar to select your desired date range:
   - Quick selections available (7 days, 30 days, etc.)
   - Custom date range option

3. Click the "Load Data" button in each tab to view the visualizations

## Data Privacy

This application processes your health data locally on your computer. No data is sent to external servers or stored online.

## Requirements

- Python 3.9+
- Streamlit
- Pandas
- Plotly
- Other dependencies listed in `requirements.txt`

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use this project however you'd like.