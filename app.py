"""
DTW Comparison Tool - Entry Point

This is the main entry point for the Streamlit application.
All business logic has been modularized into the src/ folder.
"""
import streamlit as st
from src.config import PAGE_TITLE, PAGE_LAYOUT, PAGES
from src.pages import home, dtw_comparison, batch_comparison, single_file_comparison

# Configure Streamlit page
st.set_page_config(
    page_title=PAGE_TITLE, 
    layout=PAGE_LAYOUT,
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    
    /* Sidebar styling - theme-aware */
    [data-testid="stSidebar"] {
        background-color: #202225;
    }
    
    /* Dark mode support for sidebar */
    @media (prefers-color-scheme: dark) {
        [data-testid="stSidebar"] {
            background-color: var(--secondary-background-color);
        }
    }
    
    /* Navigation button styling - theme-aware */
    .nav-button {
        width: 100%;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        border: 2px solid var(--text-color-light, #e0e0e0);
        background-color: var(--secondary-background-color);
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: left;
        font-size: 1rem;
        color: var(--text-color);
    }
    
    .nav-button:hover {
        border-color: #1f77b4;
        background-color: var(--background-color);
        transform: translateX(5px);
    }
    
    .nav-button.active {
        border-color: #1f77b4;
        background-color: #1f77b4;
        color: white !important;
        font-weight: 600;
    }
    
    /* Info box styling - theme-aware */
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: rgba(31, 119, 180, 0.1);
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    
    /* Step header styling */
    .step-header {
        color: #1f77b4;
        font-weight: 600;
        font-size: 1.3rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Hide default streamlit header */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Button styling */
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        font-weight: 600;
        border-radius: 0.5rem;
        padding: 0.5rem 2rem;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #1557a0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation with selectbox (more professional than radio)
with st.sidebar:
    st.markdown("### 📊 DTW Comparison Tool")
    st.markdown("---")
    
    # Navigation with selectbox
    page = st.selectbox(
        "Choose Analysis Mode",
        PAGES,
        index=0,
        help="Select the type of analysis you want to perform"
    )
    
    st.markdown("---")
    
    # Add some helpful info in sidebar
    st.markdown("### ℹ️ Quick Guide")
    if page == "Home":
        st.info("Learn about DTW and how to use this tool")
    elif page == "DTW Comparison":
        st.info("Compare two time series files using DTW algorithm")
    elif page == "DTW Batch Folder Comparison":
        st.info("Batch process multiple files in a folder")
    elif page == "Single File Pairwise Comparison":
        st.info("Compare columns within a single file")
    
    st.markdown("---")
    st.markdown("### 📚 Resources")
    st.markdown("""
    - [What is DTW?](https://en.wikipedia.org/wiki/Dynamic_time_warping)
    - [Documentation](https://github.com)
    """)

# Route to appropriate page
if page == "Home":
    home.render()
elif page == "DTW Comparison":
    dtw_comparison.render()
elif page == "DTW Batch Folder Comparison":
    batch_comparison.render()
elif page == "Single File Pairwise Comparison":
    single_file_comparison.render()
