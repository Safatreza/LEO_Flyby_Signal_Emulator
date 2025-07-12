"""
Enhanced Flask Dashboard for Dependency-free LEO Satellite Flyby Emulator
- Displays comprehensive Matplotlib plots (orbit, signal, antenna tracking)
- Real-time simulation data with interactive controls
- Advanced visualizations with multiple plot types
- Modern responsive UI with real-time updates
- Runs on localhost:5001 to avoid conflicts
"""
import os
import json
import base64
import math
import random
from io import BytesIO
from datetime import datetime
from flask import Flask, render_template, jsonify, request, Response
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Import simulation functions from demo.py
from demo import CONFIG, run_simulation, calculate_satellite_position, calculate_doppler_shift, calculate_path_loss, calculate_snr, simulate_antenna_tracking

app = Flask(__name__)

# Global variable to store simulation results
simulation_results = None

# Constants
C = 299792458  # Speed of light in m/s


def create_plot_image(plot_func, *args, **kwargs):
    """
    Create a matplotlib plot and return it as a base64 encoded image.
    
    Args:
        plot_func: Function that creates the plot
        *args, **kwargs: Arguments for the plot function
    
    Returns:
        str: Base64 encoded PNG image
    """
    plt.figure(figsize=(12, 8))
    plot_func(*args, **kwargs)
    
    # Save plot to bytes buffer
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    
    # Encode to base64
    img_data = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()
    
    return img_data


def plot_orbit_overview(results):
    """Create comprehensive orbit overview plot."""
    times = [r['time_sec'] for r in results]
    ranges = [r['satellite']['range_km'] for r in results]
    elevations = [r['satellite']['elevation_deg'] for r in results]
    azimuths = [r['satellite']['azimuth_deg'] for r in results]
    
    plt.subplot(2, 2, 1)
    plt.plot(times, ranges, 'b-', linewidth=2)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Range (km)')
    plt.title('Satellite Range vs Time')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 2)
    plt.plot(times, elevations, 'g-', linewidth=2)
    plt.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Horizon')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Elevation (degrees)')
    plt.title('Satellite Elevation vs Time')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 3)
    plt.plot(times, azimuths, 'm-', linewidth=2)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Azimuth (degrees)')
    plt.title('Satellite Azimuth vs Time')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 4)
    # Create polar plot for ground track
    ax = plt.subplot(2, 2, 4, projection='polar')
    valid_data = [(az, el) for az, el in zip(azimuths, elevations) if el >= 0]
    if valid_data:
        az_vals, el_vals = zip(*valid_data)
        ax.scatter(np.radians(az_vals), [90-el for el in el_vals], 
                  c=el_vals, cmap='viridis', s=20, alpha=0.7)
        ax.set_title('Ground Track (Polar View)')
        ax.grid(True)
    
    plt.tight_layout()


def plot_signal_metrics(results):
    """Create comprehensive signal metrics plot."""
    times = [r['time_sec'] for r in results]
    dopplers = [r['signal']['doppler_hz'] for r in results if r['signal']['doppler_hz'] is not None]
    snrs = [r['signal']['snr_db'] for r in results if r['signal']['snr_db'] is not None]
    path_losses = [r['signal']['path_loss_db'] for r in results if r['signal']['path_loss_db'] is not None]
    valid_times = [t for t, r in zip(times, results) if r['signal']['doppler_hz'] is not None]
    
    plt.subplot(2, 2, 1)
    plt.plot(valid_times, dopplers, 'r-', linewidth=2)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Doppler Shift (Hz)')
    plt.title('Doppler Shift vs Time')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 2)
    plt.plot(valid_times, snrs, 'm-', linewidth=2)
    plt.axhline(y=10, color='r', linestyle='--', alpha=0.5, label='10 dB threshold')
    plt.axhline(y=15, color='orange', linestyle='--', alpha=0.5, label='15 dB threshold')
    plt.xlabel('Time (seconds)')
    plt.ylabel('SNR (dB)')
    plt.title('Signal-to-Noise Ratio vs Time')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 3)
    plt.plot(valid_times, path_losses, 'b-', linewidth=2)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Path Loss (dB)')
    plt.title('Path Loss vs Time')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 4)
    # SNR vs Range scatter plot
    ranges = [r['satellite']['range_km'] for r in results if r['signal']['snr_db'] is not None]
    plt.scatter(ranges, snrs, c=snrs, cmap='viridis', alpha=0.7, s=30)
    plt.xlabel('Range (km)')
    plt.ylabel('SNR (dB)')
    plt.title('SNR vs Range')
    plt.colorbar(label='SNR (dB)')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()


