"""Home page module"""
import streamlit as st


def render():
    """Render the home page"""
    st.title("DTW Comparison Tool")
    st.header("What is this tool?")
    st.markdown("""
    This tool allows you to compare the similarity between time series datasets using **Dynamic Time Warping (DTW)**.
    DTW is a robust algorithm that measures the similarity between two sequences, even if they are out of phase or have different speeds.
    """)
    
    st.header("How to use it?")
    st.markdown("""
    The tool provides three main functionalities, accessible via the sidebar:
    
    1. **DTW Comparison**
       - Compare two individual datasets (CSV or Excel files).
       - Upload your files, select the relevant columns, and compute the DTW distance and visualizations.
    
    2. **DTW Batch Folder Comparison**
       - Compare all files in a folder (CSV or Excel) in a pairwise fashion.
       - Enter the folder path, select columns, and the tool will compute the DTW distance for every pair of files.
       - Files are then ranked by how different they are from the others, and a heatmap of all pairwise distances is displayed.
    
    3. **Single File Pairwise Comparison**
       - Compare columns within a single file in a pairwise fashion.
       - Upload one file, select columns to compare, and view pairwise DTW distances with rankings.
    """)
    
    st.header("How to interpret the results?")
    st.markdown("""
    - The **DTW distance** quantifies the similarity between your time series:
      - **Lower DTW score**: The series are more similar in shape and pattern.
      - **Higher DTW score**: The series are less similar.
    - The tool removes outliers and normalizes data (if multivariate) for fair comparison.
    - Use the plots to visually inspect how the series align after cleaning and normalization.
    - In the batch mode, use the ranking and heatmap to identify files that are outliers or most different from the rest.
    - There is no universal "good" or "bad" DTW score; use it for **relative comparison** between different pairs or periods.
    """)
    
    st.info("Ready? Use the sidebar to select either 'DTW Comparison' for two files, 'DTW Batch Folder Comparison' for a folder of files, or 'Single File Pairwise Comparison' for comparing columns within one file.")
