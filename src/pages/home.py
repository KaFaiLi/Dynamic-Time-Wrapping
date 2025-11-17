"""Home page module"""
import streamlit as st


def render():
    """Render the home page"""
    # Hero section
    st.markdown('<h1 class="main-header">📊 DTW Comparison Tool</h1>', unsafe_allow_html=True)
    st.markdown("### Powerful Time Series Analysis Using Dynamic Time Warping")
    
    st.markdown("---")
    
    # Feature cards in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔍 What is DTW?")
        st.markdown("""
        Dynamic Time Warping is a sophisticated algorithm that measures similarity between 
        time series sequences, even when they're:
        - Out of phase
        - Operating at different speeds
        - Slightly distorted
        """)
    
    with col2:
        st.markdown("### 🎯 Key Features")
        st.markdown("""
        - **Outlier Detection**: Automatic IQR-based filtering
        - **Normalization**: Smart multivariate handling
        - **Visualization**: Interactive plots and heatmaps
        - **Export**: Download results as Excel files
        """)
    
    with col3:
        st.markdown("### 📈 Use Cases")
        st.markdown("""
        - Stock market pattern matching
        - Sensor data comparison
        - Speech recognition analysis
        - Medical signal processing
        """)
    
    st.markdown("---")
    
    # Analysis modes
    st.markdown('<h2 class="step-header">🛠️ Analysis Modes</h2>', unsafe_allow_html=True)
    
    # Mode 1
    with st.expander("📝 **DTW Comparison** - Compare Two Files", expanded=False):
        st.markdown("""
        **Perfect for:** Comparing two specific time series datasets
        
        **How it works:**
        1. Upload two CSV or Excel files
        2. Select date/time columns for temporal alignment
        3. Choose numerical columns to compare
        4. Get DTW distance and visualization
        
        **Output:**
        - Numerical DTW similarity score
        - Overlay plot of both time series
        - Cleaned data preview
        """)
    
    # Mode 2
    with st.expander("📁 **Batch Folder Comparison** - Analyze Multiple Files", expanded=False):
        st.markdown("""
        **Perfect for:** Processing entire directories of time series data
        
        **How it works:**
        1. Provide path to folder containing CSV/Excel files
        2. Select common columns across all files
        3. Automatic pairwise comparison of all files
        4. View ranking and similarity heatmap
        
        **Output:**
        - Pairwise distance matrix
        - Ranking of most dissimilar files
        - Interactive heatmap visualization
        - Downloadable Excel reports
        """)
    
    # Mode 3
    with st.expander("📊 **Single File Comparison** - Compare Columns Within File", expanded=False):
        st.markdown("""
        **Perfect for:** Analyzing relationships between columns in one dataset
        
        **How it works:**
        1. Upload a single CSV or Excel file
        2. Select multiple columns to compare
        3. Pairwise DTW comparison of all selected columns
        4. Identify which columns behave similarly
        
        **Output:**
        - Column-to-column distance matrix
        - Ranking of most dissimilar columns
        - Heatmap showing column relationships
        - Excel export functionality
        """)
    
    st.markdown("---")
    
    # Interpretation guide
    st.markdown('<h2 class="step-header">📖 Interpreting Results</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("**Lower DTW Distance**")
        st.markdown("""
        - Time series are more similar
        - Patterns align closely
        - Behaviors are correlated
        - Good for finding matches
        """)
    
    with col2:
        st.warning("**Higher DTW Distance**")
        st.markdown("""
        - Time series are less similar
        - Patterns diverge significantly
        - Independent behaviors
        - Useful for outlier detection
        """)
    
    st.info("""
    **💡 Pro Tip:** DTW distances are relative, not absolute. Always compare within your dataset rather than 
    using universal thresholds. The ranking feature helps identify outliers automatically.
    """)
    
    # Data preprocessing info
    with st.expander("⚙️ **Behind the Scenes: Data Processing Pipeline**"):
        st.markdown("""
        The tool automatically handles:
        
        1. **DateTime Combination**: Merges separate date and time columns
        2. **Outlier Removal**: IQR-based filtering (Q1 - 1.5×IQR to Q3 + 1.5×IQR)
        3. **Length Alignment**: Truncates to minimum common length
        4. **Normalization**: Z-score normalization for multivariate comparisons
        5. **DTW Computation**: Dynamic programming algorithm for optimal alignment
        
        All preprocessing is done automatically to ensure fair comparisons!
        """)
    
    st.markdown("---")
    
    # Call to action
    st.markdown("""
    ### 🚀 Ready to Get Started?
    
    Choose an analysis mode from the sidebar to begin your time series comparison!
    
    **Quick Start Recommendations:**
    - New users? Start with **DTW Comparison** for a simple two-file comparison
    - Have many files? Use **Batch Folder Comparison** for automated processing
    - Exploring one dataset? Try **Single File Comparison** to understand column relationships
    """)
    st.markdown('</div>', unsafe_allow_html=True)
