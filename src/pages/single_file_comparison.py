"""Single File Pairwise Comparison page"""
import streamlit as st
import pandas as pd
import numpy as np
import itertools
from src.utils.file_io import read_file
from src.utils.preprocessing import add_datetime, remove_outliers_iqr
from src.utils.dtw import dtw_distance
from src.utils.visualization import plot_single_comparison, plot_heatmap, compute_ranking


def render():
    """Render the single file pairwise comparison page"""
    st.title("Single File: Pairwise DTW Comparison")
    st.header("Upload one file and compare selected columns 2 by 2")
    
    # 1. File upload
    uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"], key="single_file")
    
    if uploaded_file:
        # Read file
        df = read_file(uploaded_file)
        
        st.write("Preview of uploaded data:")
        st.dataframe(df.head())
        
        # 2. Select date/time columns (optional)
        date_col = st.selectbox("Date column (optional)", ["None"] + list(df.columns), index=0, key="single_date")
        time_col = st.selectbox("Time column (optional)", ["None"] + list(df.columns), index=0, key="single_time")
        
        # 3. Select columns to compare
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            st.warning("No numeric columns found for comparison.")
        else:
            selected_cols = st.multiselect(
                "Select columns to compare pairwise (at least 2)",
                numeric_cols,
                key="single_cols"
            )
            
            if len(selected_cols) < 2:
                st.info("Please select at least two columns.")
            else:
                run = st.button("Run Pairwise DTW Comparison")
                
                if run:
                    # Add Datetime if needed
                    if date_col != "None":
                        df = add_datetime(df, date_col, time_col)
                        df = df.sort_values('Datetime')
                    
                    # Prepare results and distance matrix
                    results = []
                    pairs = list(itertools.combinations(selected_cols, 2))
                    n = len(selected_cols)
                    dist_matrix = np.zeros((n, n))
                    
                    st.write(f"Comparing {len(pairs)} pairs:")
                    
                    for idx, (col1, col2) in enumerate(pairs):
                        # Remove outliers independently
                        s1 = remove_outliers_iqr(df[col1].dropna())
                        s2 = remove_outliers_iqr(df[col2].dropna())
                        
                        # Align lengths
                        min_len = min(len(s1), len(s2))
                        s1 = s1.iloc[:min_len].values
                        s2 = s2.iloc[:min_len].values
                        
                        # Normalize
                        mean = np.mean(np.concatenate([s1, s2]))
                        std = np.std(np.concatenate([s1, s2]))
                        std = std if std != 0 else 1
                        s1 = (s1 - mean) / std
                        s2 = (s2 - mean) / std
                        
                        # DTW
                        dist = dtw_distance(s1, s2)
                        results.append({
                            "Column 1": col1,
                            "Column 2": col2,
                            "DTW Distance": dist
                        })
                        
                        # Fill symmetric matrix
                        i = selected_cols.index(col1)
                        j = selected_cols.index(col2)
                        dist_matrix[i, j] = dist
                        dist_matrix[j, i] = dist
                        
                        # Plot
                        st.subheader(f"DTW: {col1} vs {col2} (Distance: {dist:.3f})")
                        fig = plot_single_comparison(s1, s2, col1, col2, dist)
                        st.pyplot(fig)
                    
                    # Show results table
                    st.subheader("Pairwise DTW Distances")
                    st.dataframe(pd.DataFrame(results))
                    
                    # Compute ranking
                    ranking = compute_ranking(dist_matrix, selected_cols)
                    
                    st.subheader("Column Ranking by Mean DTW Distance (most different at top)")
                    st.dataframe(pd.DataFrame(ranking, columns=["Column", "Mean DTW Distance"]))
                    
                    # Show heatmap
                    st.subheader("Pairwise Distance Heatmap")
                    fig = plot_heatmap(dist_matrix, selected_cols, "DTW Distance Matrix")
                    st.pyplot(fig)
    else:
        st.info("Please upload a file to begin.")
