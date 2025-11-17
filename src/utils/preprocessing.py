"""Data preprocessing utilities including datetime handling and outlier removal"""
import pandas as pd
import numpy as np
from src.config import IQR_MULTIPLIER


def add_datetime(df, date_col, time_col):
    """
    Combine date and optional time columns into a single datetime column.
    
    Args:
        df: DataFrame containing the data
        date_col: Name of the date column
        time_col: Name of the time column or "None" if not applicable
        
    Returns:
        pd.DataFrame: DataFrame with added 'Datetime' column, sorted by datetime
    """
    if time_col == "None":
        df['Datetime'] = pd.to_datetime(df[date_col].astype(str), errors='coerce')
    else:
        df['Datetime'] = pd.to_datetime(
            df[date_col].astype(str) + " " + df[time_col].astype(str),
            errors='coerce'
        )
    df = df.sort_values('Datetime')
    return df


def remove_outliers_iqr_multicol(df, columns):
    """
    Remove outliers from multiple columns using IQR method.
    
    Args:
        df: DataFrame containing the data
        columns: List of column names to check for outliers
        
    Returns:
        pd.DataFrame: DataFrame with outliers removed
    """
    mask = pd.Series(True, index=df.index)
    for col in columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - IQR_MULTIPLIER * IQR
        upper_bound = Q3 + IQR_MULTIPLIER * IQR
        mask &= (df[col] >= lower_bound) & (df[col] <= upper_bound)
    return df[mask].reset_index(drop=True)


def remove_outliers_iqr(series):
    """
    Remove outliers from a single series using IQR method.
    
    Args:
        series: pandas Series to clean
        
    Returns:
        pd.Series: Series with outliers removed
    """
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - IQR_MULTIPLIER * IQR
    upper = Q3 + IQR_MULTIPLIER * IQR
    return series[(series >= lower) & (series <= upper)]


def normalize_data(x, y):
    """
    Normalize two datasets using combined statistics (z-score normalization).
    
    Args:
        x: First numpy array (can be 1D or 2D)
        y: Second numpy array (can be 1D or 2D)
        
    Returns:
        tuple: (normalized_x, normalized_y)
    """
    combined = np.vstack([x, y])
    means = combined.mean(axis=0)
    stds = combined.std(axis=0)
    stds[stds == 0] = 1  # Avoid division by zero
    x_norm = (x - means) / stds
    y_norm = (y - means) / stds
    return x_norm, y_norm


def normalize_multiple_arrays(arrays):
    """
    Normalize multiple arrays together using combined statistics.
    
    Args:
        arrays: Dictionary of {name: numpy_array}
        
    Returns:
        dict: Dictionary of {name: normalized_array}
    """
    all_data = np.vstack([arr for arr in arrays.values() if len(arr) > 0])
    means = all_data.mean(axis=0)
    stds = all_data.std(axis=0)
    stds[stds == 0] = 1
    
    normalized = {}
    for name, arr in arrays.items():
        if len(arr) > 0:
            normalized[name] = (arr - means) / stds
        else:
            normalized[name] = arr
    
    return normalized


def align_lengths(x, y):
    """
    Truncate arrays to minimum length for fair comparison.
    
    Args:
        x: First numpy array
        y: Second numpy array
        
    Returns:
        tuple: (truncated_x, truncated_y)
    """
    min_len = min(len(x), len(y))
    return x[:min_len], y[:min_len]
