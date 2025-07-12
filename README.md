# 🛰️ LEO Flyby Signal Emulator

A comprehensive Python-based simulator for Low Earth Orbit (LEO) satellite flyby communications, featuring realistic signal modeling, antenna tracking, and interactive dashboards.

## 📋 Description

The LEO Flyby Signal Emulator simulates the complete communication link between a ground station and a passing LEO satellite. It models orbital dynamics, signal propagation characteristics (Doppler shift, path loss, SNR), antenna tracking behavior, and provides both command-line and web-based interfaces for analysis and visualization.

The project includes both a full-featured version with external dependencies and a lightweight dependency-free demo version for quick testing and educational purposes.

## ✨ Features

### 🛰️ **Orbit Simulation**
- TLE-based satellite orbit calculations using Skyfield
- Realistic orbital mechanics and ground track prediction
- Configurable ground station locations and observation windows
- Horizon detection and visibility calculations

### 📡 **Signal Modeling**
- **Doppler Shift**: Frequency shift due to relative motion
- **Path Loss**: Free-space path loss with atmospheric attenuation
- **SNR Calculation**: Complete link budget analysis
- **Noise Modeling**: Realistic thermal and system noise
- **Atmospheric Effects**: Tropospheric and ionospheric impacts

### 🎯 **Antenna Tracking**
- Realistic antenna pointing simulation
- Configurable beamwidth and slew rate limitations
- Pointing error modeling and lock status tracking
- 2D and 3D visualization of tracking performance

### 🔌 **API Interface**
- Thread-safe mock API for external system integration
- Real-time data streaming with configurable update rates
- Command/response logging and error handling
- Robot receiver simulation for antenna control

### 📊 **Interactive Dashboards**
- **Flask Dashboard**: Real-time web interface with Plotly visualizations
- **Demo Dashboard**: Lightweight version with Matplotlib plots
- Interactive parameter controls and live data updates
- Multiple plot types (orbit, signal metrics, antenna tracking)

### 🧪 **Testing & Validation**
- Comprehensive unit tests for core modules
- Pytest-based test suite with coverage reporting
- Mock data generation for testing scenarios
- Error handling and edge case validation

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/LEO_Flyby_Signal_Emulator.git
cd LEO_Flyby_Signal_Emulator
```

### 2. Install Dependencies

#### For Full Project (with external dependencies):
```bash
pip install -r requirements.txt
```

#### For Demo Version (dependency-free):
```bash
# Only requires matplotlib for plotting
pip install matplotlib
```

### 3. Run the Project

#### Main Project Options:
```bash
# Interactive Jupyter notebook
jupyter notebook demo.ipynb

# Flask dashboard (full version)
python gui_dashboard/flask_app.py

# Command-line simulation
python flyby_model/orbit_sim.py
```

#### Demo Version Options:
```bash
# Command-line demo with plots
python demo/demo.py

# Flask demo dashboard
python demo/demo_flask_app.py
```

## 📊 Sample Run

### Demo Version Output:
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

### Dashboard Access:
- **Main Dashboard**: http://localhost:5000
- **Demo Dashboard**: http://localhost:5001

## 📦 Dependencies

### Full Project Dependencies:
- `numpy` - Numerical computations
- `skyfield` - Astronomical calculations and TLE processing
- `plotly` - Interactive visualizations
- `flask` - Web dashboard framework
- `pyyaml` - Configuration file parsing
- `pytest` - Testing framework
- `matplotlib` - Static plotting

### Demo Version Dependencies:
- `matplotlib` - Plotting (optional, falls back gracefully)

## 🎮 Usage

### Quick Start (Demo Version)
```bash
# Run basic simulation with plots
python demo/demo.py

# Launch web dashboard
python demo/demo_flask_app.py
```

### Full Project Usage
```bash
# Interactive exploration
jupyter notebook demo.ipynb

# Web dashboard with real-time updates
python gui_dashboard/flask_app.py

# Run tests
pytest tests/

# API integration example
python api_interface/xlapi_mock.py
```

### Configuration
Edit `config/sim_config.yaml` to customize:
- Ground station coordinates
- Satellite TLE data
- Signal parameters
- Simulation timing
- Antenna specifications

## 📁 Project Structure

```
LEO_Flyby_Signal_Emulator/
├── config/
│   └── sim_config.yaml          # Configuration file
├── flyby_model/
│   ├── orbit_sim.py             # Orbit simulation
│   ├── signal_model.py          # Signal calculations
│   └── tracking_sim.py          # Antenna tracking
├── api_interface/
│   ├── xlapi_mock.py            # Mock API interface
│   └── robot_receiver.py        # Receiver simulation
├── gui_dashboard/
│   ├── flask_app.py             # Main Flask dashboard
│   └── plotter.py               # Plotly visualizations
├── demo/
│   ├── demo.py                  # Dependency-free demo
│   ├── demo_flask_app.py        # Demo Flask dashboard
│   └── demo.ipynb               # Jupyter notebook
├── tests/
│   ├── test_orbit_sim.py        # Orbit simulation tests
│   └── test_signal_model.py     # Signal model tests
├── data/
│   └── plots/                   # Generated plots
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔧 API Endpoints

### Main Dashboard (`localhost:5000`)
- `GET /` - Main dashboard page
- `GET /api/status` - Current simulation status
- `GET /api/config` - Configuration parameters
- `POST /api/update_config` - Update configuration
- `GET /api/plots` - Generated plot images

### Demo Dashboard (`localhost:5001`)
- `GET /` - Demo dashboard page
- `GET /api/status` - Current status
- `GET /api/config` - Configuration
- `GET /api/restart` - Restart simulation
- `GET /api/summary` - Simulation summary

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=flyby_model tests/

# Run specific test file
pytest tests/test_orbit_sim.py
```

## 📈 Performance

- **Simulation Speed**: ~1000 time steps/second
- **Memory Usage**: <100 MB for typical simulations
- **Plot Generation**: Real-time updates
- **API Response**: <50ms for status queries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Skyfield](https://rhodesmill.org/skyfield/) for astronomical calculations
- [Plotly](https://plotly.com/) for interactive visualizations
- [Flask](https://flask.palletsprojects.com/) for web framework
- NASA for TLE data and orbital mechanics

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the documentation in `docs/`
- Review the example notebooks in `demo/`

---

**Happy Satellite Tracking! 🛰️📡** 