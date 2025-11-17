"""File I/O utilities for reading CSV and Excel files"""
import pandas as pd


def read_file(file):
    """
    Read a CSV or Excel file and return a pandas DataFrame.
    
    Args:
        file: File object from Streamlit file uploader
        
    Returns:
        pd.DataFrame: Loaded data
    """
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)


def read_file_from_path(file_path):
    """
    Read a CSV or Excel file from a file path and return a pandas DataFrame.
    
    Args:
        file_path: Path to the file
        
    Returns:
        pd.DataFrame: Loaded data
    """
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    else:
        return pd.read_excel(file_path)
