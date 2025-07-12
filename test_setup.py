#!/usr/bin/env python3
"""
LEO Antenna Tracking Simulator
- Simulates ground station antenna tracking a LEO satellite.
- Reads azimuth/elevation from orbit log and antenna parameters from config.
- Outputs tracking log and interactive plots.
"""
import os
import sys
import yaml
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import plotly.graph_objs as go

# Constants
CONFIG_PATH = 'config/sim_config.yaml'
ORBIT_LOG = 'data/logs/orbit_log.csv'
TRACKING_LOG = 'data/logs/tracking_log.csv'
PLOT_DIR = 'data/plots/'

def load_antenna_config(config_path):
    """Load antenna parameters from YAML config."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        antenna = config.get('antenna', {})
        return antenna
    except Exception as e:
        raise RuntimeError(f"Failed to load antenna config: {e}")

def interpolate_track(times, values, slew_rate_deg_s, time_step=1.0):
    """
    Interpolate antenna motion with slew rate limit.
    Args:
        times: list of time indices (seconds)
        values: list of azimuth or elevation values (degrees)
        slew_rate_deg_s: max slew rate in deg/s
        time_step: time step in seconds
    Returns:
        np.array of interpolated values
    """
    # Interpolate with cubic for smoothness
    f = interp1d(times, values, kind='cubic', fill_value='extrapolate')
    interp_times = np.arange(times[0], times[-1]+1, time_step)
    interp_values = f(interp_times)
    # Apply slew rate limit
    limited_values = [interp_values[0]]
    for v in interp_values[1:]:
        prev = limited_values[-1]
        max_delta = slew_rate_deg_s * time_step
        delta = np.clip(v - prev, -max_delta, max_delta)
        limited_values.append(prev + delta)
    return interp_times, np.array(limited_values)

def simulate_tracking(orbit_df, antenna_config):
    """
    Simulate antenna tracking and return DataFrame.
    Args:
        orbit_df: DataFrame with time, azimuth, elevation
        antenna_config: dict with beamwidth and slew_rate
    Returns:
        DataFrame with time, antenna_az, antenna_el, pointing_error, lock_status
    """
    beamwidth = float(antenna_config.get('beamwidth_deg', 10))
    slew_rate = float(antenna_config.get('slew_rate_deg_s', 5))
    # Prepare time and az/el arrays
    times = np.arange(len(orbit_df))
    sat_az = orbit_df['azimuth'].values
    sat_el = orbit_df['elevation'].values
    # Interpolate antenna motion
    interp_times, ant_az = interpolate_track(times, sat_az, slew_rate)
    _, ant_el = interpolate_track(times, sat_el, slew_rate)
    # Calculate pointing error and lock status
    pointing_error = np.sqrt((ant_az - sat_az)**2 + (ant_el - sat_el)**2)
    lock_status = np.where(
        (pointing_error < beamwidth/2) & (sat_el >= 0),
        'Locked',
        'Signal lost'
    )
    # Use original time column for output
    output_times = orbit_df['time'].values
    # Build DataFrame
    df = pd.DataFrame({
        'time': output_times,
        'antenna_az': ant_az,
        'antenna_el': ant_el,
        'pointing_error': pointing_error,
        'lock_status': lock_status
    })
    return df

def plot_tracking(df, orbit_df):
    """Generate and save 2D polar and 3D trajectory plots."""
    os.makedirs(PLOT_DIR, exist_ok=True)
    # 2D Polar Plot (Azimuth vs Elevation)
    polar_fig = go.Figure()
    polar_fig.add_trace(go.Scatterpolar(
        r=orbit_df['elevation'],
        theta=orbit_df['azimuth'],
        mode='lines+markers',
        name='Satellite'
    ))
    polar_fig.add_trace(go.Scatterpolar(
        r=df['antenna_el'],
        theta=df['antenna_az'],
        mode='lines+markers',
        name='Antenna'
    ))
    polar_fig.update_layout(
        title='Antenna vs Satellite (Polar Plot)',
        polar=dict(
            radialaxis=dict(range=[0, 90], title='Elevation (deg)'),
            angularaxis=dict(direction='clockwise', rotation=90, title='Azimuth (deg)')
        )
    )
    polar_fig.write_html(os.path.join(PLOT_DIR, 'tracking_polar.html'))

    # 3D Trajectory Plot
    traj_fig = go.Figure()
    traj_fig.add_trace(go.Scatter3d(
        x=orbit_df['azimuth'], y=orbit_df['elevation'], z=np.arange(len(orbit_df)),
        mode='lines', name='Satellite'
    ))
    traj_fig.add_trace(go.Scatter3d(
        x=df['antenna_az'], y=df['antenna_el'], z=np.arange(len(df)),
        mode='lines', name='Antenna'
    ))
    traj_fig.update_layout(
        title='Antenna vs Satellite Trajectory (3D)',
        scene=dict(
            xaxis_title='Azimuth (deg)',
            yaxis_title='Elevation (deg)',
            zaxis_title='Time Index'
        )
    )
    traj_fig.write_html(os.path.join(PLOT_DIR, 'tracking_3d.html'))

def main():
    """Main entry point for antenna tracking simulation."""
    try:
        # Load antenna config
        antenna_config = load_antenna_config(CONFIG_PATH)
        # Load orbit data
        if not os.path.exists(ORBIT_LOG):
            print(f"Error: Orbit log not found at {ORBIT_LOG}")
            sys.exit(1)
        orbit_df = pd.read_csv(ORBIT_LOG)
        if len(orbit_df) == 0:
            print("Error: Orbit log is empty.")
            sys.exit(1)
        # Simulate tracking
        tracking_df = simulate_tracking(orbit_df, antenna_config)
        # Save tracking log
        os.makedirs(os.path.dirname(TRACKING_LOG), exist_ok=True)
        tracking_df.to_csv(TRACKING_LOG, index=False)
        print(f"Tracking simulation complete. Results saved to {TRACKING_LOG}")
        # Generate plots
        plot_tracking(tracking_df, orbit_df)
        print(f"Plots saved to {PLOT_DIR}")
        print(tracking_df.head())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 