# 📖 LEO Flyby Signal Emulator - User Manual

## 📋 Overview

The LEO Flyby Signal Emulator is a comprehensive Python-based simulator for Low Earth Orbit (LEO) satellite communications. It models orbital dynamics, signal propagation, and antenna tracking to provide realistic satellite flyby simulations.

The project includes both a **full-featured version** with external dependencies and a **lightweight demo version** that requires minimal setup.

## 🚀 Quick Start - Demo Version

The demo version is designed to be **dependency-free** and provides a quick way to understand the core concepts without complex setup.

### Running the Demo

#### 1. Command-Line Demo
```bash
# Run the basic simulation with plots
python demo/demo.py
```

**Expected Output:**
```
LEO Satellite Flyby Emulator Demo
========================================
Starting LEO Flyby Simulation...
Duration: 600 seconds (10.0 minutes)
Time step: 1 seconds
Simulation completed. Generated 601 data points.

=== Simulation Summary ===
Total simulation time: 600 seconds
Satellite visible: 245/601 points (40.8%)

Signal Statistics:
  Average SNR: 15.2 dB
  SNR range: 8.1 to 22.3 dB
  Average Doppler shift: 62.4 Hz
  Doppler range: -45.2 to 145.8 Hz

Tracking Statistics:
  In beam: 238/245 points (97.1%)
  Beamwidth: 10°

✓ Simulation completed successfully!
```

**Generated Files:**
- `data/plots/demo_overview.png` - Orbit and signal overview
- `data/plots/demo_tracking.png` - Antenna tracking visualization

#### 2. Web Dashboard Demo
```bash
# Launch the demo Flask dashboard
python demo/demo_flask_app.py
```

**Access:** http://localhost:5001

**Features:**
- Real-time satellite status display
- Interactive plots (orbit, signal metrics, antenna tracking)
- Simulation controls (restart, refresh)
- API endpoints for data access

## 🛠️ Full Project Setup

### Prerequisites
- Python 3.8 or higher
- Git
- pip (Python package installer)

### Step-by-Step Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/LEO_Flyby_Signal_Emulator.git
cd LEO_Flyby_Signal_Emulator
```

#### 2. Create Virtual Environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Verify Installation
```bash
python -c "import skyfield, plotly, flask, yaml; print('All dependencies installed successfully!')"
```

### Running the Full Project

#### 1. Interactive Jupyter Notebook
```bash
jupyter notebook demo.ipynb
```

**Features:**
- Step-by-step simulation walkthrough
- Interactive parameter adjustment
- Real-time visualization
- Educational explanations

#### 2. Flask Dashboard
```bash
python gui_dashboard/flask_app.py
```

**Access:** http://localhost:5000

**Features:**
- Real-time simulation monitoring
- Interactive Plotly visualizations
- Parameter controls
- Data export capabilities

#### 3. Command-Line Simulation
```bash
# Run orbit simulation
python flyby_model/orbit_sim.py

# Run signal modeling
python flyby_model/signal_model.py

# Run antenna tracking
python flyby_model/tracking_sim.py
```

#### 4. API Interface
```bash
# Start mock API server
python api_interface/xlapi_mock.py

# In another terminal, run receiver
python api_interface/robot_receiver.py
```

## 🔧 Configuration

### Demo Configuration
The demo uses a simple Python dictionary in `demo/demo.py`:

```python
CONFIG = {
    'duration_sec': 600,      # 10 minutes
    'time_step_sec': 1,       # 1 second intervals
    'satellite': {
        'altitude_km': 500,   # Circular orbit altitude
        'velocity_km_s': 7.8, # Orbital velocity
    },
    # ... more parameters
}
```

### Full Project Configuration
Edit `config/sim_config.yaml`:

```yaml
ground_station:
  latitude_deg: 37.7749    # San Francisco
  longitude_deg: -122.4194
  elevation_m: 10

