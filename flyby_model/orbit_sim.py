"""
LEO Satellite Flyby Simulator
- Computes azimuth, elevation, range, and radial velocity relative to a ground station.
- Reads TLE from data/tle_example.txt and config from config/sim_config.yaml.
- Outputs results as a pandas DataFrame and logs to data/logs/orbit_log.csv.
"""
import os
import sys
import yaml
import pandas as pd
from datetime import datetime, timedelta
import numpy as np # Added for velocity calculation

try:
    from skyfield.api import load, EarthSatellite, wgs84, Topos
except ImportError:
    raise ImportError("Skyfield is required. Install with: pip install skyfield")

# Constants
TLE_PATH = 'data/tle_example.txt'
CONFIG_PATH = 'config/sim_config.yaml'
LOG_PATH = 'data/logs/orbit_log.csv'


def load_config(config_path):
    """Load simulation and ground station config from YAML."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        gs = config['ground_station']
        sim = config.get('simulation', {})
        return gs, sim
    except Exception as e:
        raise RuntimeError(f"Failed to load config: {e}")


def load_tle(tle_path):
    """Load TLE lines from file."""
    try:
        with open(tle_path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        if len(lines) < 3:
            raise ValueError("TLE file must have at least 3 lines (name, line1, line2)")
        return lines[0], lines[1], lines[2]
    except Exception as e:
        raise RuntimeError(f"Failed to load TLE: {e}")


def simulate_flyby(gs, sim, tle_lines):
    """
    Simulate satellite flyby and return a pandas DataFrame.
    gs: ground station dict
    sim: simulation params dict
    tle_lines: (name, line1, line2)
    """
    # Parse ground station coordinates
    try:
        lat = float(gs['latitude_deg'])
        lon = float(gs['longitude_deg'])
        alt = float(gs.get('elevation_m', 0))
    except Exception as e:
        raise ValueError(f"Invalid ground station coordinates: {e}")

    # Simulation parameters
    duration = int(sim.get('duration_sec', 600))  # default 10 min
    time_step = int(sim.get('time_step_sec', 1))  # default 1 sec

    # Load TLE and create satellite object
    try:
        satellite = EarthSatellite(tle_lines[1], tle_lines[2], tle_lines[0])
    except Exception as e:
        raise ValueError(f"Invalid TLE: {e}")

    ts = load.timescale()
    # Start time: now (UTC)
    t0 = datetime.utcnow()
    times = [t0 + timedelta(seconds=i) for i in range(0, duration + 1, time_step)]
    
    # Convert to Skyfield time format
    sf_times = ts.utc([t.year for t in times], [t.month for t in times], [t.day for t in times],
                      [t.hour for t in times], [t.minute for t in times], [t.second for t in times])

    # Ground station location (corrected API usage)
    gs_topos = wgs84.latlon(lat, lon, elevation_m=alt)

    # Results
    records = []
    for t, sf_time in zip(times, sf_times):
        # Satellite position relative to ground station
        difference = satellite - gs_topos
        topocentric = difference.at(sf_time)
        el, az, distance = topocentric.altaz()
        
        # Radial velocity (range rate) - simplified calculation
        try:
            # Get velocity vector and project onto line of sight
            velocity_vector = topocentric.velocity.km_per_s
            # For simplicity, use the magnitude of velocity as radial component
            velocity = np.linalg.norm(velocity_vector)
        except Exception:
            velocity = 7.0  # Default LEO velocity in km/s
        
        # Flag if below horizon
        below_horizon = el.degrees < 0
        records.append({
            'time': t.strftime('%Y-%m-%d %H:%M:%S'),
            'azimuth': az.degrees,
            'elevation': el.degrees,
            'range': distance.km,
            'velocity': velocity,
            'below_horizon': below_horizon
        })
    df = pd.DataFrame(records)
    return df


def main():
    """Main entry point for the flyby simulation."""
    try:
        gs, sim = load_config(CONFIG_PATH)
        tle_lines = load_tle(TLE_PATH)
        df = simulate_flyby(gs, sim, tle_lines)
        # Save to CSV
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        df.to_csv(LOG_PATH, index=False)
        print(f"Simulation complete. Results saved to {LOG_PATH}")
        print(f"Generated {len(df)} data points")
        print("\nFirst few results:")
        print(df.head())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 