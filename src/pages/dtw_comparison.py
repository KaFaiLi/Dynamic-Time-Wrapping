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
    st.markdown('<h1 class="main-header">📝 DTW Comparison</h1>', unsafe_allow_html=True)
    st.markdown("### Compare two time series datasets using Dynamic Time Warping")
    st.markdown("---")
    
    # --- 1. File upload ---
    st.markdown('<div class="step-header">📤 Step 1: Upload Your Files</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        file1 = st.file_uploader("📄 First Dataset", type=["csv", "xlsx"], key="file1", help="Upload your first time series file")
    with col2:
        file2 = st.file_uploader("📄 Second Dataset", type=["csv", "xlsx"], key="file2", help="Upload your second time series file")
    
    if file1 and file2:
        df1 = read_file(file1)
        df2 = read_file(file2)
        
        st.success(f"✅ Files loaded successfully! ({len(df1)} rows in File 1, {len(df2)} rows in File 2)")
        
        st.markdown("---")
        st.markdown('<div class="step-header">📅 Step 2: Configure Date/Time Columns</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**First Dataset**")
            date_col1 = st.selectbox("📅 Date column", df1.columns, index=0, key="date1")
            time_options1 = ["None"] + list(df1.columns)
            time_col1 = st.selectbox("🕐 Time column (optional)", time_options1, index=0, key="time1")
        
        with col2:
            st.markdown("**Second Dataset**")
            date_col2 = st.selectbox("📅 Date column", df2.columns, index=0, key="date2")
            time_options2 = ["None"] + list(df2.columns)
            time_col2 = st.selectbox("🕐 Time column (optional)", time_options2, index=0, key="time2")
        
        # --- Select columns to compare ---
        st.markdown("---")
        st.markdown('<div class="step-header">🎯 Step 3: Select Columns to Compare</div>', unsafe_allow_html=True)
        st.info("💡 Select the same number of columns from each file. For multivariate comparison, order matters!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**First Dataset Columns**")
            cols1 = st.multiselect("Select columns", list(df1.columns), key="cols1", help="Choose numerical columns to compare")
        with col2:
            st.markdown("**Second Dataset Columns**")
            cols2 = st.multiselect("Select columns", list(df2.columns), key="cols2", help="Choose numerical columns to compare")
        
        st.markdown("---")
        run = st.button("🚀 Run DTW Comparison", type="primary", use_container_width=True)
        
        if run:
            if not cols1 or not cols2:
                st.warning("⚠️ Please select at least one column from each file to compare.")
            elif len(cols1) != len(cols2):
                st.error("❌ Please select the same number of columns from each file for comparison.")
            else:
                with st.spinner('🔄 Processing data and computing DTW distance...'):
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
                st.markdown("---")
                st.markdown("## 📊 Results")
                
                # Display DTW distance in a nice metric box
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.metric(
                        label=f"DTW Distance ({', '.join(cols1)} vs {', '.join(cols2)})",
                        value=f"{distance:.3f}",
                        help="Lower values indicate more similar time series patterns"
                    )
                
                st.markdown("---")
                
                # Visualize
                st.markdown("### 📈 Time Series Visualization")
                st.caption("Showing cleaned and normalized data (if multivariate)")
                title = f'Comparison: {", ".join(cols1)} (File 1) vs {", ".join(cols2)} (File 2)'
                fig = plot_time_series_comparison(x, y, cols1, cols2, title)
                st.pyplot(fig)
                
                # Show data preview in expandable section
                with st.expander("🔍 View Cleaned Data Preview (First 5 Rows)", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Dataset 1**")
                        st.dataframe(df1_clean.head(), use_container_width=True)
                    with col2:
                        st.markdown("**Dataset 2**")
                        st.dataframe(df2_clean.head(), use_container_width=True)
                
                # Show processing info
                with st.expander("ℹ️ Processing Information"):
                    st.markdown(f"""
                    - **Original rows:** File 1: {len(df1)}, File 2: {len(df2)}
                    - **After outlier removal:** File 1: {len(df1_clean)}, File 2: {len(df2_clean)}
                    - **Final aligned length:** {len(x)} data points
                    - **Comparison type:** {'Multivariate (normalized)' if len(cols1) > 1 else 'Univariate (raw values)'}
                    - **Columns compared:** {len(cols1)}
                    """)
    else:
        st.info("👆 Please upload both CSV or Excel files to begin the analysis.")