def plot_antenna_tracking(results):
    """Create comprehensive antenna tracking plot."""
    azimuths = [r['satellite']['azimuth_deg'] for r in results]
    elevations = [r['satellite']['elevation_deg'] for r in results]
    antenna_az = [r['antenna']['antenna_az_deg'] for r in results]
    antenna_el = [r['antenna']['antenna_el_deg'] for r in results]
    pointing_errors = [r['antenna']['pointing_error_deg'] for r in results]
    in_beam = [r['antenna']['in_beam'] for r in results]
    
    plt.subplot(2, 2, 1)
    # Color points by lock status
    locked_az = [az for az, lock in zip(azimuths, in_beam) if lock]
    locked_el = [el for el, lock in zip(elevations, in_beam) if lock]
    unlocked_az = [az for az, lock in zip(azimuths, in_beam) if not lock]
    unlocked_el = [el for el, lock in zip(elevations, in_beam) if not lock]
    
    if locked_az:
        plt.scatter(locked_az, locked_el, c='green', s=20, alpha=0.7, label='Locked')
    if unlocked_az:
        plt.scatter(unlocked_az, unlocked_el, c='red', s=20, alpha=0.7, label='Unlocked')
    
    plt.plot(antenna_az, antenna_el, 'b--', linewidth=2, alpha=0.7, label='Antenna Path')
    plt.xlabel('Azimuth (degrees)')
    plt.ylabel('Elevation (degrees)')
    plt.title('Antenna Tracking vs Satellite Position')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 2)
    times = range(len(pointing_errors))
    plt.plot(times, pointing_errors, 'g-', linewidth=2)
    plt.axhline(y=CONFIG['antenna']['beamwidth_deg']/2, color='r', linestyle='--', 
               alpha=0.5, label=f'Beamwidth/2 ({CONFIG["antenna"]["beamwidth_deg"]/2:.1f}°)')
    plt.xlabel('Time Step')
    plt.ylabel('Pointing Error (degrees)')
    plt.title('Pointing Error vs Time')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 3)
    # Lock status over time
    lock_status = [1 if lock else 0 for lock in in_beam]
    plt.plot(times, lock_status, 'b-', linewidth=2)
    plt.xlabel('Time Step')
    plt.ylabel('Lock Status')
    plt.title('Antenna Lock Status Over Time')
    plt.yticks([0, 1], ['Unlocked', 'Locked'])
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 4)
    # Pointing error histogram
    valid_errors = [err for err in pointing_errors if err < 999]
    if valid_errors:
        plt.hist(valid_errors, bins=20, alpha=0.7, color='green', edgecolor='black')
            plt.axvline(x=CONFIG['antenna']['beamwidth_deg']/2, color='r', linestyle='--',
                    alpha=0.5, label=f'Beamwidth/2 ({CONFIG["antenna"]["beamwidth_deg"]/2:.1f}°)')
        plt.xlabel('Pointing Error (degrees)')
        plt.ylabel('Frequency')
        plt.title('Pointing Error Distribution')
        plt.legend()
        plt.grid(True, alpha=0.3)
    
    plt.tight_layout()