satellite:
  tle_file: "data/satellites.txt"
  # ... more parameters
```

## 🧪 Testing

### Run Unit Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=flyby_model tests/

# Run specific test
pytest tests/test_orbit_sim.py
```

### Expected Test Output
```
============================= test session starts =============================
platform win32 -- Python 3.9.7, pytest-6.2.5, py-1.10.0, pluggy-0.13.1
collected 8 items

tests/test_orbit_sim.py ....                                           [ 50%]
tests/test_signal_model.py ....                                        [100%]

============================== 8 passed in 2.34s ==============================
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Missing Dependencies
**Error:** `ModuleNotFoundError: No module named 'skyfield'`

**Solution:**
```bash
pip install -r requirements.txt
```

#### 2. Port Conflicts
**Error:** `Address already in use`

**Solutions:**
- Change port in `gui_dashboard/flask_app.py`:
  ```python
  app.run(host='0.0.0.0', port=5002, debug=False)  # Change 5000 to 5002
  ```
- Or kill existing process:
  ```bash
  # Windows
  netstat -ano | findstr :5000
  taskkill /PID <PID> /F
  
  # macOS/Linux
  lsof -ti:5000 | xargs kill -9
  ```

#### 3. Missing TLE File
**Error:** `FileNotFoundError: data/satellites.txt`

**Solution:**
```bash
# Create data directory
mkdir -p data

# Download sample TLE data
curl -o data/satellites.txt "https://www.celestrak.com/NORAD/elements/stations.txt"
```

#### 4. Matplotlib Backend Issues
**Error:** `RuntimeError: Invalid DISPLAY variable`

**Solution:**
```python
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
```

#### 5. Jupyter Notebook Issues
**Error:** `jupyter: command not found`

**Solution:**
```bash
pip install jupyter
```

### Performance Issues

#### Slow Simulation
- Reduce time step in configuration
- Use fewer data points
- Close other applications

#### Memory Issues
- Reduce simulation duration
- Use smaller TLE datasets
- Restart Python kernel

## 📁 Expected Outputs

### Demo Version Outputs
```
demo/
├── demo.py                    # Main demo script
├── demo_flask_app.py          # Demo dashboard
└── templates/
    └── demo_dashboard.html    # Auto-generated template

data/
├── plots/
│   ├── demo_overview.png      # Orbit and signal plots
│   └── demo_tracking.png      # Antenna tracking plot
└── logs/                      # Simulation logs (if enabled)
```

### Full Project Outputs
```
data/
├── plots/
│   ├── orbit_2d.png          # 2D orbit visualization
│   ├── orbit_3d.html         # Interactive 3D plot
│   ├── signal_metrics.html   # Signal analysis
│   └── antenna_tracking.html # Tracking performance
├── logs/
│   ├── orbit_sim.log         # Orbit simulation logs
│   ├── signal_model.log      # Signal modeling logs
│   └── tracking_sim.log      # Tracking simulation logs
└── satellites.txt            # TLE data file
```

### Log Files
Log files contain detailed simulation information:
- Satellite positions and velocities
- Signal calculations and parameters
- Antenna pointing and tracking data
- Error messages and warnings
- Performance metrics

## 📞 Getting Help

### Documentation
- `README.md` - Project overview and quick start
- `user_guide.md` - Technical details and code explanation
- `demo.ipynb` - Interactive tutorial

### Support
- Check the troubleshooting section above
- Review log files in `data/logs/`
- Open an issue on GitHub
- Check the example configurations

### Useful Commands
```bash
# Check Python version
python --version

# List installed packages
pip list

# Check if virtual environment is active
echo $VIRTUAL_ENV  # Unix
echo %VIRTUAL_ENV% # Windows

# Update dependencies
pip install --upgrade -r requirements.txt

# Clean generated files
rm -rf data/plots/* data/logs/*
```

---

**Happy Satellite Tracking! 🛰️📡** 