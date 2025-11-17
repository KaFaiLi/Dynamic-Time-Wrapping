"""DTW Comparison page - compare two uploaded files"""
import streamlit as st
from src.utils.file_io import read_file
from src.utils.preprocessing import (
    add_datetime, 
    remove_outliers_iqr_multicol,
    normalize_data,
    align_lengths
)
from src.utils.dtw import dtw_distance_multivariate
from src.utils.visualization import plot_time_series_comparison


def render():
    """Render the DTW comparison page"""
    st.title("DTW Comparison: Upload and Analyze")
    
    # --- 1. File upload ---
    st.header("Step 1: Upload Your Files")
    file1 = st.file_uploader("Upload first CSV or Excel file", type=["csv", "xlsx"], key="file1")
    file2 = st.file_uploader("Upload second CSV or Excel file", type=["csv", "xlsx"], key="file2")
    
    if file1 and file2:
        df1 = read_file(file1)
        df2 = read_file(file2)
        
        st.header("Step 2: Select Date/Time Columns")
        date_col1 = st.selectbox("Date column in first file", df1.columns, index=0, key="date1")
        time_options1 = ["None"] + list(df1.columns)
        time_col1 = st.selectbox("Time column in first file (optional)", time_options1, index=0, key="time1")
        
        date_col2 = st.selectbox("Date column in second file", df2.columns, index=0, key="date2")
        time_options2 = ["None"] + list(df2.columns)
        time_col2 = st.selectbox("Time column in second file (optional)", time_options2, index=0, key="time2")
        
        # --- Select columns to compare ---
        st.header("Step 3: Select Columns to Compare")
        cols1 = st.multiselect("Select columns from first file", list(df1.columns), key="cols1")
        cols2 = st.multiselect("Select columns from second file", list(df2.columns), key="cols2")
        
        run = st.button("Run DTW Comparison")
        
        if run:
            if not cols1 or not cols2:
                st.info("Please select at least one column from each file to compare.")
            elif len(cols1) != len(cols2):
                st.warning("Please select the same number of columns from each file for comparison.")
            else:
                # --- Combine date and time columns ---
                df1 = add_datetime(df1, date_col1, time_col1)
                df2 = add_datetime(df2, date_col2, time_col2)
                
                # Only keep selected columns + Datetime
                df1 = df1[["Datetime"] + cols1]
                df2 = df2[["Datetime"] + cols2]
                
                # Remove outliers
                df1_clean = remove_outliers_iqr_multicol(df1, cols1)
                df2_clean = remove_outliers_iqr_multicol(df2, cols2)
                
                # Extract selected columns as numpy arrays
                x = df1_clean[cols1].values
                y = df2_clean[cols2].values
                
                # Align lengths
                x, y = align_lengths(x, y)
                
                # Normalize if multivariate
                if len(cols1) > 1:
                    x, y = normalize_data(x, y)
                
                # Compute DTW distance
                distance = dtw_distance_multivariate(x, y)
                
                # Display results
                st.subheader(f"DTW distance between datasets (columns: {', '.join(cols1)} vs {', '.join(cols2)}):")
                st.success(f"{distance:.3f}")
                
                # Visualize
                st.subheader("Time Series Comparison (Outliers Removed, Normalized if Multivariate)")
                title = f'Comparison of {", ".join(cols1)} (File 1) vs {", ".join(cols2)} (File 2)'
                fig = plot_time_series_comparison(x, y, cols1, cols2, title)
                st.pyplot(fig)
                
                # Show data preview
                st.subheader("Preview of Cleaned Data (First 5 Rows Each)")
                st.write("Dataset 1:")
                st.dataframe(df1_clean.head())
                st.write("Dataset 2:")
                st.dataframe(df2_clean.head())
    else:
        st.info("Please upload both files to begin.")