def plot_3d_trajectory(results):
    """Create 3D trajectory visualization."""
    from mpl_toolkits.mplot3d import Axes3D
    
    # Extract data
    ranges = [r['satellite']['range_km'] for r in results]
    azimuths = [r['satellite']['azimuth_deg'] for r in results]
    elevations = [r['satellite']['elevation_deg'] for r in results]
    
    # Convert to 3D coordinates
    x = [r * math.cos(math.radians(az)) * math.cos(math.radians(el)) for r, az, el in zip(ranges, azimuths, elevations)]
    y = [r * math.sin(math.radians(az)) * math.cos(math.radians(el)) for r, az, el in zip(ranges, azimuths, elevations)]
    z = [r * math.sin(math.radians(el)) for r, el in zip(ranges, elevations)]
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot trajectory
    ax.plot(x, y, z, 'b-', linewidth=2, alpha=0.8, label='Satellite Trajectory')
    
    # Color points by elevation
    scatter_plot = ax.scatter(x, y, z, c=elevations, cmap='viridis', s=20, alpha=0.7)
    
    # Add ground station at origin
    ax.scatter([0], [0], [0], c='red', s=100, marker='^', label='Ground Station')
    
    ax.set_xlabel('X (km)')
    ax.set_ylabel('Y (km)')
    ax.set_zlabel('Z (km)')
    ax.set_title('3D Satellite Trajectory')
    
    # Add colorbar
    cbar = plt.colorbar(scatter_plot, ax=ax, shrink=0.8, aspect=20)
    cbar.set_label('Elevation (degrees)')
    
    ax.legend()
    plt.tight_layout()


