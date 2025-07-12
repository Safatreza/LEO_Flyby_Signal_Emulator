"""
Dependency-free LEO Satellite Flyby Emulator Demo
- Simplified two-body orbit model (circular orbit, 500 km altitude)
- Basic signal calculations (Doppler, path loss, SNR)
- Antenna tracking simulation with fixed beamwidth
- Uses only standard Python libraries and Matplotlib
- Outputs plots to data/plots/
"""
import math
import random
import os
from datetime import datetime, timedelta

# Configuration dictionary
CONFIG = {
    'duration_sec': 600,      # 10 minutes
    'time_step_sec': 1,       # 1 second intervals
    'satellite': {
        'altitude_km': 500,   # Circular orbit altitude
        'velocity_km_s': 7.8, # Orbital velocity
        'earth_radius_km': 6371
    },
    'ground_station': {
        'latitude_deg': 37.7749,  # San Francisco
        'longitude_deg': -122.4194,
        'elevation_m': 10
    },
    'signal': {
        'frequency_hz': 2.4e9,    # 2.4 GHz
        'tx_power_dbm': 20,       # Transmit power
        'tx_gain_db': 20,         # Transmit antenna gain
        'rx_gain_db': 20          # Receive antenna gain
    },
    'antenna': {
        'beamwidth_deg': 10       # Antenna beamwidth
    }
}

# Constants
C = 299792458  # Speed of light in m/s


def calculate_satellite_position(time_sec, config):
    """
    Calculate satellite position using simplified circular orbit model.
    
    Args:
        time_sec: Time in seconds from start
        config: Configuration dictionary
    
    Returns:
        dict: Satellite position (lat, lon, altitude, range, azimuth, elevation)
    """
    # Simplified circular orbit calculation
    # Assume satellite moves in a circular orbit at fixed altitude
    
    # Calculate orbital period (simplified)
    altitude_km = config['satellite']['altitude_km']
    earth_radius = config['satellite']['earth_radius_km']
    orbital_radius = earth_radius + altitude_km
    
    # Angular velocity (simplified)
    angular_velocity = config['satellite']['velocity_km_s'] / orbital_radius  # rad/s
    
    # Satellite position (simplified - assume starts at longitude 0)
    satellite_lon = (angular_velocity * time_sec) * 180 / math.pi  # Convert to degrees
    satellite_lat = 0  # Assume equatorial orbit for simplicity
    
    # Ground station position
    gs_lat = config['ground_station']['latitude_deg']
    gs_lon = config['ground_station']['longitude_deg']
    
    # Calculate range and angles (simplified spherical trigonometry)
    lat_diff = satellite_lat - gs_lat
    lon_diff = satellite_lon - gs_lon
    
    # Simplified range calculation
    range_km = math.sqrt((lat_diff * 111)**2 + (lon_diff * 111)**2 + altitude_km**2)
    
    # Simplified azimuth and elevation
    azimuth = math.atan2(lon_diff, lat_diff) * 180 / math.pi
    if azimuth < 0:
        azimuth += 360
    
    # Simplified elevation calculation
    elevation = math.asin(altitude_km / range_km) * 180 / math.pi
    
    return {
        'latitude_deg': satellite_lat,
        'longitude_deg': satellite_lon,
        'altitude_km': altitude_km,
        'range_km': range_km,
        'azimuth_deg': azimuth,
        'elevation_deg': elevation
    }


def calculate_doppler_shift(velocity_km_s, frequency_hz):
    """
    Calculate Doppler shift in Hz.
    
    Args:
        velocity_km_s: Radial velocity in km/s
        frequency_hz: Carrier frequency in Hz
    
    Returns:
        float: Doppler shift in Hz
    """
    velocity_m_s = velocity_km_s * 1000
    doppler_shift = (velocity_m_s / C) * frequency_hz
    return doppler_shift


def calculate_path_loss(range_km, frequency_hz):
    """
    Calculate free-space path loss in dB.
    
    Args:
        range_km: Distance in km
        frequency_hz: Carrier frequency in Hz
    
    Returns:
        float: Path loss in dB
    """
    range_m = range_km * 1000
    # FSPL = 20*log10(d) + 20*log10(f) + 20*log10(4π/c)
    path_loss = (20 * math.log10(range_m) + 
                 20 * math.log10(frequency_hz) + 
                 20 * math.log10(4 * math.pi / C))
    return path_loss


def calculate_snr(tx_power_dbm, tx_gain_db, rx_gain_db, path_loss_db):
    """
    Calculate signal-to-noise ratio in dB.
    
    Args:
        tx_power_dbm: Transmit power in dBm
        tx_gain_db: Transmit antenna gain in dB
        rx_gain_db: Receive antenna gain in dB
        path_loss_db: Path loss in dB
    
    Returns:
        float: SNR in dB
    """
    # Simplified SNR calculation (noise power assumed constant)
    snr = tx_power_dbm + tx_gain_db + rx_gain_db - path_loss_db - 120  # -120 dBm noise floor
    return snr


def simulate_antenna_tracking(satellite_pos, config):
    """
    Simulate antenna tracking with fixed beamwidth.
    
    Args:
        satellite_pos: Satellite position dictionary
        config: Configuration dictionary
    
    Returns:
        dict: Antenna tracking results
    """
    # Simplified antenna tracking (assume perfect tracking with some error)
    beamwidth = config['antenna']['beamwidth_deg']
    
    # Add small pointing error
    pointing_error = random.uniform(-1, 1)  # ±1 degree error
    
    antenna_az = satellite_pos['azimuth_deg'] + pointing_error
    antenna_el = satellite_pos['elevation_deg'] + pointing_error
    
    # Calculate pointing error
    az_error = abs(antenna_az - satellite_pos['azimuth_deg'])
    el_error = abs(antenna_el - satellite_pos['elevation_deg'])
    total_error = math.sqrt(az_error**2 + el_error**2)
    
    # Check if in beam
    in_beam = total_error < beamwidth / 2
    
    return {
        'antenna_az_deg': antenna_az,
        'antenna_el_deg': antenna_el,
        'pointing_error_deg': total_error,
        'in_beam': in_beam
    }


def run_simulation(config):
    """
    Run complete LEO flyby simulation.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        list: Simulation results
    """
    print("Starting LEO Flyby Simulation...")
    print(f"Duration: {config['duration_sec']} seconds ({config['duration_sec']/60:.1f} minutes)")
    print(f"Time step: {config['time_step_sec']} seconds")
    
    results = []
    
    for t in range(0, config['duration_sec'] + 1, config['time_step_sec']):
        # Calculate satellite position
        sat_pos = calculate_satellite_position(t, config)
        
        # Skip if below horizon
        if sat_pos['elevation_deg'] < 0:
            results.append({
                'time_sec': t,
                'satellite': sat_pos,
                'signal': {'doppler_hz': None, 'path_loss_db': None, 'snr_db': None},
                'antenna': {'antenna_az_deg': 0, 'antenna_el_deg': 0, 'pointing_error_deg': 999, 'in_beam': False}
            })
            continue
        
        # Calculate signal parameters
        # Simplified velocity calculation (assume constant radial velocity)
        velocity_km_s = config['satellite']['velocity_km_s'] * 0.7  # Approximate radial component
        
        doppler_hz = calculate_doppler_shift(velocity_km_s, config['signal']['frequency_hz'])
        path_loss_db = calculate_path_loss(sat_pos['range_km'], config['signal']['frequency_hz'])
        snr_db = calculate_snr(
            config['signal']['tx_power_dbm'],
            config['signal']['tx_gain_db'],
            config['signal']['rx_gain_db'],
            path_loss_db
        )
        
        # Simulate antenna tracking
        antenna_data = simulate_antenna_tracking(sat_pos, config)
        
        results.append({
            'time_sec': t,
            'satellite': sat_pos,
            'signal': {
                'doppler_hz': doppler_hz,
                'path_loss_db': path_loss_db,
                'snr_db': snr_db
            },
            'antenna': antenna_data
        })
    
    print(f"Simulation completed. Generated {len(results)} data points.")
    return results


def create_plots(results, config):
    """
    Create matplotlib plots of simulation results.
    
    Args:
        results: Simulation results list
        config: Configuration dictionary
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
    except ImportError:
        print("Matplotlib not available. Skipping plots.")
        return
    
    # Create plots directory
    os.makedirs('data/plots', exist_ok=True)
    
    # Extract data
    times = [r['time_sec'] for r in results]
    ranges = [r['satellite']['range_km'] for r in results]
    elevations = [r['satellite']['elevation_deg'] for r in results]
    azimuths = [r['satellite']['azimuth_deg'] for r in results]
    dopplers = [r['signal']['doppler_hz'] for r in results if r['signal']['doppler_hz'] is not None]
    snrs = [r['signal']['snr_db'] for r in results if r['signal']['snr_db'] is not None]
    antenna_az = [r['antenna']['antenna_az_deg'] for r in results]
    antenna_el = [r['antenna']['antenna_el_deg'] for r in results]
    
    # 1. Orbit plot (range vs time)
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    plt.plot(times, ranges, 'b-', linewidth=2)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Range (km)')
    plt.title('Satellite Range vs Time')
    plt.grid(True)
    
    # 2. Elevation plot
    plt.subplot(2, 2, 2)
    plt.plot(times, elevations, 'g-', linewidth=2)
    plt.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Horizon')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Elevation (degrees)')
    plt.title('Satellite Elevation vs Time')
    plt.legend()
    plt.grid(True)
    
    # 3. Signal metrics
    plt.subplot(2, 2, 3)
    valid_times = [t for t, r in zip(times, results) if r['signal']['doppler_hz'] is not None]
    plt.plot(valid_times, dopplers, 'r-', linewidth=2, label='Doppler Shift')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Doppler Shift (Hz)')
    plt.title('Doppler Shift vs Time')
    plt.grid(True)
    
    # 4. SNR plot
    plt.subplot(2, 2, 4)
    plt.plot(valid_times, snrs, 'm-', linewidth=2, label='SNR')
    plt.axhline(y=10, color='r', linestyle='--', alpha=0.5, label='10 dB threshold')
    plt.xlabel('Time (seconds)')
    plt.ylabel('SNR (dB)')
    plt.title('Signal-to-Noise Ratio vs Time')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('data/plots/demo_overview.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Antenna tracking plot
    plt.figure(figsize=(10, 6))
    plt.plot(azimuths, elevations, 'b-', linewidth=2, label='Satellite', alpha=0.7)
    plt.plot(antenna_az, antenna_el, 'r--', linewidth=2, label='Antenna', alpha=0.7)
    plt.xlabel('Azimuth (degrees)')
    plt.ylabel('Elevation (degrees)')
    plt.title('Antenna Tracking vs Satellite Position')
    plt.legend()
    plt.grid(True)
    plt.savefig('data/plots/demo_tracking.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Plots saved to data/plots/")


def print_summary(results, config):
    """
    Print simulation summary.
    
    Args:
        results: Simulation results list
        config: Configuration dictionary
    """
    print("\n=== Simulation Summary ===")
    
    # Count visible points
    visible_points = sum(1 for r in results if r['satellite']['elevation_deg'] >= 0)
    total_points = len(results)
    
    print(f"Total simulation time: {config['duration_sec']} seconds")
    print(f"Satellite visible: {visible_points}/{total_points} points ({visible_points/total_points*100:.1f}%)")
    
    if visible_points > 0:
        # Signal statistics
        valid_signals = [r for r in results if r['signal']['snr_db'] is not None]
        if valid_signals:
            snrs = [r['signal']['snr_db'] for r in valid_signals]
            dopplers = [r['signal']['doppler_hz'] for r in valid_signals]
            
            print(f"\nSignal Statistics:")
            print(f"  Average SNR: {sum(snrs)/len(snrs):.1f} dB")
            print(f"  SNR range: {min(snrs):.1f} to {max(snrs):.1f} dB")
            print(f"  Average Doppler shift: {sum(dopplers)/len(dopplers):.1f} Hz")
            print(f"  Doppler range: {min(dopplers):.1f} to {max(dopplers):.1f} Hz")
        
        # Tracking statistics
        in_beam_count = sum(1 for r in results if r['antenna']['in_beam'])
        print(f"\nTracking Statistics:")
        print(f"  In beam: {in_beam_count}/{visible_points} points ({in_beam_count/visible_points*100:.1f}%)")
        print(f"  Beamwidth: {config['antenna']['beamwidth_deg']}°")
    
    print("\n✓ Simulation completed successfully!")


def main():
    """
    Main function to run the LEO flyby simulation demo.
    """
    print("LEO Satellite Flyby Emulator Demo")
    print("=" * 40)
    
    # Run simulation
    results = run_simulation(CONFIG)
    
    # Create plots
    create_plots(results, CONFIG)
    
    # Print summary
    print_summary(results, CONFIG)


if __name__ == "__main__":
    main() 