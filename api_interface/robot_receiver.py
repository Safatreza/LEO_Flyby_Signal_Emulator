"""
RobotReceiver - Simulates a receiver/robotic arm for a LEO satellite emulator.
- Receives signal and antenna data via XLAPI
- Logs to data/logs/receiver_log.txt
- Simulates antenna movement with slew rate
- Outputs lock status based on SNR and pointing error
"""
import os
import sys
import time
import yaml
from datetime import datetime
from api_interface.xlapi_mock import XLAPI

LOG_PATH = 'data/logs/receiver_log.txt'
CONFIG_PATH = 'config/sim_config.yaml'

class RobotReceiver:
    """
    Simulates a receiver/robotic arm for a LEO satellite emulator.
    Receives signal and antenna data via XLAPI, logs, and outputs lock status.
    """
    def __init__(self, xlapi=None):
        self.xlapi = xlapi if xlapi else XLAPI()
        self.current_az = 0.0
        self.current_el = 0.0
        self.slew_rate = 5.0  # deg/s default
        self.beamwidth = 10.0  # deg default
        self.last_snr = 0.0
        self.last_pointing_error = 999.0
        self._load_config()
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    def _load_config(self):
        """Load slew rate and beamwidth from config."""
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = yaml.safe_load(f)
            antenna = config.get('antenna', {})
            self.slew_rate = float(antenna.get('slew_rate_deg_s', 5.0))
            self.beamwidth = float(antenna.get('beamwidth_deg', 10.0))
        except Exception as e:
            self._log(f"Error loading config: {e}")

    def _log(self, message):
        """Log a message with timestamp to the receiver log file."""
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_PATH, 'a') as f:
            f.write(f'[{timestamp}] {message}\n')

    def receive_signal(self):
        """Receive signal data from XLAPI (thread-safe)."""
        try:
            data = self.xlapi.signal_queue.get(timeout=1)
            self.last_snr = data['snr']
            self._log(f"Received signal: {data}")
            return data
        except Exception as e:
            self._log(f"Error receiving signal: {e}")
            return None

    def receive_antenna(self):
        """Receive antenna data from XLAPI (thread-safe)."""
        try:
            data = self.xlapi.antenna_queue.get(timeout=1)
            target_az = data['azimuth']
            target_el = data['elevation']
            # Simulate antenna movement with slew rate
            az_diff = target_az - self.current_az
            el_diff = target_el - self.current_el
            az_step = max(min(az_diff, self.slew_rate), -self.slew_rate)
            el_step = max(min(el_diff, self.slew_rate), -self.slew_rate)
            self.current_az += az_step
            self.current_el += el_step
            self._log(f"Moved antenna to: az={self.current_az:.2f}, el={self.current_el:.2f}")
            return {'azimuth': self.current_az, 'elevation': self.current_el}
        except Exception as e:
            self._log(f"Error receiving antenna: {e}")
            return None

    def compute_pointing_error(self, target_az, target_el):
        """Compute pointing error in degrees."""
        error = ((self.current_az - target_az)**2 + (self.current_el - target_el)**2) ** 0.5
        self.last_pointing_error = error
        return error

    def get_status(self):
        """
        Output status: 'Locked on satellite' if SNR > 10 dB and pointing error < beamwidth/2,
        'Signal lost' otherwise.
        """
        if self.last_snr > 10 and self.last_pointing_error < self.beamwidth / 2:
            status = 'Locked on satellite'
        else:
            status = 'Signal lost'
        self._log(f"Status: {status} (SNR={self.last_snr}, error={self.last_pointing_error})")
        return status

# Example usage (for testing)
if __name__ == '__main__':
    api = XLAPI()
    receiver = RobotReceiver(api)
    # Simulate sending data
    api.send_signal_data('2025-07-12 22:00:00', 1234.5, 20.1)
    api.set_antenna(180, 45)
    sig = receiver.receive_signal()
    ant = receiver.receive_antenna()
    if sig and ant:
        error = receiver.compute_pointing_error(ant['azimuth'], ant['elevation'])
        print('Pointing error:', error)
    print('Status:', receiver.get_status()) 