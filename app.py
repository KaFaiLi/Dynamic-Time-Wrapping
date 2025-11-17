"""
DTW Comparison Tool - Entry Point

This is the main entry point for the Streamlit application.
All business logic has been modularized into the src/ folder.
"""
import streamlit as st
from src.config import PAGE_TITLE, PAGE_LAYOUT, PAGES
from src.pages import home, dtw_comparison, batch_comparison, single_file_comparison

# Configure Streamlit page
st.set_page_config(page_title=PAGE_TITLE, layout=PAGE_LAYOUT)

# Sidebar navigation
page = st.sidebar.radio("Navigation", PAGES, index=0)

# Route to appropriate page
if page == "Home":
    home.render()
elif page == "DTW Comparison":
    dtw_comparison.render()
elif page == "DTW Batch Folder Comparison":
    batch_comparison.render()
elif page == "Single File Pairwise Comparison":
    single_file_comparison.render()
