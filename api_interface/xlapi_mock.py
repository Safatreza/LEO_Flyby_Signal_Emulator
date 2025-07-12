"""
XLAPI Mock - Emulates a control interface for a LEO satellite emulator.
- Thread-safe real-time data streaming using queue.Queue
- Logs all commands and responses
- Error handling for invalid inputs
"""
import os
import sys
import queue
import threading
from datetime import datetime

LOG_PATH = 'data/logs/api_log.txt'

class XLAPI:
    """
    Mock XLAPI interface for LEO satellite emulator.
    Provides methods to send signal data, set antenna position, and get receiver status.
    Uses a thread-safe queue for real-time data streaming.
    """
    def __init__(self):
        self.signal_queue = queue.Queue()
        self.antenna_queue = queue.Queue()
        self.status = 'Idle'
        self.lock = threading.Lock()
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    def log(self, message):
        """Log a message with timestamp to the API log file."""
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        with self.lock:
            with open(LOG_PATH, 'a') as f:
                f.write(f'[{timestamp}] {message}\n')

    def send_signal_data(self, t, doppler, snr):
        """
        Send signal metrics to the receiver.
        Args:
            t: Timestamp or time string
            doppler: Doppler shift (Hz)
            snr: Signal-to-noise ratio (dB)
        Returns:
            True if data accepted, False otherwise
        """
        try:
            if snr < 0:
                raise ValueError('SNR cannot be negative')
            self.signal_queue.put({'time': t, 'doppler': doppler, 'snr': snr})
            self.log(f'Sent signal data: t={t}, doppler={doppler}, snr={snr}')
            self.status = 'Locked' if snr > 10 else 'Signal lost'
            return True
        except Exception as e:
            self.log(f'Error sending signal data: {e}')
            return False

    def set_antenna(self, az, el):
        """
        Set antenna position.
        Args:
            az: Azimuth (degrees, 0-360)
            el: Elevation (degrees, 0-90)
        Returns:
            True if position accepted, False otherwise
        """
        try:
            if not (0 <= az <= 360):
                raise ValueError('Azimuth out of range (0-360)')
            if not (0 <= el <= 90):
                raise ValueError('Elevation out of range (0-90)')
            self.antenna_queue.put({'azimuth': az, 'elevation': el})
            self.log(f'Set antenna: az={az}, el={el}')
            return True
        except Exception as e:
            self.log(f'Error setting antenna: {e}')
            return False

    def get_status(self):
        """
        Get receiver status (e.g., 'Locked' or 'Signal lost').
        Returns:
            Status string
        """
        self.log(f'Get status: {self.status}')
        return self.status

# Example usage (for testing)
if __name__ == '__main__':
    api = XLAPI()
    print('Send signal:', api.send_signal_data('2025-07-12 22:00:00', 1234.5, 20.1))
    print('Set antenna:', api.set_antenna(180, 45))
    print('Set antenna (bad):', api.set_antenna(400, -10))
    print('Status:', api.get_status()) 