"""Configuration settings for the DTW Comparison Tool"""

# Streamlit page configuration
PAGE_TITLE = "DTW Comparison Tool"
PAGE_LAYOUT = "wide"

# Navigation pages
PAGES = [
    "Home",
    "DTW Comparison",
    "DTW Batch Folder Comparison",
    "Single File Pairwise Comparison"
]

# Outlier removal settings
IQR_MULTIPLIER = 1.5

# File type support
SUPPORTED_FILE_TYPES = ["csv", "xlsx"]
