# DTW Comparison Tool - AI Agent Instructions

## Project Overview
A Streamlit web application for comparing time series data using Dynamic Time Warping (DTW) algorithm. The tool supports univariate and multivariate time series comparison with three main workflows: single pairwise comparison, batch folder comparison, and within-file column comparison.

## Architecture & Key Components

### Single-File Structure
The entire application lives in `app.py` with three distinct page modes:
1. **DTW Comparison**: Upload 2 files, compare selected columns between them
2. **DTW Batch Folder Comparison**: Process entire folder of CSV/Excel files pairwise
3. **Single File Pairwise Comparison**: Compare columns within one file

### Data Flow Pattern
All three modes follow this pipeline:
1. File reading (CSV/Excel support via pandas)
2. Datetime combination (date + optional time columns → single 'Datetime' column)
3. IQR-based outlier removal per column
4. Length alignment (truncate to minimum length)
5. Normalization (for multivariate: combined mean/std across both datasets)
6. DTW distance computation
7. Visualization + ranking

### DTW Implementation
Pure Python/NumPy implementation in `dtw_distance_multivariate()` function:
- Uses dynamic programming with cost matrix
- Multivariate support via `np.linalg.norm()` for vector distances
- Returns cumulative distance from `dtw_matrix[n, m]`
- Same algorithm duplicated in batch and single-file modes (consider DRY refactoring)

## Critical Patterns & Conventions

### Outlier Removal Strategy
**IQR method** (Q1 - 1.5×IQR to Q3 + 1.5×IQR):
- `remove_outliers_iqr_multicol()`: Applies mask across all selected columns (intersection)
- `remove_outliers_iqr()`: Single column variant (used in single-file mode)
- Always applied **before** length alignment and normalization

### Normalization Logic
**Context-dependent normalization:**
- Univariate (1 column): No normalization (raw values compared)
- Multivariate (2+ columns): Z-score normalization using combined statistics from both datasets
- In batch mode: All files normalized together using global mean/std (see line ~450: `all_data = np.vstack(...)`)

### Length Alignment
Always truncates to `min(len(x), len(y))` **after** outlier removal. This means datasets with more outliers will contribute less data to the final comparison.

### File Handling
- Supports `.csv` (via `pd.read_csv`) and `.xlsx` (via `pd.read_excel`)
- Date parsing uses `pd.to_datetime(..., errors='coerce')` to handle malformed dates gracefully
- Batch mode expects common columns across all files (uses `set.intersection()`)

## Development Workflows

### Running the App
```bash
streamlit run app.py
```
Launches on default port (8501). Terminal shows in VS Code workspace context.

### Testing Different Modes
No automated tests exist. Manual testing approach:
1. **DTW Comparison**: Use 2 files from `Input/` with different stock columns
2. **Batch Mode**: Point to `Input/` folder, select common columns (Date, any stock tickers)
3. **Single File**: Use `Input/daily_stock_prices.csv`, compare stock columns like NVDA vs TSLA

### Common Debugging Points
- **Empty results after outlier removal**: Check IQR bounds with sample data; very skewed distributions may over-filter
- **NaN DTW distances**: Occurs when `min_len == 0` after outlier removal (handled in batch mode, line ~437)
- **Normalization issues**: Verify `stds != 0` check is working (division by zero protection)

## Data Structure Expectations

### Input CSV Format (see `Input/daily_stock_prices.csv`)
- **Date column**: String parseable by pandas (e.g., "2010-01-04")
- **Numeric columns**: Stock prices or any continuous time series data
- **Missing values**: Empty cells handled via pandas `.dropna()` or NaN propagation

### Column Selection Requirements
- DTW Comparison: Same number of columns from each file (order matters for multivariate)
- Batch Folder: All files must have same number of selected columns
- Single File: At least 2 columns for pairwise comparison

## Output & Results Interpretation

### DTW Distance Scale
- **Lower values**: More similar temporal patterns (after alignment)
- **No universal threshold**: Use for relative comparison within dataset
- **Influenced by**: Normalization choice, outlier removal, series length

### Ranking Logic
Mean DTW distance to all other entities (files or columns), excluding self-comparison:
```python
mean_dist = np.nanmean(np.where(dist_matrix == 0, np.nan, dist_matrix), axis=1)
```
Higher mean = more different from others (potential outlier)

### Export Features
Batch and single-file modes support downloads:
- Pairwise distance table (Excel via `xlsxwriter`)
- Ranking table (Excel)
- Heatmap visualization (PNG via `matplotlib.savefig`)

## Known Limitations & Design Decisions

### Why Pure Python DTW?
No external DTW library dependency (like `fastdtw` or `dtaidistance`). Keeps dependencies minimal but trades performance for simplicity. For large datasets (>10k points), consider adding library option.

### Code Duplication
DTW implementation appears in 3 places:
1. `dtw_distance_multivariate()` (main comparison, batch)
2. `dtw_distance()` univariate variant (single-file mode)
Refactor opportunity: Extract to shared utility function.

### Progress Bars
Only batch mode shows progress (lines ~432-448). Consider adding to single-file pairwise for consistency with multiple comparisons.

### Memory Considerations
Batch mode loads all files into memory (`dfs` dict). For large folders with massive CSV files, may hit memory limits. No streaming/chunking implemented.

## Dependencies
Key libraries used:
- `streamlit`: Web UI framework
- `pandas`: Data manipulation, CSV/Excel I/O
- `numpy`: Numerical operations, DTW matrix
- `matplotlib`: Plotting time series overlays
- `seaborn`: Heatmap visualization
- `xlsxwriter` (via pandas): Excel export with formatting

## Future Extension Points
- Add configurable IQR multiplier (currently hardcoded 1.5)
- Support for different distance metrics in DTW (currently Euclidean for multivariate)
- Implement Sakoe-Chiba band or Itakura parallelogram constraints for faster DTW
- Add statistical significance testing (permutation tests)
- Support for irregular time series (interpolation before DTW)
