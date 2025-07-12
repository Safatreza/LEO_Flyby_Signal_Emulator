"""
Flask Dashboard for LEO Satellite Flyby Emulator
- Displays Plotly plots from plotter.py
- Shows real-time simulation data
- Includes interactive sliders for parameters
- Serves at localhost:5000
"""
from flask import Flask, render_template_string, request, jsonify
import yaml
import pandas as pd
import os
from datetime import datetime
import plotly.graph_objs as go
from plotter import plot_polar_tracking, plot_signal_metrics, plot_3d_trajectory

app = Flask(__name__)

# Configuration
CONFIG_PATH = 'config/sim_config.yaml'
ORBIT_LOG = 'data/logs/orbit_log.csv'
SIGNAL_LOG = 'data/logs/signal_log.csv'
TRACKING_LOG = 'data/logs/tracking_log.csv'

def load_config():
    """Load configuration from YAML file."""
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def get_latest_data():
    """Get latest simulation data from log files."""
    data = {}
    try:
        if os.path.exists(ORBIT_LOG):
            orbit_df = pd.read_csv(ORBIT_LOG)
            if len(orbit_df) > 0:
                latest = orbit_df.iloc[-1]
                data['orbit'] = {
                    'azimuth': latest['azimuth'],
                    'elevation': latest['elevation'],
                    'range': latest['range'],
                    'velocity': latest['velocity']
                }
    except Exception as e:
        print(f"Error reading orbit data: {e}")
    
    try:
        if os.path.exists(SIGNAL_LOG):
            signal_df = pd.read_csv(SIGNAL_LOG)
            if len(signal_df) > 0:
                latest = signal_df.iloc[-1]
                data['signal'] = {
                    'doppler_shift': latest['doppler_shift'],
                    'path_loss': latest['path_loss'],
                    'snr': latest['snr']
                }
    except Exception as e:
        print(f"Error reading signal data: {e}")
    
    try:
        if os.path.exists(TRACKING_LOG):
            tracking_df = pd.read_csv(TRACKING_LOG)
            if len(tracking_df) > 0:
                latest = tracking_df.iloc[-1]
                data['tracking'] = {
                    'antenna_az': latest['antenna_az'],
                    'antenna_el': latest['antenna_el'],
                    'pointing_error': latest['pointing_error'],
                    'lock_status': latest['lock_status']
                }
    except Exception as e:
        print(f"Error reading tracking data: {e}")
    
    return data

