# 🍎 Apple Health Data Explorer

A powerful tool to analyze and visualize your Apple Health data with interactive dashboards and comprehensive insights.

![image](https://github.com/user-attachments/assets/0c98b7d5-9ccb-4066-8d6d-9005e6548a08)


## ✨ Features

### 📊 Interactive Dashboards
- **Heart & Fitness**
  - Heart rate patterns and variability
  - VO2 max trends
  - Resting heart rate analysis
  - Walking heart rate averages

- **Activity Tracking**
  - Step count visualization
  - Distance (walking, running, cycling)
  - Active energy burned
  - Exercise and stand time
  - Flights climbed

- **Workout Analysis**
  - Workout type distribution
  - Duration and calorie tracking
  - Distance and energy metrics
  - Historical workout patterns

- **Sleep Insights**
  - Sleep duration tracking
  - Sleep pattern analysis
  - Quality metrics visualization

- **Body Metrics**
  - Weight tracking
  - BMI calculations
  - Body measurements
  - Trend analysis with trendlines

- **Vital Signs**
  - Blood oxygen levels
  - Respiratory rate tracking

- **Nutrition Tracking**
  - Water intake
  - Caffeine consumption
  - Comprehensive dietary metrics
  - Macro and micronutrient analysis

- **Environmental Monitoring**
  - Audio exposure levels
  - Time in daylight tracking

### 🔍 Advanced Features
- **Smart Data Processing**
  - Efficient preprocessing of large health datasets
  - Timezone-aware data handling
  - Source normalization (merges similar sources like "iPhone" variations)
  - Batch processing for optimal performance

- **Comprehensive Insights**
  - Cross-metric correlation analysis
  - Pattern detection
  - Health trend identification
  - Activity impact analysis

- **Data Management**
  - CSV export functionality for all metrics
  - Flexible date range filtering
  - Source-based filtering
  - Data integrity checks

## 🚀 Getting Started

1. **Export Your Health Data**
   - Open the Health app on your iPhone
   - Tap your profile picture
   - Select "Export All Health Data"
   - Save the exported zip file

2. **Setup**
   ```bash
   # Clone the repository
   git clone https://github.com/d4rk-lucif3r/Apple-Health-Data-Explorer.git
   cd apple-health-explorer

   # Install dependencies
   pip install -r requirements.txt

   # Extract your health data
   # Place the export.xml file in the apple_health_export directory

   # Preprocess the data
   python preprocess_health_data.py
   ```

3. **Run the Application**
   ```bash
   # Start the Streamlit app
   streamlit run app.py
   ```

4. ** Or Just do
   ```bash
   python main.py
   ```

## 📱 Data Sources
The application supports data from various sources:
- Apple Watch
- iPhone
- Third-party health apps

All similar source names (e.g., different iPhone variations) are automatically normalized during preprocessing for better organization.

## 🔄 Data Processing
- Preprocessing handles timezone conversion
- Efficient batch processing of large datasets
- Source name normalization for cleaner data organization
- Automatic metadata generation and tracking

## 📈 Visualization Features
- Interactive time-series plots
- Distribution charts
- Correlation analysis
- Trend identification
- Custom date range analysis
- Source-based filtering

## 🛠 Technical Details
- Built with Python, Pandas, and Streamlit
- Interactive visualizations using Plotly
- Efficient XML parsing and data processing
- Modular architecture for easy maintenance
- Comprehensive error handling and data validation

## 📝 Notes
- All dates are stored in timezone-naive format for consistent analysis
- Data is preprocessed for optimal performance
- Regular backups of your health data are recommended
- The app respects data privacy and processes all data locally

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
