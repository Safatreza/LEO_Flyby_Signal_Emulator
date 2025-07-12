"""
Plotter for LEO Satellite Flyby Visualization
- Reads data from orbit, signal, and tracking logs (pandas DataFrames)
- Generates interactive Plotly plots and saves as HTML
"""
import os
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

PLOT_DIR = 'data/plots/'
os.makedirs(PLOT_DIR, exist_ok=True)


def plot_polar_tracking(tracking_df, output_path=None):
    """
    Create a 2D polar plot of antenna azimuth/elevation.
    Args:
        tracking_df: DataFrame with 'antenna_az', 'antenna_el', 'lock_status'
        output_path: Path to save HTML file
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=tracking_df['antenna_el'],
        theta=tracking_df['antenna_az'],
        mode='lines+markers',
        marker=dict(color=(tracking_df['lock_status'] == 'Locked').map({True: 'green', False: 'red'})),
        name='Antenna Pointing',
        text=tracking_df['lock_status'],
        hovertemplate='Az: %{theta:.2f}°<br>El: %{r:.2f}°<br>Status: %{text}'
    ))
    fig.update_layout(
        title='Antenna Azimuth/Elevation (Polar Plot)',
        polar=dict(
            radialaxis=dict(range=[0, 90], title='Elevation (deg)'),
            angularaxis=dict(direction='clockwise', rotation=90, title='Azimuth (deg)')
        ),
        showlegend=True
    )
    if output_path:
        fig.write_html(output_path)
    return fig


def plot_signal_metrics(signal_df, output_path=None):
    """
    Create 2D time-series plots of Doppler shift, path loss, and SNR.
    Args:
        signal_df: DataFrame with 'time', 'doppler_shift', 'path_loss', 'snr'
        output_path: Path to save HTML file
    Returns:
        Plotly Figure
    """
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        subplot_titles=('Doppler Shift (Hz)', 'Path Loss (dB)', 'SNR (dB)'))
    fig.add_trace(go.Scatter(x=signal_df['time'], y=signal_df['doppler_shift'],
                             mode='lines+markers', name='Doppler Shift',
                             hovertemplate='Time: %{x}<br>Doppler: %{y:.2f} Hz'), row=1, col=1)
    fig.add_trace(go.Scatter(x=signal_df['time'], y=signal_df['path_loss'],
                             mode='lines+markers', name='Path Loss',
                             hovertemplate='Time: %{x}<br>Path Loss: %{y:.2f} dB'), row=2, col=1)
    fig.add_trace(go.Scatter(x=signal_df['time'], y=signal_df['snr'],
                             mode='lines+markers', name='SNR',
                             hovertemplate='Time: %{x}<br>SNR: %{y:.2f} dB'), row=3, col=1)
    fig.update_layout(title='Signal Metrics Over Time', height=900, showlegend=True)
    fig.update_xaxes(title_text='Time', row=3, col=1)
    fig.update_yaxes(title_text='Doppler (Hz)', row=1, col=1)
    fig.update_yaxes(title_text='Path Loss (dB)', row=2, col=1)
    fig.update_yaxes(title_text='SNR (dB)', row=3, col=1)
    if output_path:
        fig.write_html(output_path)
    return fig


def plot_3d_trajectory(orbit_df, tracking_df, output_path=None):
    """
    Create a 3D plot of satellite and antenna trajectory relative to the ground station.
    Args:
        orbit_df: DataFrame with 'azimuth', 'elevation', 'range'
        tracking_df: DataFrame with 'antenna_az', 'antenna_el'
        output_path: Path to save HTML file
    Returns:
        Plotly Figure
    """
    # Convert spherical to Cartesian for satellite
    sat_x = orbit_df['range'] * np.cos(np.radians(orbit_df['elevation'])) * np.cos(np.radians(orbit_df['azimuth']))
    sat_y = orbit_df['range'] * np.cos(np.radians(orbit_df['elevation'])) * np.sin(np.radians(orbit_df['azimuth']))
    sat_z = orbit_df['range'] * np.sin(np.radians(orbit_df['elevation']))
    # Antenna (assume fixed radius for visualization)
    ant_r = orbit_df['range'].mean() * 0.1
    ant_x = ant_r * np.cos(np.radians(tracking_df['antenna_el'])) * np.cos(np.radians(tracking_df['antenna_az']))
    ant_y = ant_r * np.cos(np.radians(tracking_df['antenna_el'])) * np.sin(np.radians(tracking_df['antenna_az']))
    ant_z = ant_r * np.sin(np.radians(tracking_df['antenna_el']))
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=sat_x, y=sat_y, z=sat_z, mode='lines+markers',
                               name='Satellite Trajectory',
                               marker=dict(size=3, color='blue'),
                               line=dict(color='blue')))
    fig.add_trace(go.Scatter3d(x=ant_x, y=ant_y, z=ant_z, mode='lines+markers',
                               name='Antenna Pointing',
                               marker=dict(size=3, color='orange'),
                               line=dict(color='orange')))
    fig.update_layout(
        title='3D Trajectory: Satellite and Antenna',
        scene=dict(
            xaxis_title='X (km)',
            yaxis_title='Y (km)',
            zaxis_title='Z (km)'
        ),
        legend=dict(x=0.01, y=0.99)
    )
    if output_path:
        fig.write_html(output_path)
    return fig


# Example usage for batch plotting
if __name__ == '__main__':
    import numpy as np
    # Load data
    orbit_df = pd.read_csv('data/logs/orbit_log.csv')
    signal_df = pd.read_csv('data/logs/signal_log.csv')
    tracking_df = pd.read_csv('data/logs/tracking_log.csv')
    # Plot and save
    plot_polar_tracking(tracking_df, os.path.join(PLOT_DIR, 'tracking_polar.html'))
    plot_signal_metrics(signal_df, os.path.join(PLOT_DIR, 'signal_plot.html'))
    plot_3d_trajectory(orbit_df, tracking_df, os.path.join(PLOT_DIR, 'orbit_plot.html'))
    print('Plots saved to', PLOT_DIR) 