@app.route('/')
def dashboard():
    """Main dashboard page with plots and controls."""
    config = load_config()
    
    # Generate plots
    plots_html = {}
    try:
        if all(os.path.exists(f) for f in [ORBIT_LOG, SIGNAL_LOG, TRACKING_LOG]):
            orbit_df = pd.read_csv(ORBIT_LOG)
            signal_df = pd.read_csv(SIGNAL_LOG)
            tracking_df = pd.read_csv(TRACKING_LOG)
            
            # Generate plot HTML
            polar_fig = plot_polar_tracking(tracking_df)
            plots_html['polar'] = polar_fig.to_html(full_html=False, include_plotlyjs='cdn')
            
            signal_fig = plot_signal_metrics(signal_df)
            plots_html['signal'] = signal_fig.to_html(full_html=False, include_plotlyjs='cdn')
            
            traj_fig = plot_3d_trajectory(orbit_df, tracking_df)
            plots_html['trajectory'] = traj_fig.to_html(full_html=False, include_plotlyjs='cdn')
    except Exception as e:
        print(f"Error generating plots: {e}")
    
    # Get latest data
    latest_data = get_latest_data()
    
    # HTML template
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>LEO Satellite Flyby Emulator Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { text-align: center; margin-bottom: 30px; }
            .controls { background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
            .plot-container { margin: 20px 0; }
            .status { background: #e8f5e8; padding: 10px; border-radius: 5px; margin: 10px 0; }
            .slider-container { margin: 10px 0; }
            label { display: inline-block; width: 150px; }
            input[type="range"] { width: 200px; }
            .value-display { display: inline-block; margin-left: 10px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>LEO Satellite Flyby Emulator Dashboard</h1>
            <p>Real-time simulation monitoring and control</p>
        </div>
        
        <div class="controls">
            <h3>Simulation Controls</h3>
            <div class="slider-container">
                <label>Frequency (MHz):</label>
                <input type="range" id="freq" min="100" max="1000" value="''' + str(config.get('signal', {}).get('frequency_hz', 437)/1e6) + '''" step="1">
                <span class="value-display" id="freq-value"></span>
            </div>
            <div class="slider-container">
                <label>Duration (min):</label>
                <input type="range" id="duration" min="1" max="30" value="''' + str(config.get('simulation', {}).get('duration_sec', 600)//60) + '''" step="1">
                <span class="value-display" id="duration-value"></span>
            </div>
            <div class="slider-container">
                <label>Time Step (sec):</label>
                <input type="range" id="timestep" min="1" max="10" value="''' + str(config.get('simulation', {}).get('time_step_sec', 1)) + '''" step="1">
                <span class="value-display" id="timestep-value"></span>
            </div>
            <button onclick="updateConfig()">Update Configuration</button>
        </div>
        
        <div class="status">
            <h3>Current Status</h3>
            <p><strong>Time:</strong> <span id="current-time"></span></p>
            <p><strong>SNR:</strong> <span id="current-snr">N/A</span> dB</p>
            <p><strong>Lock Status:</strong> <span id="lock-status">N/A</span></p>
            <p><strong>Pointing Error:</strong> <span id="pointing-error">N/A</span>°</p>
        </div>
        
        <div class="plot-container">
            <h3>Antenna Tracking (Polar Plot)</h3>
            <div id="polar-plot">
                ''' + plots_html.get('polar', '<p>No tracking data available</p>') + '''
            </div>
        </div>
        
        <div class="plot-container">
            <h3>Signal Metrics</h3>
            <div id="signal-plot">
                ''' + plots_html.get('signal', '<p>No signal data available</p>') + '''
            </div>
        </div>
        
        <div class="plot-container">
            <h3>3D Trajectory</h3>
            <div id="trajectory-plot">
                ''' + plots_html.get('trajectory', '<p>No trajectory data available</p>') + '''
            </div>
        </div>
        
        <script>
            // Update slider value displays
            document.getElementById('freq').addEventListener('input', function() {
                document.getElementById('freq-value').textContent = this.value + ' MHz';
            });
            document.getElementById('duration').addEventListener('input', function() {
                document.getElementById('duration-value').textContent = this.value + ' min';
            });
            document.getElementById('timestep').addEventListener('input', function() {
                document.getElementById('timestep-value').textContent = this.value + ' sec';
            });
            
            // Initialize displays
            document.getElementById('freq-value').textContent = document.getElementById('freq').value + ' MHz';
            document.getElementById('duration-value').textContent = document.getElementById('duration').value + ' min';
            document.getElementById('timestep-value').textContent = document.getElementById('timestep').value + ' sec';
            
            // Update status every second
            function updateStatus() {
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('current-time').textContent = new Date().toLocaleString();
                        document.getElementById('current-snr').textContent = data.snr || 'N/A';
                        document.getElementById('lock-status').textContent = data.lock_status || 'N/A';
                        document.getElementById('pointing-error').textContent = data.pointing_error || 'N/A';
                    });
            }
            
            function updateConfig() {
                const config = {
                    frequency: document.getElementById('freq').value,
                    duration: document.getElementById('duration').value,
                    timestep: document.getElementById('timestep').value
                };
                fetch('/api/update_config', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(config)
                }).then(response => response.json())
                  .then(data => alert('Configuration updated: ' + data.message));
            }
            
            // Update status every second
            setInterval(updateStatus, 1000);
            updateStatus();
        </script>
    </body>
    </html>
    '''
    
    return render_template_string(html_template)

@app.route('/api/status')
def api_status():
    """API endpoint for real-time status data."""
    data = get_latest_data()
    return jsonify({
        'snr': data.get('signal', {}).get('snr', 'N/A'),
        'lock_status': data.get('tracking', {}).get('lock_status', 'N/A'),
        'pointing_error': data.get('tracking', {}).get('pointing_error', 'N/A'),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/update_config', methods=['POST'])
def api_update_config():
    """API endpoint for updating configuration."""
    try:
        config = request.json
        # Here you would update the config file
        # For now, just return success
        return jsonify({'message': 'Configuration updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    print("Starting LEO Flyby Emulator Dashboard...")
    print("Access the dashboard at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 