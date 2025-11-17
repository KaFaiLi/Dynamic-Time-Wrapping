"""DTW Batch Folder Comparison page"""
import streamlit as st
import pandas as pd
import numpy as np
import os
import itertools
import io
from src.utils.file_io import read_file_from_path
from src.utils.preprocessing import (
    add_datetime,
    remove_outliers_iqr_multicol,
    normalize_multiple_arrays,
    align_lengths
)
from src.utils.dtw import dtw_distance_multivariate
from src.utils.visualization import plot_heatmap, compute_ranking


def render():
    """Render the batch folder comparison page"""
    st.title("DTW Batch Folder Comparison")
    st.header("Compare all files in a folder using DTW")
    
    # 1. Folder input
    folder_path = st.text_input("Enter the path to a folder containing CSV/Excel files:")
    
    if folder_path and os.path.isdir(folder_path):
        # List all CSV/Excel files
        files = [f for f in os.listdir(folder_path) if f.endswith(('.csv', '.xlsx'))]
        
        if len(files) < 2:
            st.warning("The folder must contain at least two CSV or Excel files.")
        else:
            st.write(f"Found {len(files)} files:")
            st.write(files)
            
            # --- 2. Read all files into dataframes
            dfs = {}
            for fname in files:
                fpath = os.path.join(folder_path, fname)
                dfs[fname] = read_file_from_path(fpath)
            
            # --- 3. Select date/time columns (must exist in all files)
            all_columns = [set(df.columns) for df in dfs.values()]
            common_cols = set.intersection(*all_columns)
            
            if not common_cols:
                st.error("No common columns found across all files.")
            else:
                st.header("Step 2: Select Date/Time Columns (must exist in all files)")
                date_col = st.selectbox("Date column", list(common_cols), key="batch_date")
                time_options = ["None"] + list(common_cols)
                time_col = st.selectbox("Time column (optional)", time_options, key="batch_time")
                
                # --- 4. Select columns to compare for each file
                st.header("Step 3: Select Columns to Compare for Each File")
                selected_columns = {}
                for fname in files:
                    st.subheader(f"Columns for {fname}")
                    selected_columns[fname] = st.multiselect(
                        f"Select columns for {fname}",
                        list(dfs[fname].columns),
                        key=f"cols_{fname}"
                    )
                
                run = st.button("Run Batch DTW Comparison")
                
                if run:
                    # Check that all files have same number of columns selected
                    n_cols_set = set(len(cols) for cols in selected_columns.values())
                    
                    if 0 in n_cols_set:
                        st.info("Please select at least one column for every file.")
                    elif len(n_cols_set) > 1:
                        st.warning("Please select the same number of columns for every file (order matters for multivariate DTW).")
                    else:
                        # 5. Preprocess all dataframes
                        processed = {}
                        for fname in files:
                            df = dfs[fname]
                            cols = selected_columns[fname]
                            df = add_datetime(df, date_col, time_col)
                            df_clean = remove_outliers_iqr_multicol(df, cols)
                            arr = df_clean[cols].values
                            processed[fname] = arr
                        
                        # --- 6. Normalize all arrays together if multivariate
                        n_cols = list(n_cols_set)[0]
                        if n_cols > 1:
                            processed = normalize_multiple_arrays(processed)
                        
                        # --- 7. Compute pairwise DTW distances with progress bar
                        results = []
                        dist_matrix = np.zeros((len(files), len(files)))
                        pairs = list(itertools.combinations(range(len(files)), 2))
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        total = len(pairs)
                        
                        for idx, (i, j) in enumerate(pairs):
                            f1, f2 = files[i], files[j]
                            x, y = processed[f1], processed[f2]
                            
                            min_len = min(len(x), len(y))
                            if min_len == 0:
                                dist = np.nan
                            else:
                                x_, y_ = align_lengths(x, y)
                                dist = dtw_distance_multivariate(x_, y_)
                            
                            results.append({'File 1': f1, 'File 2': f2, 'DTW Distance': dist})
                            dist_matrix[i, j] = dist
                            dist_matrix[j, i] = dist
                            
                            # Update progress bar
                            progress = (idx + 1) / total
                            progress_bar.progress(progress)
                            status_text.text(f"Comparing: {f1} vs {f2} ({idx + 1}/{total})")
                        
                        progress_bar.empty()
                        status_text.empty()
                        
                        # --- 8. Compute ranking
                        ranking = compute_ranking(dist_matrix, files)
                        
                        # --- 9. Display results
                        st.subheader("Pairwise DTW Distances")
                        pairwise_df = pd.DataFrame(results)
                        st.dataframe(pairwise_df)
                        
                        st.subheader("File Ranking (most different at top)")
                        ranking_df = pd.DataFrame(ranking, columns=["File", "Mean DTW Distance"])
                        st.dataframe(ranking_df)
                        
                        st.subheader("Pairwise Distance Heatmap")
                        fig = plot_heatmap(dist_matrix, files, "DTW Distance Matrix")
                        st.pyplot(fig)
                        
                        # --- Download options
                        # Download Pairwise DTW Distances as Excel
                        excel_buffer1 = io.BytesIO()
                        with pd.ExcelWriter(excel_buffer1, engine='xlsxwriter') as writer:
                            pairwise_df.to_excel(writer, index=False, sheet_name='Pairwise_DTW_Distances')
                        excel_buffer1.seek(0)
                        
                        st.download_button(
                            label="Download Pairwise DTW Distances (Excel)",
                            data=excel_buffer1,
                            file_name="pairwise_dtw_distances.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                        # Download File Ranking as Excel
                        excel_buffer2 = io.BytesIO()
                        with pd.ExcelWriter(excel_buffer2, engine='xlsxwriter') as writer:
                            ranking_df.to_excel(writer, index=False, sheet_name='File_Ranking')
                        excel_buffer2.seek(0)
                        
                        st.download_button(
                            label="Download File Ranking (Excel)",
                            data=excel_buffer2,
                            file_name="file_ranking.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                        # Download Heatmap as PNG
                        img_buffer = io.BytesIO()
                        fig.savefig(img_buffer, format='png', bbox_inches='tight')
                        img_buffer.seek(0)
                        
                        st.download_button(
                            label="Download Heatmap (PNG)",
                            data=img_buffer,
                            file_name="dtw_heatmap.png",
                            mime="image/png"
                        )
    else:
        st.info("Please enter a valid folder path containing at least two CSV/Excel files.")
