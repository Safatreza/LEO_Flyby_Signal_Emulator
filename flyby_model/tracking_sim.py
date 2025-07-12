"""
LEO Satellite Antenna Tracking Simulator
- Simulates antenna tracking with beamwidth and slew rate constraints
- Calculates pointing error and lock status
- Generates 2D and 3D tracking visualizations
- Logs tracking performance to data/logs/tracking_log.csv
"""
import os
import sys
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Constants
CONFIG_PATH = 'config/sim_config.yaml'
LOG_PATH = 'data/logs/tracking_log.csv'


def load_tracking_config(config_path):
    """Load antenna tracking parameters from YAML config."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        antenna_config = config.get('antenna', {})
        return antenna_config
    except Exception as e:
        raise RuntimeError(f"Failed to load tracking config: {e}")


class TrackingSimulator:
    """
    Simulates antenna tracking with realistic constraints.
    Handles beamwidth, slew rate, pointing errors, and lock status.
    """
    
    def __init__(self, beamwidth_deg=10.0, slew_rate_deg_s=5.0, pointing_error_deg=0.5):
        """
        Initialize tracking simulator.
        
        Args:
            beamwidth_deg: Antenna beamwidth in degrees
            slew_rate_deg_s: Maximum slew rate in degrees/second
            pointing_error_deg: RMS pointing error in degrees
        """
        self.beamwidth_deg = float(beamwidth_deg)
        self.slew_rate_deg_s = float(slew_rate_deg_s)
        self.pointing_error_deg = float(pointing_error_deg)
        
        # Current antenna position
        self.current_az_deg = 0.0
        self.current_el_deg = 0.0
        
        # Tracking statistics
        self.total_points = 0
        self.locked_points = 0
        self.tracking_errors = []
        
        # Create log directory
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    def is_target_in_beam(self, target_az_deg, target_el_deg, antenna_az_deg, antenna_el_deg):
        """
        Check if target is within antenna beam.
        
        Args:
            target_az_deg: Target azimuth in degrees
            target_el_deg: Target elevation in degrees
            antenna_az_deg: Antenna azimuth in degrees
            antenna_el_deg: Antenna elevation in degrees
            
        Returns:
            bool: True if target is in beam
        """
        # Handle azimuth wrap-around (0-360 degrees)
        az_diff = abs(target_az_deg - antenna_az_deg)
        az_diff = min(az_diff, 360 - az_diff)  # Take shortest angular distance
        
        el_diff = abs(target_el_deg - antenna_el_deg)
        
        # Check if within beamwidth
        in_beam = (az_diff <= self.beamwidth_deg / 2) and (el_diff <= self.beamwidth_deg / 2)
        return in_beam

    def apply_pointing_error(self, az_deg, el_deg):
        """
        Apply realistic pointing error to antenna position.
        
        Args:
            az_deg: Desired azimuth in degrees
            el_deg: Desired elevation in degrees
            
        Returns:
            tuple: (azimuth_with_error, elevation_with_error)
        """
        # Add Gaussian pointing error
        az_error = np.random.normal(0, self.pointing_error_deg)
        el_error = np.random.normal(0, self.pointing_error_deg)
        
        az_with_error = az_deg + az_error
        el_with_error = el_deg + el_error
        
        # Ensure elevation stays within valid range
        el_with_error = np.clip(el_with_error, 0, 90)
        
        return az_with_error, el_with_error

    def move_antenna(self, target_az_deg, target_el_deg, time_step_sec=1.0):
        """
        Move antenna to target position with slew rate constraints.
        
        Args:
            target_az_deg: Target azimuth in degrees
            target_el_deg: Target elevation in degrees
            time_step_sec: Time step in seconds
            
        Returns:
            tuple: (actual_azimuth, actual_elevation, pointing_error)
        """
        # Calculate required movement
        az_diff = target_az_deg - self.current_az_deg
        el_diff = target_el_deg - self.current_el_deg
        
        # Handle azimuth wrap-around
        if az_diff > 180:
            az_diff -= 360
        elif az_diff < -180:
            az_diff += 360
        
        # Apply slew rate constraints
        max_az_step = self.slew_rate_deg_s * time_step_sec
        max_el_step = self.slew_rate_deg_s * time_step_sec
        
        az_step = np.clip(az_diff, -max_az_step, max_az_step)
        el_step = np.clip(el_diff, -max_el_step, max_el_step)
        
        # Update antenna position
        self.current_az_deg += az_step
        self.current_el_deg += el_step
        
        # Normalize azimuth to 0-360 range
        self.current_az_deg = self.current_az_deg % 360
        
        # Apply pointing error
        actual_az, actual_el = self.apply_pointing_error(self.current_az_deg, self.current_el_deg)
        
        # Calculate pointing error
        pointing_error = np.sqrt((target_az_deg - actual_az)**2 + (target_el_deg - actual_el)**2)
        
        return actual_az, actual_el, pointing_error

    def simulate_tracking(self, orbit_df, signal_df):
        """
        Simulate antenna tracking for the entire orbit.
        
        Args:
            orbit_df: DataFrame with orbit data (time, azimuth, elevation, range)
            signal_df: DataFrame with signal data (time, snr, doppler_shift)
            
        Returns:
            DataFrame: Tracking simulation results
        """
        records = []
        
        for _, orbit_row in orbit_df.iterrows():
            try:
                time = orbit_row['time']
                target_az = float(orbit_row['azimuth'])
                target_el = float(orbit_row['elevation'])
                range_km = float(orbit_row['range'])
                below_horizon = orbit_row.get('below_horizon', False)
                
                # Skip if below horizon
                if below_horizon or target_el < 0:
                    records.append({
                        'time': time,
                        'target_azimuth': target_az,
                        'target_elevation': target_el,
                        'antenna_azimuth': 0,
                        'antenna_elevation': 0,
                        'pointing_error': 999,
                        'in_beam': False,
                        'locked': False,
                        'range_km': range_km
                    })
                    continue
                
                # Move antenna to target
                actual_az, actual_el, pointing_error = self.move_antenna(target_az, target_el)
                
                # Check if in beam
                in_beam = self.is_target_in_beam(target_az, target_el, actual_az, actual_el)
                
                # Check lock status (in beam and good signal)
                locked = in_beam
                
                # Update statistics
                self.total_points += 1
                if locked:
                    self.locked_points += 1
                self.tracking_errors.append(pointing_error)
                
                records.append({
                    'time': time,
                    'target_azimuth': target_az,
                    'target_elevation': target_el,
                    'antenna_azimuth': actual_az,
                    'antenna_elevation': actual_el,
                    'pointing_error': pointing_error,
                    'in_beam': in_beam,
                    'locked': locked,
                    'range_km': range_km
                })
                
            except (ValueError, TypeError) as e:
                print(f"Warning: Invalid tracking data at time {orbit_row.get('time', 'unknown')}: {e}")
                records.append({
                    'time': orbit_row.get('time', ''),
                    'target_azimuth': 0,
                    'target_elevation': 0,
                    'antenna_azimuth': 0,
                    'antenna_elevation': 0,
                    'pointing_error': 999,
                    'in_beam': False,
                    'locked': False,
                    'range_km': 0
                })
        
        return pd.DataFrame(records)

    def generate_plots(self, tracking_df, save_path='data/plots/'):
        """
        Generate tracking visualization plots.
        
        Args:
            tracking_df: DataFrame with tracking results
            save_path: Directory to save plots
        """
        try:
            os.makedirs(save_path, exist_ok=True)
            
            # Filter valid tracking data
            valid_data = tracking_df[tracking_df['pointing_error'] < 999]
            
            if len(valid_data) == 0:
                print("No valid tracking data to plot")
                return
            
            # 1. 2D Tracking Plot
            plt.figure(figsize=(12, 8))
            
            plt.subplot(2, 2, 1)
            plt.plot(valid_data['target_azimuth'], valid_data['target_elevation'], 
                    'b-', linewidth=2, label='Satellite', alpha=0.7)
            plt.plot(valid_data['antenna_azimuth'], valid_data['antenna_elevation'], 
                    'r--', linewidth=2, label='Antenna', alpha=0.7)
            plt.xlabel('Azimuth (degrees)')
            plt.ylabel('Elevation (degrees)')
            plt.title('Antenna Tracking vs Satellite Position')
            plt.legend()
            plt.grid(True)
            
            # 2. Pointing Error vs Time
            plt.subplot(2, 2, 2)
            times = range(len(valid_data))
            plt.plot(times, valid_data['pointing_error'], 'g-', linewidth=2)
            plt.axhline(y=self.beamwidth_deg/2, color='r', linestyle='--', 
                       alpha=0.5, label=f'Beamwidth/2 ({self.beamwidth_deg/2:.1f}°)')
            plt.xlabel('Time Step')
            plt.ylabel('Pointing Error (degrees)')
            plt.title('Pointing Error vs Time')
            plt.legend()
            plt.grid(True)
            
            # 3. Lock Status
            plt.subplot(2, 2, 3)
            locked_times = valid_data[valid_data['locked'] == True].index
            unlocked_times = valid_data[valid_data['locked'] == False].index
            
            if len(locked_times) > 0:
                plt.scatter(locked_times, [1]*len(locked_times), c='green', 
                           s=20, alpha=0.7, label='Locked')
            if len(unlocked_times) > 0:
                plt.scatter(unlocked_times, [0]*len(unlocked_times), c='red', 
                           s=20, alpha=0.7, label='Unlocked')
            
            plt.xlabel('Time Step')
            plt.ylabel('Lock Status')
            plt.title('Antenna Lock Status')
            plt.legend()
            plt.grid(True)
            
            # 4. Range vs Lock Status
            plt.subplot(2, 2, 4)
            locked_ranges = valid_data[valid_data['locked'] == True]['range_km']
            unlocked_ranges = valid_data[valid_data['locked'] == False]['range_km']
            
            if len(locked_ranges) > 0:
                plt.hist(locked_ranges, bins=20, alpha=0.7, label='Locked', color='green')
            if len(unlocked_ranges) > 0:
                plt.hist(unlocked_ranges, bins=20, alpha=0.7, label='Unlocked', color='red')
            
            plt.xlabel('Range (km)')
            plt.ylabel('Frequency')
            plt.title('Range Distribution by Lock Status')
            plt.legend()
            plt.grid(True)
            
            plt.tight_layout()
            plt.savefig(os.path.join(save_path, 'tracking_analysis.png'), 
                       dpi=300, bbox_inches='tight')
            plt.show()
            
            print(f"Tracking plots saved to {save_path}")
            
        except Exception as e:
            print(f"Error generating tracking plots: {e}")

    def get_tracking_statistics(self):
        """
        Get tracking performance statistics.
        
        Returns:
            dict: Tracking statistics
        """
        if self.total_points == 0:
            return {
                'total_points': 0,
                'locked_points': 0,
                'lock_percentage': 0,
                'avg_pointing_error': 0,
                'max_pointing_error': 0
            }
        
        return {
            'total_points': self.total_points,
            'locked_points': self.locked_points,
            'lock_percentage': (self.locked_points / self.total_points) * 100,
            'avg_pointing_error': np.mean(self.tracking_errors) if self.tracking_errors else 0,
            'max_pointing_error': np.max(self.tracking_errors) if self.tracking_errors else 0
        }


def main():
    """Main entry point for tracking simulation."""
    try:
        # Load configuration
        antenna_config = load_tracking_config(CONFIG_PATH)
        
        # Check if orbit and signal data exist
        orbit_log_path = 'data/logs/orbit_log.csv'
        signal_log_path = 'data/logs/signal_log.csv'
        
        if not os.path.exists(orbit_log_path):
            print(f"Error: Orbit data not found at {orbit_log_path}")
            print("Please run orbit_sim.py first to generate orbit data.")
            sys.exit(1)
        
        if not os.path.exists(signal_log_path):
            print(f"Error: Signal data not found at {signal_log_path}")
            print("Please run signal_model.py first to generate signal data.")
            sys.exit(1)
        
        # Load data
        orbit_df = pd.read_csv(orbit_log_path)
        signal_df = pd.read_csv(signal_log_path)
        
        # Initialize tracking simulator
        beamwidth = float(antenna_config.get('beamwidth_deg', 10.0))
        slew_rate = float(antenna_config.get('slew_rate_deg_s', 5.0))
        pointing_error = float(antenna_config.get('pointing_error_deg', 0.5))
        
        tracker = TrackingSimulator(beamwidth, slew_rate, pointing_error)
        
        # Run tracking simulation
        tracking_df = tracker.simulate_tracking(orbit_df, signal_df)
        
        # Save results
        tracking_df.to_csv(LOG_PATH, index=False)
        print(f"Tracking simulation complete. Results saved to {LOG_PATH}")
        
        # Generate plots
        tracker.generate_plots(tracking_df)
        
        # Print statistics
        stats = tracker.get_tracking_statistics()
        print(f"\nTracking Statistics:")
        print(f"  Total points: {stats['total_points']}")
        print(f"  Locked points: {stats['locked_points']}")
        print(f"  Lock percentage: {stats['lock_percentage']:.1f}%")
        print(f"  Average pointing error: {stats['avg_pointing_error']:.2f}°")
        print(f"  Maximum pointing error: {stats['max_pointing_error']:.2f}°")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 