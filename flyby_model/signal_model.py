"""
LEO Satellite Signal Emulator
- Calculates Doppler shift, path loss, SNR, and atmospheric attenuation.
- Reads orbit data from pandas DataFrame and signal parameters from config.
- Outputs results as a pandas DataFrame and logs to data/logs/signal_log.csv.
"""
import os
import sys
import yaml
import numpy as np
import pandas as pd
from datetime import datetime

# Constants
CONFIG_PATH = 'config/sim_config.yaml'
LOG_PATH = 'data/logs/signal_log.csv'
C = 299792458  # Speed of light in m/s
K = 1.380649e-23  # Boltzmann constant in J/K
T_SYS = 290  # System noise temperature in K


def load_signal_config(config_path):
    """Load signal parameters from YAML config."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        signal_config = config.get('signal', {})
        return signal_config
    except Exception as e:
        raise RuntimeError(f"Failed to load signal config: {e}")


def calculate_doppler_shift(velocity_km_s, frequency_hz):
    """
    Calculate Doppler shift in Hz.
    Args:
        velocity_km_s: Radial velocity in km/s
        frequency_hz: Carrier frequency in Hz
    Returns:
        Doppler shift in Hz
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
        Path loss in dB
    """
    range_m = range_km * 1000
    # FSPL = 20*log10(d) + 20*log10(f) + 20*log10(4π/c)
    path_loss = (20 * np.log10(range_m) + 
                 20 * np.log10(frequency_hz) + 
                 20 * np.log10(4 * np.pi / C))
    return path_loss


def calculate_thermal_noise(bandwidth_hz):
    """
    Calculate thermal noise power in dBm.
    Args:
        bandwidth_hz: System bandwidth in Hz
    Returns:
        Noise power in dBm
    """
    noise_power_w = K * T_SYS * bandwidth_hz
    noise_power_dbm = 10 * np.log10(noise_power_w * 1000)
    return noise_power_dbm


def calculate_atmospheric_attenuation(elevation_deg, range_km):
    """
    Calculate atmospheric attenuation in dB.
    Args:
        elevation_deg: Elevation angle in degrees
        range_km: Range in km
    Returns:
        Atmospheric attenuation in dB
    """
    if elevation_deg < 10:
        # Apply 0.1 dB/km for low elevation angles
        attenuation = 0.1 * range_km
    else:
        # Negligible attenuation for high elevation angles
        attenuation = 0.0
    return attenuation


def calculate_snr(tx_power_dbm, tx_gain_db, rx_gain_db, path_loss_db, 
                  atmospheric_loss_db, noise_power_dbm):
    """
    Calculate signal-to-noise ratio in dB.
    Args:
        tx_power_dbm: Transmit power in dBm
        tx_gain_db: Transmit antenna gain in dB
        rx_gain_db: Receive antenna gain in dB
        path_loss_db: Path loss in dB
        atmospheric_loss_db: Atmospheric attenuation in dB
        noise_power_dbm: Noise power in dBm
    Returns:
        SNR in dB
    """
    # SNR = P_tx + G_tx + G_rx - FSPL - N - atmospheric_loss
    snr = (tx_power_dbm + tx_gain_db + rx_gain_db - 
           path_loss_db - noise_power_dbm - atmospheric_loss_db)
    return snr


def simulate_signal(orbit_df, signal_config):
    """
    Simulate signal parameters for the entire orbit.
    Args:
        orbit_df: Pandas DataFrame with orbit data (time, range, velocity, elevation)
        signal_config: Dictionary with signal parameters
    Returns:
        Pandas DataFrame with signal simulation results
    """
    # Extract signal parameters
    frequency_hz = float(signal_config.get('frequency_hz', 437e6))
    tx_power_dbm = float(signal_config.get('tx_power_dbm', 30))
    tx_gain_db = float(signal_config.get('tx_gain_db', 0))
    rx_gain_db = float(signal_config.get('rx_gain_db', 10))
    bandwidth_hz = float(signal_config.get('bandwidth_hz', 20000))
    
    # Calculate noise power
    noise_power_dbm = calculate_thermal_noise(bandwidth_hz)
    
    # Initialize results list
    records = []
    
    for _, row in orbit_df.iterrows():
        try:
            # Extract orbit data
            time = row['time']
            range_km = float(row['range'])
            velocity_km_s = float(row['velocity'])
            elevation_deg = float(row['elevation'])
            
            # Skip if satellite is below horizon
            if elevation_deg < 0:
                records.append({
                    'time': time,
                    'doppler_shift': np.nan,
                    'path_loss': np.nan,
                    'snr': np.nan,
                    'atmospheric_loss': np.nan,
                    'below_horizon': True
                })
                continue
            
            # Calculate signal parameters
            doppler_shift = calculate_doppler_shift(velocity_km_s, frequency_hz)
            path_loss = calculate_path_loss(range_km, frequency_hz)
            atmospheric_loss = calculate_atmospheric_attenuation(elevation_deg, range_km)
            snr = calculate_snr(tx_power_dbm, tx_gain_db, rx_gain_db, 
                              path_loss, atmospheric_loss, noise_power_dbm)
            
            records.append({
                'time': time,
                'doppler_shift': doppler_shift,
                'path_loss': path_loss,
                'snr': snr,
                'atmospheric_loss': atmospheric_loss,
                'below_horizon': False
            })
            
        except (ValueError, TypeError) as e:
            print(f"Warning: Invalid data at time {row.get('time', 'unknown')}: {e}")
            records.append({
                'time': row.get('time', ''),
                'doppler_shift': np.nan,
                'path_loss': np.nan,
                'snr': np.nan,
                'atmospheric_loss': np.nan,
                'below_horizon': True
            })
    
    return pd.DataFrame(records)


def main():
    """Main entry point for signal simulation."""
    try:
        # Load signal configuration
        signal_config = load_signal_config(CONFIG_PATH)
        
        # Check if orbit data exists
        orbit_log_path = 'data/logs/orbit_log.csv'
        if not os.path.exists(orbit_log_path):
            print(f"Error: Orbit data not found at {orbit_log_path}")
            print("Please run orbit_sim.py first to generate orbit data.")
            sys.exit(1)
        
        # Load orbit data
        orbit_df = pd.read_csv(orbit_log_path)
        print(f"Loaded orbit data with {len(orbit_df)} points")
        
        # Simulate signal
        signal_df = simulate_signal(orbit_df, signal_config)
        
        # Save results
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        signal_df.to_csv(LOG_PATH, index=False)
        
        print(f"Signal simulation complete. Results saved to {LOG_PATH}")
        print(f"Signal parameters:")
        print(f"  Frequency: {signal_config.get('frequency_hz', 437e6)/1e6:.1f} MHz")
        print(f"  TX Power: {signal_config.get('tx_power_dbm', 30)} dBm")
        print(f"  RX Gain: {signal_config.get('rx_gain_db', 10)} dB")
        print(f"  Bandwidth: {signal_config.get('bandwidth_hz', 20000)/1e3:.1f} kHz")
        
        # Show summary statistics
        valid_snr = signal_df[signal_df['snr'].notna()]['snr']
        if len(valid_snr) > 0:
            print(f"\nSNR Statistics:")
            print(f"  Mean: {valid_snr.mean():.2f} dB")
            print(f"  Min: {valid_snr.min():.2f} dB")
            print(f"  Max: {valid_snr.max():.2f} dB")
        
        print(f"\nFirst few results:")
        print(signal_df.head())
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 