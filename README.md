# 📊 DTW Comparison Tool

A powerful Streamlit web application for comparing time series data using Dynamic Time Warping (DTW) algorithm. This tool supports both univariate and multivariate time series comparison with three main workflows: single pairwise comparison, batch folder comparison, and within-file column comparison.

## ✨ Features

- **🔍 Dynamic Time Warping**: Advanced algorithm that measures similarity between time series, handling:
  - Phase shifts and temporal misalignments
  - Different operating speeds
  - Minor distortions in patterns

- **📈 Multiple Analysis Modes**:
  - **DTW Comparison**: Compare two time series files column-by-column
  - **Batch Folder Comparison**: Process entire folders of CSV/Excel files pairwise
  - **Single File Pairwise Comparison**: Compare multiple columns within a single file

- **🧹 Data Preprocessing**:
  - Automatic IQR-based outlier detection and removal
  - Smart normalization for multivariate time series
  - Datetime column combination support
  - Automatic length alignment

- **📊 Visualization**:
  - Interactive time series overlays
  - DTW distance heatmaps
  - Ranking visualizations
  - Exportable plots (PNG format)

- **💾 Export Capabilities**:
  - Download pairwise distance tables (Excel)
  - Download ranking tables (Excel)
  - Export heatmap visualizations (PNG)

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**:
```bash
git clone https://github.com/KaFaiLi/Dynamic-Time-Wrapping.git
cd Dynamic-Time-Wrapping
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`.

## 📖 Usage Guide

### DTW Comparison Mode

Compare two time series files:

1. Navigate to **DTW Comparison** from the sidebar
2. Upload two CSV or Excel files
3. Select date (and optionally time) columns
4. Choose numeric columns to compare (same number from each file)
5. Click **Run DTW Analysis**
6. View results including:
   - DTW distance metric
   - Time series overlay plots
   - Processing statistics

### Batch Folder Comparison Mode

Process multiple files at once:

1. Navigate to **DTW Batch Folder Comparison**
2. Enter the folder path containing your CSV/Excel files
3. Select date and numeric columns (must be common across all files)
4. Click **Run Batch Comparison**
5. View and download:
   - Pairwise distance matrix
   - DTW distance heatmap
   - Ranking table (sorted by mean distance)

### Single File Pairwise Comparison Mode

Compare columns within one file:

1. Navigate to **Single File Pairwise Comparison**
2. Upload a CSV or Excel file
3. Select date column
4. Choose multiple numeric columns to compare
5. Click **Run Pairwise Comparison**
6. Analyze results with heatmap and rankings

## 📁 Project Structure

```
Dynamic-Time-Wrapping/
├── app.py                          # Main entry point
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── Input/                          # Sample data directory
│   └── daily_stock_prices.csv     # Example dataset
└── src/                            # Source code
    ├── config.py                   # Configuration settings
    ├── pages/                      # Page modules
    │   ├── home.py                 # Home/documentation page
    │   ├── dtw_comparison.py       # Two-file comparison
    │   ├── batch_comparison.py     # Batch processing
    │   └── single_file_comparison.py  # Single-file analysis
    └── utils/                      # Utility modules
        ├── file_io.py              # File reading
        ├── preprocessing.py        # Data cleaning
        ├── dtw.py                  # DTW algorithms
        └── visualization.py        # Plotting functions
```

## 🎯 Use Cases

- **Financial Analysis**: Compare stock price patterns across different securities
- **Sensor Data**: Analyze similarity in IoT sensor readings
- **Healthcare**: Compare patient vitals or medical signal patterns
- **Quality Control**: Detect anomalies in manufacturing time series
- **Climate Studies**: Compare weather or environmental patterns

## 🔧 Algorithm Details

### DTW Distance Calculation

The tool implements a pure Python/NumPy DTW algorithm using dynamic programming:
- Computes cumulative distance matrix
- Supports both univariate and multivariate time series
- Uses Euclidean distance for multivariate comparisons

### Preprocessing Pipeline

1. **Datetime Combination**: Merges separate date and time columns
2. **Outlier Removal**: IQR method (Q1 - 1.5×IQR to Q3 + 1.5×IQR)
3. **Length Alignment**: Truncates to minimum length across datasets
4. **Normalization**: Z-score normalization for multivariate data (optional for univariate)

## 📊 Sample Data

The repository includes sample stock price data in `Input/daily_stock_prices.csv` containing:
- Date column
- Multiple stock ticker columns (e.g., AAPL, GOOGL, MSFT, TSLA, NVDA)
- Daily closing prices

Try the sample data to explore the tool's capabilities!

## 🛠️ Configuration

You can customize the tool's behavior by modifying `src/config.py`:

```python
IQR_MULTIPLIER = 1.5          # Outlier removal sensitivity
SUPPORTED_FILE_TYPES = ["csv", "xlsx"]  # File format support
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, fork the repository, and create pull requests.

## 📝 License

This project is open source and available under the MIT License.

## 🔗 Resources

- [Dynamic Time Warping (Wikipedia)](https://en.wikipedia.org/wiki/Dynamic_time_warping)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [DTW Algorithm Overview](https://rtavenar.github.io/blog/dtw.html)

## ⚠️ Notes

- **File Requirements**: CSV/Excel files must have a date column and at least one numeric column
- **Performance**: For large datasets (>10,000 points), processing may take longer
- **Memory**: Batch mode loads all files into memory; consider system resources for large folders
- **Common Columns**: Batch mode requires all files to share the selected column names

## 📧 Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.

---

Made with ❤️ using Streamlit and Python
