"""Single File Pairwise Comparison page"""
import streamlit as st
import pandas as pd
import numpy as np
import itertools
import io
import matplotlib.pyplot as plt
from src.utils.file_io import read_file
from src.utils.preprocessing import add_datetime, remove_outliers_iqr
from src.utils.dtw import dtw_distance, dtw_distance_with_path, analyze_local_divergence
from src.utils.visualization import plot_single_comparison, plot_heatmap, compute_ranking, plot_divergence_analysis


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
        # Reset session state when new file is uploaded
        if 'last_uploaded_file' not in st.session_state or st.session_state.last_uploaded_file != uploaded_file.name:
            st.session_state.analysis_complete = False
            st.session_state.last_uploaded_file = uploaded_file.name
        
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
            
            # Reset analysis if column selection changes
            if 'last_selected_cols' not in st.session_state or st.session_state.last_selected_cols != selected_cols:
                st.session_state.analysis_complete = False
                st.session_state.last_selected_cols = selected_cols
            
            if len(selected_cols) >= 2:
                num_comparisons = len(list(itertools.combinations(selected_cols, 2)))
                st.caption(f"This will perform {num_comparisons} pairwise comparisons")
            
            if len(selected_cols) < 2:
                st.warning("⚠️ Please select at least two columns.")
            else:
                st.markdown("---")
                
                # 4. Divergence Analysis Settings
                st.markdown('<div class="step-header">⚙️ Step 4: Divergence Analysis Settings</div>', unsafe_allow_html=True)
                st.info("💡 Configure divergence detection parameters. Analysis will run automatically for all pairs.")
                
                col_config1, col_config2 = st.columns(2)
                with col_config1:
                    window_size = st.slider(
                        "Smoothing Window Size",
                        min_value=5,
                        max_value=50,
                        value=10,
                        help="Larger windows = smoother divergence detection, less sensitive to noise"
                    )
                with col_config2:
                    threshold_percentile = st.slider(
                        "Divergence Threshold (Percentile)",
                        min_value=50,
                        max_value=95,
                        value=75,
                        help="Higher percentile = only flag extreme divergences (less sensitive)"
                    )
                
                st.markdown("---")
                
                # Initialize session state for storing results
                if 'analysis_complete' not in st.session_state:
                    st.session_state.analysis_complete = False
                
                col_btn1, col_btn2 = st.columns([3, 1])
                with col_btn1:
                    run = st.button("🚀 Run Pairwise DTW Comparison with Divergence Analysis", type="primary", use_container_width=True)
                with col_btn2:
                    if st.session_state.analysis_complete:
                        if st.button("🔄 Clear Results", use_container_width=True):
                            st.session_state.analysis_complete = False
                            st.rerun()
                
                if run:
                    # Add Datetime if needed
                    if date_col != "None":
                        df = add_datetime(df, date_col, time_col)
                        df = df.sort_values('Datetime')
                    
                    # Prepare results and distance matrix
                    st.markdown("---")
                    st.markdown("## 🔄 Processing Comparisons & Divergence Analysis")
                    
                    results = []
                    divergence_results = {}  # Store divergence data for all pairs
                    pairs = list(itertools.combinations(selected_cols, 2))
                    n = len(selected_cols)
                    dist_matrix = np.zeros((n, n))
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    total = len(pairs)
                    
                    # Container for individual comparisons
                    comparisons_container = st.container()
                    
                    for idx, (col1, col2) in enumerate(pairs):
                        status_text.text(f"📊 Comparing & analyzing divergence: `{col1}` vs `{col2}` ({idx + 1}/{total})")
                        
                        # Remove outliers independently
                        s1 = remove_outliers_iqr(df[col1].dropna())
                        s2 = remove_outliers_iqr(df[col2].dropna())

                        # Align lengths
                        min_len = min(len(s1), len(s2))
                        s1_aligned = s1.iloc[:min_len]
                        s2_aligned = s2.iloc[:min_len]
                        
                        # Create aligned dataframe for later use
                        df_aligned = pd.DataFrame({
                            col1: s1_aligned.values,
                            col2: s2_aligned.values
                        }, index=s1_aligned.index)
                        
                        # Normalize
                        mean = np.mean(np.concatenate([s1_aligned.values, s2_aligned.values]))
                        std = np.std(np.concatenate([s1_aligned.values, s2_aligned.values]))
                        std = std if std != 0 else 1
                        s1_norm = (s1_aligned.values - mean) / std
                        s2_norm = (s2_aligned.values - mean) / std
                        
                        # DTW with path
                        dist, path = dtw_distance_with_path(s1_norm.reshape(-1, 1), s2_norm.reshape(-1, 1))
                        
                        # Divergence analysis
                        divergence_scores, divergence_periods, threshold = analyze_local_divergence(
                            s1_norm.reshape(-1, 1), s2_norm.reshape(-1, 1), 
                            path, window_size, threshold_percentile
                        )
                        
                        # Store divergence data
                        df_normalized = pd.DataFrame({
                            col1: s1_norm,
                            col2: s2_norm
                        }, index=s1_aligned.index)
                        
                        divergence_results[f"{col1} vs {col2}"] = {
                            'df_normalized': df_normalized,
                            'path': path,
                            'divergence_scores': divergence_scores,
                            'divergence_periods': divergence_periods,
                            'threshold': threshold,
                            'num_periods': len(divergence_periods)
                        }
                        
                        results.append({
                            "Column 1": col1,
                            "Column 2": col2,
                            "DTW Distance": dist,
                            "Divergence Periods": len(divergence_periods)
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
                    st.success(f"✅ Completed {total} pairwise comparisons with divergence analysis!")
                    
                    # Store results in session state
                    st.session_state.results = results
                    st.session_state.divergence_results = divergence_results
                    st.session_state.dist_matrix = dist_matrix
                    st.session_state.selected_cols = selected_cols
                    st.session_state.pairs = pairs
                    st.session_state.analysis_complete = True
                
                # Display results (whether just computed or from session state)
                if st.session_state.analysis_complete:
                    # Retrieve from session state
                    results = st.session_state.results
                    divergence_results = st.session_state.divergence_results
                    dist_matrix = st.session_state.dist_matrix
                    selected_cols = st.session_state.selected_cols
                    pairs = st.session_state.pairs
                    
                    # Show results in tabs
                    st.markdown("---")
                    st.markdown("## 📊 Results")
                    
                    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Distance Table", "🔍 Divergence Summary", "🏆 Column Ranking", "🗺️ Heatmap", "📈 Detailed Analysis"])
                    
                    with tab1:
                        st.markdown("### Pairwise DTW Distances & Divergence Counts")
                        st.caption("All pairwise comparisons with detected divergence periods")
                        results_df = pd.DataFrame(results)
                        st.dataframe(
                            results_df.style.background_gradient(subset=['Divergence Periods'], cmap='YlOrRd'),
                            use_container_width=True, 
                            height=400
                        )
                    
                    with tab2:
                        st.markdown("### Divergence Analysis Summary")
                        st.caption("Overview of all divergence periods detected across all pairs")
                        
                        # Create summary statistics
                        total_divergence_periods = sum([data['num_periods'] for data in divergence_results.values()])
                        
                        if total_divergence_periods > 0:
                            col_stat1, col_stat2, col_stat3 = st.columns(3)
                            with col_stat1:
                                st.metric("Total Divergence Periods", total_divergence_periods)
                            with col_stat2:
                                pairs_with_divergence = sum([1 for data in divergence_results.values() if data['num_periods'] > 0])
                                st.metric("Pairs with Divergence", f"{pairs_with_divergence}/{len(pairs)}")
                            with col_stat3:
                                avg_periods = total_divergence_periods / len(pairs)
                                st.metric("Avg Periods per Pair", f"{avg_periods:.1f}")
                            
                            st.markdown("---")
                            
                            # Detailed table of all divergence periods
                            all_divergence_data = []
                            for pair_name, data in divergence_results.items():
                                if data['num_periods'] > 0:
                                    for start, end, severity in data['divergence_periods']:
                                        path = data['path']
                                        df_norm = data['df_normalized']
                                        start_idx = path[start][0]
                                        end_idx = path[min(end, len(path)-1)][0]
                                        
                                        all_divergence_data.append({
                                            'Pair': pair_name,
                                            'Start Time': df_norm.index[start_idx],
                                            'End Time': df_norm.index[end_idx],
                                            'Duration': end - start,
                                            'Severity': severity,
                                            'Alert': '🔴 Critical' if severity > 1.5 else '🟠 Warning'
                                        })
                            
                            if all_divergence_data:
                                divergence_summary_df = pd.DataFrame(all_divergence_data)
                                divergence_summary_df = divergence_summary_df.sort_values('Severity', ascending=False)
                                
                                st.markdown("#### All Detected Divergence Periods (Sorted by Severity)")
                                st.dataframe(
                                    divergence_summary_df.style.applymap(
                                        lambda x: 'background-color: #ffcccc' if x == '🔴 Critical' else ('background-color: #ffe6cc' if x == '🟠 Warning' else ''),
                                        subset=['Alert']
                                    ).background_gradient(subset=['Severity'], cmap='YlOrRd'),
                                    use_container_width=True,
                                    height=400
                                )
                                
                                # Export divergence summary
                                output = io.BytesIO()
                                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                    divergence_summary_df.to_excel(writer, sheet_name='All Divergence Periods', index=False)
                                    results_df.to_excel(writer, sheet_name='DTW Distances', index=False)
                                output.seek(0)
                                
                                st.download_button(
                                    label="📥 Download Complete Divergence Report (Excel)",
                                    data=output,
                                    file_name="divergence_analysis_report.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                        else:
                            st.info("✅ No significant divergence periods detected in any pair with current threshold settings.")
                    
                    with tab3:
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
                    
                    with tab4:
                        st.markdown("### Distance Matrix Heatmap")
                        st.caption("Visual representation of pairwise DTW distances")
                        
                        fig = plot_heatmap(dist_matrix, selected_cols, "DTW Distance Matrix")
                        st.pyplot(fig, use_container_width=True)
                        plt.close(fig)
                    
                    with tab5:
                        st.markdown("### Detailed Divergence Analysis")
                        st.caption("Select a pair to view comprehensive divergence visualization")
                        
                        # Let user select a pair to visualize
                        selected_pair = st.selectbox(
                            "Select a pair for detailed visualization:",
                            list(divergence_results.keys()),
                            help="Choose which comparison to examine in detail"
                        )
                        
                        if selected_pair:
                            col1, col2 = selected_pair.split(" vs ")
                            data = divergence_results[selected_pair]
                            
                            # Display summary for this pair
                            col_info1, col_info2, col_info3 = st.columns(3)
                            with col_info1:
                                st.metric("DTW Distance", f"{results_df[results_df['Column 1'] == col1]['DTW Distance'].values[0]:.3f}")
                            with col_info2:
                                st.metric("Divergence Periods", data['num_periods'])
                            with col_info3:
                                if data['num_periods'] > 0:
                                    max_severity = max([s for _, _, s in data['divergence_periods']])
                                    st.metric("Max Severity", f"{max_severity:.2f}x")
                                else:
                                    st.metric("Max Severity", "N/A")
                            
                            # Show divergence periods table for this pair
                            if data['num_periods'] > 0:
                                st.markdown("#### Divergence Periods for This Pair")
                                periods_data = []
                                for start, end, severity in data['divergence_periods']:
                                    start_idx = data['path'][start][0]
                                    end_idx = data['path'][min(end, len(data['path'])-1)][0]
                                    start_time = data['df_normalized'].index[start_idx]
                                    end_time = data['df_normalized'].index[end_idx]
                                    duration = end - start
                                    
                                    periods_data.append({
                                        "Start Time": start_time,
                                        "End Time": end_time,
                                        "Duration (points)": duration,
                                        "Severity": f"{severity:.2f}x",
                                        "Alert Level": "🔴 Critical" if severity > 1.5 else "🟠 Warning"
                                    })
                                
                                periods_df = pd.DataFrame(periods_data)
                                st.dataframe(
                                    periods_df.style.applymap(
                                        lambda x: 'background-color: #ffcccc' if x == '🔴 Critical' else ('background-color: #ffe6cc' if x == '🟠 Warning' else ''),
                                        subset=['Alert Level']
                                    ),
                                    use_container_width=True
                                )
                            
                            # Create visualization
                            st.markdown("#### Comprehensive Divergence Visualization")
                            fig = plot_divergence_analysis(
                                data['df_normalized'], 
                                col1, 
                                col2, 
                                data['path'], 
                                data['divergence_scores'], 
                                data['divergence_periods'], 
                                data['threshold']
                            )
                            
                            # Display the figure
                            st.pyplot(fig, use_container_width=True)
                            
                            # Export options for this pair
                            col_export1, col_export2 = st.columns(2)
                            with col_export1:
                                # Create buffer for download (create new buffer to avoid conflicts)
                                buf = io.BytesIO()
                                fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                                buf.seek(0)
                                st.download_button(
                                    label="📊 Download Visualization (PNG)",
                                    data=buf,
                                    file_name=f"divergence_{col1}_vs_{col2}.png",
                                    mime="image/png",
                                    use_container_width=True
                                )
                            
                            # Close the figure to free memory and prevent display issues
                            plt.close(fig)
                            
                            with col_export2:
                                if data['num_periods'] > 0:
                                    output = io.BytesIO()
                                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                        periods_df.to_excel(writer, sheet_name='Divergence Periods', index=False)
                                    output.seek(0)
                                    st.download_button(
                                        label="📋 Download Periods Table (Excel)",
                                        data=output,
                                        file_name=f"periods_{col1}_vs_{col2}.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        use_container_width=True
                                    )
    else:
        st.info("👆 Please upload a CSV or Excel file to begin the analysis.")
