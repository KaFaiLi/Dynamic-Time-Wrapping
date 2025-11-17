"""Visualization utilities for plotting time series and heatmaps"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def plot_time_series_comparison(x, y, cols1, cols2, title="Time Series Comparison"):
    """
    Create a matplotlib figure comparing two time series.
    
    Args:
        x: First dataset (numpy array)
        y: Second dataset (numpy array)
        cols1: Column names from first dataset
        cols2: Column names from second dataset
        title: Plot title
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig, ax = plt.subplots(figsize=(14, 6))
    
    if len(cols1) == 1:
        ax.plot(range(len(x)), x.flatten(), label=f'Dataset 1: {cols1[0]}', color='blue')
        ax.plot(range(len(y)), y.flatten(), label=f'Dataset 2: {cols2[0]}', color='orange')
        ax.set_ylabel(f"{cols1[0]} / {cols2[0]}")
    else:
        for i, (col1, col2) in enumerate(zip(cols1, cols2)):
            ax.plot(range(len(x)), x[:, i], label=f'Dataset 1 - {col1}')
            ax.plot(range(len(y)), y[:, i], label=f'Dataset 2 - {col2}')
        ax.set_ylabel("Normalized Value")
    
    ax.set_title(title)
    ax.set_xlabel('Time Index (aligned)')
    ax.legend()
    
    return fig


def plot_single_comparison(s1, s2, col1, col2, distance):
    """
    Plot comparison between two single time series.
    
    Args:
        s1: First series (numpy array)
        s2: Second series (numpy array)
        col1: Name of first column
        col2: Name of second column
        distance: DTW distance value
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(range(len(s1)), s1, label=col1)
    ax.plot(range(len(s2)), s2, label=col2)
    ax.set_title(f"{col1} vs {col2} (DTW Distance: {distance:.3f})")
    ax.set_xlabel("Time Index (aligned)")
    ax.set_ylabel("Normalized Value")
    ax.legend()
    
    return fig


def plot_heatmap(dist_matrix, labels, title="DTW Distance Matrix"):
    """
    Create a heatmap of pairwise DTW distances.
    
    Args:
        dist_matrix: 2D numpy array of distances
        labels: List of labels for axes
        title: Plot title
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(dist_matrix, annot=True, fmt=".1f",
               xticklabels=labels, yticklabels=labels,
               ax=ax, cmap="viridis")
    ax.set_title(title)
    
    return fig


def compute_ranking(dist_matrix, names):
    """
    Compute ranking based on mean DTW distance to all others.
    
    Args:
        dist_matrix: 2D numpy array of pairwise distances
        names: List of entity names (files or columns)
        
    Returns:
        list: List of tuples (name, mean_distance) sorted by distance (descending)
    """
    # Exclude self-comparison (diagonal = 0) by replacing with NaN
    mean_distances = np.nanmean(np.where(dist_matrix == 0, np.nan, dist_matrix), axis=1)
    ranking = sorted(zip(names, mean_distances), key=lambda x: -x[1])
    return ranking