def plot_signal_spectrum(results):
    """Create signal spectrum analysis."""
    # Extract Doppler shifts
    dopplers = [r['signal']['doppler_hz'] for r in results if r['signal']['doppler_hz'] is not None]
    snrs = [r['signal']['snr_db'] for r in results if r['signal']['snr_db'] is not None]
    
    if not dopplers:
        plt.text(0.5, 0.5, 'No signal data available', ha='center', va='center', transform=plt.gca().transAxes)
        return
    
    plt.subplot(2, 1, 1)
    plt.hist(dopplers, bins=30, alpha=0.7, color='blue', edgecolor='black')
    plt.xlabel('Doppler Shift (Hz)')
    plt.ylabel('Frequency')
    plt.title('Doppler Shift Distribution')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 1, 2)
    plt.hist(snrs, bins=30, alpha=0.7, color='green', edgecolor='black')
    plt.axvline(x=10, color='r', linestyle='--', alpha=0.5, label='10 dB threshold')
    plt.xlabel('SNR (dB)')
    plt.ylabel('Frequency')
    plt.title('SNR Distribution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()


def get_current_status(results, current_time_sec=None):
    """
    Get current simulation status for a given time.
    
    Args:
        results: Simulation results
        current_time_sec: Current time in seconds (default: latest)
    
    Returns:
        dict: Current status data
    """
    if not results:
        return None
    
    if current_time_sec is None:
        # Get latest valid result
        valid_results = [r for r in results if r['satellite']['elevation_deg'] >= 0]
        if not valid_results:
            return None
        current_result = valid_results[-1]
    else:
        # Find result closest to current time
        current_result = min(results, key=lambda x: abs(x['time_sec'] - current_time_sec))
    
    return {
        'time_sec': current_result['time_sec'],
        'satellite': {
            'azimuth_deg': round(current_result['satellite']['azimuth_deg'], 2),
            'elevation_deg': round(current_result['satellite']['elevation_deg'], 2),
            'range_km': round(current_result['satellite']['range_km'], 1),
            'altitude_km': current_result['satellite']['altitude_km']
        },
        'signal': {
            'doppler_hz': round(current_result['signal']['doppler_hz'], 1) if current_result['signal']['doppler_hz'] else None,
            'snr_db': round(current_result['signal']['snr_db'], 1) if current_result['signal']['snr_db'] else None,
            'path_loss_db': round(current_result['signal']['path_loss_db'], 1) if current_result['signal']['path_loss_db'] else None
        },
        'antenna': {
            'azimuth_deg': round(current_result['antenna']['antenna_az_deg'], 2),
            'elevation_deg': round(current_result['antenna']['antenna_el_deg'], 2),
            'pointing_error_deg': round(current_result['antenna']['pointing_error_deg'], 2),
            'in_beam': current_result['antenna']['in_beam']
        }
    }


@app.route('/')
def index():
    """Main dashboard page."""
    global simulation_results
    
    # Run simulation if not already done
    if simulation_results is None:
        print("Running simulation...")
        simulation_results = run_simulation(CONFIG)
    
    # Get current status
    current_status = get_current_status(simulation_results)
    
    # Create all plots
    orbit_plot = create_plot_image(plot_orbit_overview, simulation_results)
    signal_plot = create_plot_image(plot_signal_metrics, simulation_results)
    tracking_plot = create_plot_image(plot_antenna_tracking, simulation_results)
    
    # Create additional plots
    try:
        trajectory_3d_plot = create_plot_image(plot_3d_trajectory, simulation_results)
        spectrum_plot = create_plot_image(plot_signal_spectrum, simulation_results)
    except ImportError:
        # Fallback if 3D plotting not available
        trajectory_3d_plot = None
        spectrum_plot = create_plot_image(plot_signal_spectrum, simulation_results)
    
    return render_template('demo_dashboard.html',
                         orbit_plot=orbit_plot,
                         signal_plot=signal_plot,
                         tracking_plot=tracking_plot,
                         trajectory_3d_plot=trajectory_3d_plot,
                         spectrum_plot=spectrum_plot,
                         current_status=current_status,
                         config=CONFIG)


@app.route('/api/status')
def api_status():
    """API endpoint to get current simulation status."""
    global simulation_results
    
    if simulation_results is None:
        return jsonify({'error': 'Simulation not run'})
    
    current_time = request.args.get('time', type=float)
    status = get_current_status(simulation_results, current_time)
    
    if status is None:
        return jsonify({'error': 'No valid data for requested time'})
    
    return jsonify(status)


@app.route('/api/config')
def api_config():
    """API endpoint to get current configuration."""
    return jsonify(CONFIG)


@app.route('/api/restart')
def api_restart():
    """API endpoint to restart simulation."""
    global simulation_results
    simulation_results = None
    return jsonify({'message': 'Simulation restarted'})


@app.route('/api/summary')
def api_summary():
    """API endpoint to get simulation summary."""
    global simulation_results
    
    if simulation_results is None:
        return jsonify({'error': 'Simulation not run'})
    
    # Calculate summary statistics
    visible_points = sum(1 for r in simulation_results if r['satellite']['elevation_deg'] >= 0)
    total_points = len(simulation_results)
    
    valid_signals = [r for r in simulation_results if r['signal']['snr_db'] is not None]
    in_beam_count = sum(1 for r in simulation_results if r['antenna']['in_beam'])
    
    summary = {
        'total_time_sec': CONFIG['duration_sec'],
        'total_points': total_points,
        'visible_points': visible_points,
        'visibility_percent': round(visible_points / total_points * 100, 1),
        'in_beam_points': in_beam_count,
        'tracking_accuracy_percent': round(in_beam_count / visible_points * 100, 1) if visible_points > 0 else 0
    }
    
    if valid_signals:
        snrs = [r['signal']['snr_db'] for r in valid_signals]
        dopplers = [r['signal']['doppler_hz'] for r in valid_signals]
        
        summary.update({
            'avg_snr_db': round(sum(snrs) / len(snrs), 1),
            'min_snr_db': round(min(snrs), 1),
            'max_snr_db': round(max(snrs), 1),
            'avg_doppler_hz': round(sum(dopplers) / len(dopplers), 1),
            'min_doppler_hz': round(min(dopplers), 1),
            'max_doppler_hz': round(max(dopplers), 1)
        })
    
    return jsonify(summary)


@app.route('/api/real_time')
def api_real_time():
    """Real-time data streaming endpoint."""
    global simulation_results
    
    if simulation_results is None:
        return jsonify({'error': 'Simulation not run'})
    
    # Get current time from request
    current_time = request.args.get('time', type=float)
    if current_time is None:
        current_time = 0
    
    # Find data for current time
    current_data = None
    for result in simulation_results:
        if result['time_sec'] >= current_time:
            current_data = result
            break
    
    if current_data is None:
        current_data = simulation_results[-1]
    
    return jsonify({
        'time_sec': current_data['time_sec'],
        'satellite': current_data['satellite'],
        'signal': current_data['signal'],
        'antenna': current_data['antenna']
    })


# Create templates directory and HTML template
def create_html_template():
    """Create the enhanced HTML template for the dashboard."""
    template_dir = 'demo/templates'
    os.makedirs(template_dir, exist_ok=True)
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LEO Flyby Emulator Demo Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .status-panel {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .status-panel h2 {
            color: #4a5568;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 15px;
        }
        
        .status-item {
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .status-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .status-item h3 {
            margin: 0 0 10px 0;
            color: #4a5568;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-value {
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .status-unit {
            font-size: 12px;
            color: #718096;
            font-weight: 500;
        }
        
        .controls {
            text-align: center;
            margin: 30px 0;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            margin: 0 10px;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        .plots-section {
            margin-top: 40px;
        }
        
        .plot-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .plot-container h2 {
            color: #4a5568;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .plot-container img {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .summary {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 25px;
            border-radius: 15px;
            margin-top: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .summary h3 {
            margin-top: 0;
            color: #4a5568;
            font-size: 1.3em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .summary p {
            margin: 8px 0;
            color: #4a5568;
            font-size: 14px;
        }
        
        .summary strong {
            color: #667eea;
        }
        
        .lock-indicator {
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
        }
        
        .lock-indicator.locked {
            background: #48bb78;
            box-shadow: 0 0 10px rgba(72, 187, 120, 0.5);
        }
        
        .lock-indicator.unlocked {
            background: #f56565;
            box-shadow: 0 0 10px rgba(245, 101, 101, 0.5);
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: white;
        }
        
        .spinner {
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top: 4px solid white;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .status-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
            }
            
            .status-value {
                font-size: 24px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛰️ LEO Flyby Signal Emulator Demo Dashboard</h1>
            <p>Real-time satellite tracking and signal analysis simulation</p>
        </div>
        
        <div class="status-panel">
            <h2>📡 Current Status</h2>
            <div class="status-grid">
                <div class="status-item">
                    <h3>Satellite Azimuth</h3>
                    <div class="status-value">{{ current_status.satellite.azimuth_deg }}</div>
                    <div class="status-unit">degrees</div>
                </div>
                <div class="status-item">
                    <h3>Satellite Elevation</h3>
                    <div class="status-value">{{ current_status.satellite.elevation_deg }}</div>
                    <div class="status-unit">degrees</div>
                </div>
                <div class="status-item">
                    <h3>Range</h3>
                    <div class="status-value">{{ current_status.satellite.range_km }}</div>
                    <div class="status-unit">km</div>
                </div>
                <div class="status-item">
                    <h3>Doppler Shift</h3>
                    <div class="status-value">{{ current_status.signal.doppler_hz or 'N/A' }}</div>
                    <div class="status-unit">Hz</div>
                </div>
                <div class="status-item">
                    <h3>SNR</h3>
                    <div class="status-value">{{ current_status.signal.snr_db or 'N/A' }}</div>
                    <div class="status-unit">dB</div>
                </div>
                <div class="status-item">
                    <h3>Antenna Lock</h3>
                    <div class="status-value">
                        <span class="lock-indicator {{ 'locked' if current_status.antenna.in_beam else 'unlocked' }}"></span>
                        {{ 'Locked' if current_status.antenna.in_beam else 'No Lock' }}
                    </div>
                    <div class="status-unit">Pointing Error: {{ current_status.antenna.pointing_error_deg }}°</div>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="restartSimulation()">🔄 Restart Simulation</button>
            <button class="btn" onclick="refreshStatus()">📊 Refresh Status</button>
            <button class="btn" onclick="toggleRealTime()">⏱️ Toggle Real-time</button>
        </div>
        
        <div class="plots-section">
            <div class="plot-container">
                <h2>🛰️ Orbit Overview</h2>
                <img src="data:image/png;base64,{{ orbit_plot }}" alt="Orbit Overview">
            </div>
            
            <div class="plot-container">
                <h2>📡 Signal Metrics</h2>
                <img src="data:image/png;base64,{{ signal_plot }}" alt="Signal Metrics">
            </div>
            
            <div class="plot-container">
                <h2>🎯 Antenna Tracking</h2>
                <img src="data:image/png;base64,{{ tracking_plot }}" alt="Antenna Tracking">
            </div>
            
            {% if trajectory_3d_plot %}
            <div class="plot-container">
                <h2>🌍 3D Trajectory</h2>
                <img src="data:image/png;base64,{{ trajectory_3d_plot }}" alt="3D Trajectory">
            </div>
            {% endif %}
            
            <div class="plot-container">
                <h2>📊 Signal Spectrum</h2>
                <img src="data:image/png;base64,{{ spectrum_plot }}" alt="Signal Spectrum">
            </div>
        </div>
        
        <div class="summary">
            <h3>📋 Simulation Configuration</h3>
            <p><strong>Duration:</strong> {{ config.duration_sec }} seconds ({{ "%.1f"|format(config.duration_sec/60) }} minutes)</p>
            <p><strong>Time Step:</strong> {{ config.time_step_sec }} seconds</p>
            <p><strong>Satellite Altitude:</strong> {{ config.satellite.altitude_km }} km</p>
            <p><strong>Carrier Frequency:</strong> {{ "%.1f"|format(config.signal.frequency_hz/1e9) }} GHz</p>
            <p><strong>Antenna Beamwidth:</strong> {{ config.antenna.beamwidth_deg }}°</p>
            <p><strong>Ground Station:</strong> {{ "%.4f"|format(config.ground_station.latitude_deg) }}°N, {{ "%.4f"|format(config.ground_station.longitude_deg) }}°E</p>
        </div>
    </div>
    
    <script>
        let realTimeInterval = null;
        let currentTime = 0;
        
        function restartSimulation() {
            fetch('/api/restart')
                .then(response => response.json())
                .then(data => {
                    alert('Simulation restarted! Refreshing page...');
                    location.reload();
                });
        }
        
        function refreshStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    console.log('Current status:', data);
                    updateStatusDisplay(data);
                });
        }
        
        function updateStatusDisplay(data) {
            // Update status values in real-time
            const statusItems = document.querySelectorAll('.status-item');
            statusItems.forEach(item => {
                const valueDiv = item.querySelector('.status-value');
                const unitDiv = item.querySelector('.status-unit');
                const title = item.querySelector('h3').textContent;
                
                switch(title) {
                    case 'Satellite Azimuth':
                        valueDiv.textContent = data.satellite.azimuth_deg;
                        break;
                    case 'Satellite Elevation':
                        valueDiv.textContent = data.satellite.elevation_deg;
                        break;
                    case 'Range':
                        valueDiv.textContent = data.satellite.range_km;
                        break;
                    case 'Doppler Shift':
                        valueDiv.textContent = data.signal.doppler_hz || 'N/A';
                        break;
                    case 'SNR':
                        valueDiv.textContent = data.signal.snr_db || 'N/A';
                        break;
                    case 'Antenna Lock':
                        const lockIndicator = valueDiv.querySelector('.lock-indicator');
                        const lockText = valueDiv.childNodes[1];
                        lockIndicator.className = 'lock-indicator ' + (data.antenna.in_beam ? 'locked' : 'unlocked');
                        lockText.textContent = data.antenna.in_beam ? 'Locked' : 'No Lock';
                        unitDiv.textContent = 'Pointing Error: ' + data.antenna.pointing_error_deg + '°';
                        break;
                }
            });
        }
        
        function toggleRealTime() {
            if (realTimeInterval) {
                clearInterval(realTimeInterval);
                realTimeInterval = null;
                console.log('Real-time updates stopped');
            } else {
                realTimeInterval = setInterval(() => {
                    currentTime += {{ config.time_step_sec }};
                    fetch(`/api/real_time?time=${currentTime}`)
                        .then(response => response.json())
                        .then(data => {
                            updateStatusDisplay(data);
                        });
                }, 1000);
                console.log('Real-time updates started');
            }
        }
        
        // Auto-refresh status every 5 seconds
        setInterval(refreshStatus, 5000);
        
        // Initialize real-time mode
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Dashboard loaded successfully');
        });
    </script>
</body>
</html>'''
    
    with open(f'{template_dir}/demo_dashboard.html', 'w', encoding='utf-8', errors='ignore') as f:
        f.write(html_content)


def main():
    """Main function to run the enhanced Flask demo dashboard."""
    print("🛰️ Enhanced LEO Flyby Emulator Demo Dashboard")
    print("=" * 50)
    
    # Create HTML template
    create_html_template()
    
    print("🚀 Starting enhanced Flask demo dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5001")
    print("🎯 Features:")
    print("   • Real-time satellite tracking")
    print("   • Comprehensive signal analysis")
    print("   • Interactive antenna tracking visualization")
    print("   • 3D trajectory plots")
    print("   • Signal spectrum analysis")
    print("   • Modern responsive UI")
    print("\n⏹️  Press Ctrl+C to stop the server")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5001, debug=False)


if __name__ == "__main__":
    main() 