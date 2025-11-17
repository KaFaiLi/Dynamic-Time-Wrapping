# DTW Comparison Tool - Code Structure

## Project Structure

The project has been refactored into a modern, modular architecture:

```
.
├── app.py                          # Entry point for Streamlit application
├── app_old.py                      # Original monolithic version (backup)
├── Input/                          # Sample data files
│   └── daily_stock_prices.csv
└── src/                            # Source code organized by functionality
    ├── __init__.py
    ├── config.py                   # Centralized configuration
    ├── pages/                      # Page modules for different workflows
    │   ├── __init__.py
    │   ├── home.py                 # Home page with documentation
    │   ├── dtw_comparison.py       # Two-file comparison workflow
    │   ├── batch_comparison.py     # Batch folder comparison workflow
    │   └── single_file_comparison.py  # Single-file pairwise comparison
    └── utils/                      # Reusable utility modules
        ├── __init__.py
        ├── file_io.py              # File reading utilities
        ├── preprocessing.py        # Data cleaning and preparation
        ├── dtw.py                  # DTW algorithm implementations
        └── visualization.py        # Plotting and ranking functions
```

## Module Descriptions

### Entry Point
- **`app.py`**: Minimal entry point that configures Streamlit and routes to appropriate pages

### Configuration
- **`src/config.py`**: Centralized settings for page config, supported file types, and algorithm parameters

### Pages (`src/pages/`)
Each page module has a `render()` function that handles the UI and workflow:
- **`home.py`**: Welcome page with tool documentation
- **`dtw_comparison.py`**: Upload two files and compare selected columns
- **`batch_comparison.py`**: Compare all files in a folder pairwise
- **`single_file_comparison.py`**: Compare columns within a single file pairwise

### Utilities (`src/utils/`)
Reusable functions organized by purpose:

#### `file_io.py`
- `read_file()`: Read CSV/Excel from file uploader
- `read_file_from_path()`: Read CSV/Excel from file path

#### `preprocessing.py`
- `add_datetime()`: Combine date and time columns
- `remove_outliers_iqr_multicol()`: IQR-based outlier removal for multiple columns
- `remove_outliers_iqr()`: IQR-based outlier removal for single column
- `normalize_data()`: Z-score normalization for two datasets
- `normalize_multiple_arrays()`: Normalize multiple datasets together
- `align_lengths()`: Truncate arrays to minimum length

#### `dtw.py`
- `dtw_distance_multivariate()`: DTW for multivariate time series (uses Euclidean distance)
- `dtw_distance()`: DTW for univariate time series

#### `visualization.py`
- `plot_time_series_comparison()`: Plot two time series overlays
- `plot_single_comparison()`: Plot single pairwise comparison
- `plot_heatmap()`: Create DTW distance heatmap
- `compute_ranking()`: Calculate mean DTW distance rankings

## Running the Application

From the project root directory:

```bash
streamlit run app.py
```

The application will start on http://localhost:8501

## Benefits of New Structure

1. **Separation of Concerns**: Pages, utilities, and configuration are clearly separated
2. **Reusability**: Utility functions can be easily tested and reused
3. **Maintainability**: Changes to DTW algorithm only require editing `src/utils/dtw.py`
4. **Scalability**: Easy to add new pages or utility functions
5. **Code Organization**: Related functionality is grouped together
6. **Testing**: Utility modules can be unit tested independently
7. **Clean Entry Point**: `app.py` is minimal and focused on routing

## Migration Notes

- Original monolithic code backed up as `app_old.py`
- All functionality preserved - no features removed
- DTW algorithm implementations consolidated (previously duplicated across pages)
- Preprocessing and visualization logic now shared across all pages
