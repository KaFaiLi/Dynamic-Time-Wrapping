"""Visualization utilities for plotting time series and heatmaps"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd


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


def plot_divergence_analysis(df, col1, col2, path, divergence_scores, divergence_periods, threshold):
    """
    Create visualization highlighting divergence periods between two time series.
    
    Args:
        df: DataFrame with original data and index
        col1, col2: Column names being compared
        path: DTW alignment path
        divergence_scores: Local divergence scores along path
        divergence_periods: List of (start, end, severity) tuples
        threshold: Divergence threshold value
        
    Returns:
        matplotlib Figure object
    """
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    
    # Map path indices back to time indices
    time_indices_col1 = [path[i][0] for i in range(len(path))]
    time_indices_col2 = [path[i][1] for i in range(len(path))]
    
    # Plot 1: Original series with divergence regions highlighted
    ax1 = axes[0]
    ax1.plot(df.index, df[col1], label=col1, alpha=0.7, linewidth=2)
    ax1.plot(df.index, df[col2], label=col2, alpha=0.7, linewidth=2)
    
    # Highlight divergence periods
    legend_added = {'high': False, 'moderate': False}
    for start, end, severity in divergence_periods:
        start_time = df.index[time_indices_col1[start]]
        end_time = df.index[time_indices_col1[min(end, len(time_indices_col1)-1)]]
        
        if severity > 1.5:
            color = 'red'
            label = f'High Divergence (>{1.5:.1f}x threshold)' if not legend_added['high'] else ''
            legend_added['high'] = True
        else:
            color = 'orange'
            label = f'Moderate Divergence (>{1.0:.1f}x threshold)' if not legend_added['moderate'] else ''
            legend_added['moderate'] = True
        
        ax1.axvspan(start_time, end_time, alpha=0.2, color=color, label=label if label else '')
    
    ax1.set_ylabel('Normalized Value', fontsize=11, fontweight='bold')
    ax1.set_title(f'Time Series Comparison: {col1} vs {col2}\n(Highlighted regions show divergence periods)', 
                 fontsize=13, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Local divergence score over time
    ax2 = axes[1]
    aligned_times = [df.index[idx] for idx in time_indices_col1]
    ax2.plot(aligned_times, divergence_scores, color='purple', linewidth=2, label='Local Divergence Score')
    ax2.axhline(threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold ({threshold:.3f})')
    ax2.fill_between(aligned_times, 0, divergence_scores, where=(divergence_scores > threshold), 
                     color='red', alpha=0.3, label='High Divergence Regions')
    ax2.set_ylabel('Divergence Score', fontsize=11, fontweight='bold')
    ax2.set_title('Local DTW Divergence Over Time', fontsize=13, fontweight='bold')
    ax2.legend(loc='upper left', fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Difference between series
    ax3 = axes[2]
    diff = df[col1].values - df[col2].values
    ax3.plot(df.index, diff, color='green', linewidth=1.5, label='Difference (Col1 - Col2)')
    ax3.axhline(0, color='black', linestyle='-', linewidth=0.5)
    ax3.fill_between(df.index, 0, diff, where=(diff > 0), color='green', alpha=0.3, label='Col1 > Col2')
    ax3.fill_between(df.index, 0, diff, where=(diff < 0), color='red', alpha=0.3, label='Col1 < Col2')
    ax3.set_xlabel('Time', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Raw Difference', fontsize=11, fontweight='bold')
    ax3.set_title('Raw Difference Between Series', fontsize=13, fontweight='bold')
    ax3.legend(loc='upper left', fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig
