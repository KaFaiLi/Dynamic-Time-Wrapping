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
    st.markdown('<h1 class="main-header">📊 Single File Column Comparison</h1>', unsafe_allow_html=True)
    st.markdown("### Analyze relationships between columns within a single dataset")
    st.markdown("---")
    
    # 1. File upload
    st.markdown('<div class="step-header">📤 Step 1: Upload Your File</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "📄 Upload Dataset", 
        type=["csv", "xlsx"], 
        key="single_file",
        help="Upload a CSV or Excel file containing multiple time series columns"
    )
    
    if uploaded_file:
        # Read file
        df = read_file(uploaded_file)
        
        st.success(f"✅ File loaded successfully! ({len(df)} rows, {len(df.columns)} columns)")
        
        with st.expander("🔍 Preview uploaded data", expanded=False):
            st.dataframe(df.head(10), use_container_width=True)
        
        st.markdown("---")
        
        # 2. Select date/time columns (optional)
        st.markdown('<div class="step-header">📅 Step 2: Configure Date/Time Columns (Optional)</div>', unsafe_allow_html=True)
        st.info("💡 If your data has temporal information, select the date/time columns for proper alignment.")
        
        col1, col2 = st.columns(2)
        with col1:
            date_col = st.selectbox("📅 Date column", ["None"] + list(df.columns), index=0, key="single_date")
        with col2:
            time_col = st.selectbox("🕐 Time column", ["None"] + list(df.columns), index=0, key="single_time")
        
        st.markdown("---")
        
        # 3. Select columns to compare
        st.markdown('<div class="step-header">🎯 Step 3: Select Columns to Compare</div>', unsafe_allow_html=True)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            st.error("❌ No numeric columns found for comparison. Please upload a file with numerical data.")
        else:
            st.info(f"💡 Found {len(numeric_cols)} numeric columns. Select at least 2 to compare pairwise.")
            
            selected_cols = st.multiselect(
                "Select columns for pairwise comparison",
                numeric_cols,
                key="single_cols",
                help="Choose numerical columns to compare with each other"
            )
            
            if len(selected_cols) >= 2:
                num_comparisons = len(list(itertools.combinations(selected_cols, 2)))
                st.caption(f"This will perform {num_comparisons} pairwise comparisons")
            
            if len(selected_cols) < 2:
                st.warning("⚠️ Please select at least two columns.")
            else:
                st.markdown("---")
                run = st.button("🚀 Run Pairwise DTW Comparison", type="primary", use_container_width=True)
                
                if run:
                    # Add Datetime if needed
                    if date_col != "None":
                        df = add_datetime(df, date_col, time_col)
                        df = df.sort_values('Datetime')
                    
                    # Prepare results and distance matrix
                    st.markdown("---")
                    st.markdown("## 🔄 Processing Comparisons")
                    
                    results = []
                    pairs = list(itertools.combinations(selected_cols, 2))
                    n = len(selected_cols)
                    dist_matrix = np.zeros((n, n))
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    total = len(pairs)
                    
                    # Container for individual comparisons
                    comparisons_container = st.container()
                    
                    for idx, (col1, col2) in enumerate(pairs):
                        status_text.text(f"📊 Comparing: `{col1}` vs `{col2}` ({idx + 1}/{total})")
                        
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
                        
                        # Update progress
                        progress_bar.progress((idx + 1) / total)
                    
                    progress_bar.empty()
                    status_text.empty()
                    st.success(f"✅ Completed {total} pairwise comparisons!")
                    
                    # Show results in tabs
                    st.markdown("---")
                    st.markdown("## 📊 Results")
                    
                    tab1, tab2, tab3, tab4 = st.tabs(["📋 Distance Table", "🏆 Column Ranking", "🗺️ Heatmap", "📈 Individual Plots"])
                    
                    with tab1:
                        st.markdown("### Pairwise DTW Distances")
                        st.caption("All pairwise comparisons between selected columns")
                        results_df = pd.DataFrame(results)
                        st.dataframe(results_df, use_container_width=True, height=400)
                    
                    with tab2:
                        # Compute ranking
                        ranking = compute_ranking(dist_matrix, selected_cols)
                        ranking_df = pd.DataFrame(ranking, columns=["Column", "Mean DTW Distance"])
                        
                        st.markdown("### Column Ranking by Dissimilarity")
                        st.caption("Columns ranked by mean DTW distance to all others (higher = more different)")
                        
                        st.dataframe(
                            ranking_df.style.background_gradient(subset=['Mean DTW Distance'], cmap='YlOrRd'),
                            use_container_width=True,
                            height=400
                        )
                        
                        st.info(f"🔍 **Most dissimilar column:** `{ranking_df.iloc[0]['Column']}` (Mean distance: {ranking_df.iloc[0]['Mean DTW Distance']:.3f})")
                        st.success(f"✅ **Most similar column:** `{ranking_df.iloc[-1]['Column']}` (Mean distance: {ranking_df.iloc[-1]['Mean DTW Distance']:.3f})")
                    
                    with tab3:
                        st.markdown("### Distance Matrix Heatmap")
                        st.caption("Visual representation of pairwise DTW distances")
                        
                        fig = plot_heatmap(dist_matrix, selected_cols, "DTW Distance Matrix")
                        st.pyplot(fig)
                    
                    with tab4:
                        st.markdown("### Individual Pairwise Comparisons")
                        st.caption("Detailed visualizations of each comparison")
                        
                        for idx, (col1, col2) in enumerate(pairs):
                            with st.expander(f"🔍 {col1} vs {col2} (Distance: {results[idx]['DTW Distance']:.3f})", expanded=False):
                                # Recompute for plotting
                                s1 = remove_outliers_iqr(df[col1].dropna())
                                s2 = remove_outliers_iqr(df[col2].dropna())
                                min_len = min(len(s1), len(s2))
                                s1 = s1.iloc[:min_len].values
                                s2 = s2.iloc[:min_len].values
                                mean = np.mean(np.concatenate([s1, s2]))
                                std = np.std(np.concatenate([s1, s2]))
                                std = std if std != 0 else 1
                                s1 = (s1 - mean) / std
                                s2 = (s2 - mean) / std
                                
                                fig = plot_single_comparison(s1, s2, col1, col2, results[idx]['DTW Distance'])
                                st.pyplot(fig)
    else:
        st.info("👆 Please upload a CSV or Excel file to begin the analysis.")
