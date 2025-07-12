# 📚 LEO Flyby Signal Emulator - User Guide

## 🎯 Project Purpose

The LEO Flyby Signal Emulator is designed to simulate and analyze Low Earth Orbit (LEO) satellite communication scenarios. It models the complete communication link between a ground station and a passing satellite, including:

- **Orbital Dynamics**: Realistic satellite motion and ground track prediction
- **Signal Characteristics**: Doppler shift, path loss, SNR, and atmospheric effects
- **Antenna Tracking**: Pointing accuracy, beamwidth limitations, and lock status
- **System Integration**: Mock API interfaces for testing ground station software

This project serves as both an educational tool for understanding satellite communications and a practical framework for testing and validating ground station systems.

## 🤔 Project Rationale

### Why This Project Matters

**Educational Value:**
- Demonstrates complex orbital mechanics concepts in an accessible way
- Shows real-world applications of physics and mathematics
- Provides hands-on experience with satellite communication systems

**Technical Skills Demonstrated:**
- **Python Programming**: Object-oriented design, data processing, visualization
- **Satellite Communications**: Link budget analysis, signal propagation modeling
- **System Integration**: API design, real-time data streaming, error handling
- **Data Visualization**: Interactive plots, real-time dashboards, 3D graphics
- **Software Engineering**: Modular architecture, testing, documentation

**Industry Relevance:**
- Ground station operations and testing
- Satellite communication system design
- Educational and training applications
- Research and development in space communications

## 🔧 Code Breakdown

### Core Simulation Modules

#### `flyby_model/orbit_sim.py`
**Purpose**: Computes satellite position using Skyfield and TLE data

**Key Functions:**
- `read_tle_file()`: Parses Two-Line Element (TLE) data
- `calculate_satellite_position()`: Uses Skyfield for precise orbital calculations
- `simulate_flyby()`: Generates time series of satellite positions
- `check_horizon()`: Determines satellite visibility from ground station

**Technical Details:**
```python
# Uses Skyfield for accurate astronomical calculations
from skyfield.api import load, wgs84
ts = load.timescale()
satellite = earth + Orbital(ts, tle_line1, tle_line2)
```

#### `flyby_model/signal_model.py`
**Purpose**: Models signal propagation characteristics

**Key Functions:**
- `calculate_doppler_shift()`: `f_d = (v_r / c) * f_0`
- `calculate_path_loss()`: Free-space path loss with atmospheric attenuation
- `calculate_snr()`: Complete link budget analysis
- `add_noise()`: Realistic thermal and system noise modeling

**Technical Details:**
```python
# Free-space path loss equation
FSPL = 20 * log10(d) + 20 * log10(f) + 20 * log10(4π/c)

# Link budget
SNR = P_tx + G_tx + G_rx - FSPL - N - L_atm
```

#### `flyby_model/tracking_sim.py`
**Purpose**: Simulates antenna tracking with realistic constraints

**Key Functions:**
- `simulate_antenna_motion()`: Models antenna pointing with slew rate limits
- `calculate_pointing_error()`: Determines tracking accuracy
- `check_lock_status()`: Evaluates if satellite is within antenna beam
- `generate_plots()`: Creates 2D and 3D tracking visualizations

**Technical Details:**
```python
# Antenna pointing with slew rate constraints
max_slew_rate = 10  # degrees/second
azimuth_change = min(azimuth_change, max_slew_rate * dt)

# Beamwidth check
pointing_error = sqrt((az_error)² + (el_error)²)
in_beam = pointing_error < beamwidth / 2
```

### API Interface Modules

#### `api_interface/xlapi_mock.py`
**Purpose**: Thread-safe mock API for external system integration

**Key Features:**
- Real-time data streaming with configurable update rates
- Command/response logging and error handling
- Queue-based data management for thread safety
- Simulates realistic API behavior and timing

**Technical Details:**
```python
# Thread-safe data queues
from queue import Queue
signal_queue = Queue()
antenna_queue = Queue()

# Real-time data streaming
def stream_data():
    while True:
        data = generate_simulation_data()
        signal_queue.put(data)
        time.sleep(update_interval)
```

#### `api_interface/robot_receiver.py`
**Purpose**: Virtual receiver that processes data from the mock API

**Key Features:**
- Simulates antenna movement based on received commands
- Computes pointing error and lock status
- Provides status feedback to the API
- Logs all operations for debugging

### Visualization Modules

#### `gui_dashboard/plotter.py`
**Purpose**: Interactive Plotly visualizations for real-time monitoring

**Key Features:**
- 2D polar plots for antenna pointing
- Time-series plots for signal metrics
- 3D trajectory visualization
- Real-time data updates

**Technical Details:**
```python
# Interactive 3D plot
fig = go.Figure(data=[go.Scatter3d(
    x=azimuths, y=elevations, z=ranges,
    mode='lines+markers',
    name='Satellite Trajectory'
)])
```

#### `gui_dashboard/flask_app.py`
**Purpose**: Web-based dashboard for real-time simulation monitoring

**Key Features:**
- Real-time data display and parameter controls
- Interactive visualizations with Plotly
- API endpoints for external integration
- Configuration management interface

