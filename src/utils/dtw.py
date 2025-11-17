"""Dynamic Time Warping (DTW) distance computation"""
import numpy as np


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
