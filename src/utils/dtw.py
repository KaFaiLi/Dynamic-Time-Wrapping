"""Dynamic Time Warping (DTW) distance computation"""
import numpy as np


def dtw_distance_with_path(x, y):
    """
    Compute DTW distance and return the optimal alignment path.
    
    Args:
        x, y: Input arrays (n_samples, n_features) or (n_samples,)
    
    Returns:
        distance: DTW distance
        path: List of (i, j) tuples showing alignment
    """
    x = np.atleast_2d(x)
    y = np.atleast_2d(y)
    
    if x.shape[1] == 1:
        x = x.reshape(-1)
        y = y.reshape(-1)
        is_univariate = True
    else:
        is_univariate = False
    
    n, m = len(x), len(y)
    dtw_matrix = np.full((n + 1, m + 1), np.inf)
    dtw_matrix[0, 0] = 0
    
    # Forward pass - build cost matrix
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if is_univariate:
                cost = abs(x[i-1] - y[j-1])
            else:
                cost = np.linalg.norm(x[i-1] - y[j-1])
            
            dtw_matrix[i, j] = cost + min(
                dtw_matrix[i-1, j],    # insertion
                dtw_matrix[i, j-1],    # deletion
                dtw_matrix[i-1, j-1]   # match
            )
    
    # Backtrack to find optimal path
    path = []
    i, j = n, m
    while i > 0 and j > 0:
        path.append((i-1, j-1))
        
        # Find which direction we came from
        candidates = [
            (dtw_matrix[i-1, j-1], i-1, j-1),  # diagonal
            (dtw_matrix[i-1, j], i-1, j),      # up
            (dtw_matrix[i, j-1], i, j-1)       # left
        ]
        _, i, j = min(candidates, key=lambda x: x[0])
    
    path.reverse()
    return dtw_matrix[n, m], path


def analyze_local_divergence(x, y, path, window_size=10, threshold_percentile=75):
    """
    Identify periods of high divergence along the DTW alignment path.
    
    Args:
        x, y: Original aligned series
        path: DTW alignment path from dtw_distance_with_path()
        window_size: Size of sliding window for local distance calculation
        threshold_percentile: Percentile threshold for "high divergence"
    
    Returns:
        divergence_scores: Local divergence at each path position
        divergence_periods: List of (start_idx, end_idx, severity) tuples
        threshold: The computed threshold value
    """
    x = np.atleast_2d(x)
    y = np.atleast_2d(y)
    
    if x.shape[1] == 1:
        x = x.reshape(-1)
        y = y.reshape(-1)
        is_univariate = True
    else:
        is_univariate = False
    
    # Calculate local distance along path
    local_distances = []
    for i_x, i_y in path:
        if is_univariate:
            dist = abs(x[i_x] - y[i_y])
        else:
            dist = np.linalg.norm(x[i_x] - y[i_y])
        local_distances.append(dist)
    
    local_distances = np.array(local_distances)
    
    # Smooth with sliding window
    divergence_scores = np.convolve(
        local_distances, 
        np.ones(window_size) / window_size, 
        mode='same'
    )
    
    # Identify divergence periods
    threshold = np.percentile(divergence_scores, threshold_percentile)
    high_divergence = divergence_scores > threshold
    
    # Find contiguous regions
    divergence_periods = []
    in_divergence = False
    start_idx = 0
    
    for idx, is_divergent in enumerate(high_divergence):
        if is_divergent and not in_divergence:
            start_idx = idx
            in_divergence = True
        elif not is_divergent and in_divergence:
            severity = np.mean(divergence_scores[start_idx:idx]) / threshold
            divergence_periods.append((start_idx, idx, severity))
            in_divergence = False
    
    # Handle last period if still in divergence
    if in_divergence:
        severity = np.mean(divergence_scores[start_idx:]) / threshold
        divergence_periods.append((start_idx, len(high_divergence), severity))
    
    return divergence_scores, divergence_periods, threshold


def dtw_distance_multivariate(s1, s2, dist=lambda x, y: np.linalg.norm(x - y)):
    """
    Compute DTW distance between two sequences (supports multivariate).
    
    Uses dynamic programming with cost matrix to find optimal alignment.
    For multivariate series, uses Euclidean distance between vectors.
    
    Args:
        s1: First sequence (1D or 2D numpy array)
        s2: Second sequence (1D or 2D numpy array)
        dist: Distance function (default: Euclidean norm)
        
    Returns:
        float: DTW distance (cumulative distance from dtw_matrix[n, m])
    """
    n, m = len(s1), len(s2)
    dtw_matrix = np.full((n + 1, m + 1), np.inf)
    dtw_matrix[0, 0] = 0
    
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = dist(s1[i - 1], s2[j - 1])
            last_min = min(
                dtw_matrix[i - 1, j],      # insertion
                dtw_matrix[i, j - 1],      # deletion
                dtw_matrix[i - 1, j - 1]   # match
            )
            dtw_matrix[i, j] = cost + last_min
    
    return dtw_matrix[n, m]


def dtw_distance(s1, s2):
    """
    Compute DTW distance between two univariate sequences.
    
    Args:
        s1: First sequence (1D numpy array)
        s2: Second sequence (1D numpy array)
        
    Returns:
        float: DTW distance
    """
    n, m = len(s1), len(s2)
    dtw = np.full((n + 1, m + 1), np.inf)
    dtw[0, 0] = 0
    
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = abs(s1[i - 1] - s2[j - 1])
            dtw[i, j] = cost + min(
                dtw[i - 1, j],      # insertion
                dtw[i, j - 1],      # deletion
                dtw[i - 1, j - 1]   # match
            )
    
    return dtw[n, m]