### Demo Modules

#### `demo/demo.py`
**Purpose**: Simplified, dependency-free demonstration

**Key Features:**
- Uses only standard Python libraries (math, random)
- Matplotlib for basic plotting
- Simplified orbital model (circular orbit)
- Basic signal calculations
- No external dependencies required

**Technical Details:**
```python
# Simplified circular orbit
angular_velocity = velocity_km_s / orbital_radius
satellite_lon = (angular_velocity * time_sec) * 180 / math.pi

# Basic signal calculations
doppler_shift = (velocity_km_s * 1000 / C) * frequency_hz
path_loss = 20 * log10(range_m) + 20 * log10(frequency_hz) + 20 * log10(4 * math.pi / C)
```

#### `demo/demo_flask_app.py`
**Purpose**: Lightweight Flask dashboard for the demo version

**Key Features:**
- Base64-encoded plot images for web display
- Simple HTML template with modern styling
- API endpoints for status and control
- Runs on port 5001 to avoid conflicts

## 🎓 Demo Purpose

The demo version serves several important purposes:

### **Accessibility**
- **No Dependencies**: Runs with only Python standard library and Matplotlib
- **Quick Setup**: No complex installation or configuration required
- **Educational**: Perfect for understanding core concepts without distractions

### **Learning Objectives**
- **Orbital Mechanics**: Basic satellite motion and ground track
- **Signal Propagation**: Doppler shift, path loss, and SNR fundamentals
- **Antenna Tracking**: Pointing accuracy and beamwidth concepts
- **System Integration**: API design and data flow

### **Use Cases**
- **Classroom Demonstrations**: Quick satellite communication examples
- **Prototype Testing**: Validate concepts before full implementation
- **Educational Workshops**: Hands-on satellite tracking exercises
- **System Validation**: Test ground station software interfaces

## 🔬 Technical Details

### Orbital Mechanics

**Two-Body Problem:**
- Simplified gravitational model (Earth + satellite)
- Circular orbit approximation for demo version
- TLE-based precise calculations for full version

**Ground Track Calculation:**
```python
# Convert satellite position to ground station coordinates
lat_diff = satellite_lat - ground_station_lat
lon_diff = satellite_lon - ground_station_lon
range_km = sqrt((lat_diff * 111)² + (lon_diff * 111)² + altitude²)
```

### Link Budget Analysis

**Signal Power Budget:**
```
Received Power = Transmitted Power + Antenna Gains - Path Loss - Atmospheric Loss
SNR = Received Power - Noise Power
```

**Key Parameters:**
- **Transmit Power**: 20 dBm (typical for small satellites)
- **Antenna Gains**: 20 dB each (moderate gain antennas)
- **Path Loss**: Free-space + atmospheric attenuation
- **Noise**: Thermal noise + system noise floor

### Antenna Tracking Logic

**Pointing Algorithm:**
1. Calculate required azimuth and elevation from satellite position
2. Apply slew rate constraints to antenna movement
3. Add realistic pointing errors (mechanical, calibration)
4. Check if satellite is within antenna beamwidth
5. Update lock status based on pointing accuracy

**Beamwidth Considerations:**
- **Narrow Beam**: Higher gain, more precise tracking required
- **Wide Beam**: Lower gain, more forgiving tracking
- **Trade-off**: Signal strength vs. tracking complexity

## 🎯 Use Cases

### **Educational Applications**
- **University Courses**: Satellite communications, orbital mechanics
- **Workshops**: Hands-on satellite tracking exercises
- **Research**: Prototype testing and concept validation
- **Training**: Ground station operator training

### **Industry Applications**
- **Ground Station Testing**: Validate tracking algorithms and software
- **System Integration**: Test API interfaces and data flows
- **Performance Analysis**: Evaluate link budget and tracking accuracy
- **Risk Assessment**: Analyze communication reliability

### **Research Applications**
- **Algorithm Development**: Test new tracking or signal processing methods
- **Parameter Studies**: Analyze effects of different configurations
- **Performance Optimization**: Find optimal antenna and signal parameters
- **System Design**: Validate ground station architecture decisions

### **Development Applications**
- **Software Testing**: Unit and integration testing for satellite software
- **API Development**: Design and test communication interfaces
- **Data Analysis**: Process and visualize satellite communication data
- **System Validation**: Verify ground station performance requirements

## 🔮 Future Enhancements

### **Potential Improvements**
- **Multi-Satellite Support**: Track multiple satellites simultaneously
- **Advanced Signal Processing**: Implement modulation and coding schemes
- **Real-Time TLE Updates**: Automatic TLE data fetching and updates
- **3D Visualization**: Interactive 3D ground station and satellite models
- **Machine Learning**: AI-powered tracking and signal optimization
- **Hardware Integration**: Interface with real antenna control systems

### **Scalability Considerations**
- **Distributed Processing**: Handle multiple ground stations
- **Cloud Deployment**: Web-based access and collaboration
- **Database Integration**: Store and analyze historical data
- **API Standardization**: Industry-standard communication protocols

---

**This project demonstrates the power of Python for complex scientific and engineering applications, combining theoretical knowledge with practical implementation skills.** 🚀 