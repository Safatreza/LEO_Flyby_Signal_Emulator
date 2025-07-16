"""
Test suite for signal_model.py module
Tests signal calculations, noise modeling, and error handling for LEO satellite flyby emulator
"""
import pytest
import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flyby_model.signal_model import (
    load_signal_config, calculate_doppler_shift, calculate_path_loss,
    calculate_thermal_noise, calculate_atmospheric_attenuation,
    calculate_snr, simulate_signal
)

# Mock orbit data for testing
MOCK_ORBIT_DATA = pd.DataFrame({
    'time': ['2025-07-12 22:00:00', '2025-07-12 22:00:01', '2025-07-12 22:00:02'],
    'range': [500.0, 450.0, 400.0],  # km
    'velocity': [7.0, 7.2, 7.5],     # km/s
    'elevation': [45.0, 60.0, 75.0]  # degrees
})

# Mock signal parameters
MOCK_SIGNAL_CONFIG = {
    'frequency_hz': 2400000000,  # 2.4 GHz
    'tx_power_dbm': 20,
    'tx_gain_db': 20,
    'rx_gain_db': 20,
    'bandwidth_hz': 1000000,     # 1 MHz
    'system_noise_temp_k': 290
}


class TestSignalModel:
    """Test class for signal model functionality"""
    
    def test_load_signal_config_valid(self, tmp_path):
        """Test loading valid signal configuration from YAML"""
        import yaml
        
        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({'signal': MOCK_SIGNAL_CONFIG}, f)
        
        config = load_signal_config(str(config_file))
        
        assert config['frequency_hz'] == 2400000000
        assert config['tx_power_dbm'] == 20
        assert config['rx_gain_db'] == 20
        assert config['bandwidth_hz'] == 1000000
    
    def test_load_signal_config_invalid_path(self):
        """Test loading signal configuration from non-existent file"""
        with pytest.raises(RuntimeError, match="Failed to load signal config"):
            load_signal_config("nonexistent_file.yaml")
    
    def test_calculate_doppler_shift(self):
        """Test Doppler shift calculations"""
        # Test positive velocity (approaching)
        doppler = calculate_doppler_shift(7.0, 2400000000)  # 7 km/s, 2.4 GHz
        assert doppler > 0  # Should be positive for approaching satellite
        
        # Test negative velocity (receding)
        doppler = calculate_doppler_shift(-7.0, 2400000000)
        assert doppler < 0  # Should be negative for receding satellite
        
        # Test zero velocity
        doppler = calculate_doppler_shift(0.0, 2400000000)
        assert doppler == 0.0
        
        # Test different frequencies
        doppler_1 = calculate_doppler_shift(7.0, 1000000000)  # 1 GHz
        doppler_2 = calculate_doppler_shift(7.0, 2400000000)  # 2.4 GHz
        assert doppler_2 > doppler_1  # Higher frequency = larger Doppler shift
    
    def test_calculate_path_loss(self):
        """Test free-space path loss calculations"""
        # Test path loss increases with distance
        loss_1 = calculate_path_loss(100.0, 2400000000)  # 100 km
        loss_2 = calculate_path_loss(500.0, 2400000000)  # 500 km
        assert loss_2 > loss_1  # Longer distance = more path loss
        
        # Test path loss increases with frequency
        loss_1 = calculate_path_loss(500.0, 1000000000)  # 1 GHz
        loss_2 = calculate_path_loss(500.0, 2400000000)  # 2.4 GHz
        assert loss_2 > loss_1  # Higher frequency = more path loss
        
        # Test path loss is always positive
        loss = calculate_path_loss(500.0, 2400000000)
        assert loss > 0
    
    def test_calculate_thermal_noise(self):
        """Test thermal noise calculations"""
        # Test noise increases with bandwidth
        noise_1 = calculate_thermal_noise(1000000)   # 1 MHz
        noise_2 = calculate_thermal_noise(10000000)  # 10 MHz
        assert noise_2 > noise_1  # Higher bandwidth = more noise
        
        # Test noise is always negative (in dBm)
        noise = calculate_thermal_noise(1000000)
        assert noise < 0  # Thermal noise in dBm should be negative
    
    def test_calculate_atmospheric_attenuation(self):
        """Test atmospheric attenuation calculations"""
        # Test low elevation angle (< 10°) has attenuation
        att_low = calculate_atmospheric_attenuation(5.0, 500.0)   # 5° elevation
        assert att_low > 0  # Should have atmospheric attenuation
        
        # Test high elevation angle (≥ 10°) has no attenuation
        att_high = calculate_atmospheric_attenuation(45.0, 500.0)  # 45° elevation
        assert att_high == 0.0  # Should have no atmospheric attenuation
        
        # Test attenuation increases with range for low elevation
        att_1 = calculate_atmospheric_attenuation(5.0, 100.0)  # 100 km
        att_2 = calculate_atmospheric_attenuation(5.0, 500.0)  # 500 km
        assert att_2 > att_1  # Longer range = more attenuation
    
    def test_calculate_snr(self):
        """Test signal-to-noise ratio calculations"""
        # Test SNR calculation with typical values
        tx_power = 20    # dBm
        tx_gain = 20     # dB
        rx_gain = 20     # dB
        path_loss = 120  # dB
        atmospheric_loss = 2.0  # dB
        noise_power = -120  # dBm
        
        snr = calculate_snr(tx_power, tx_gain, rx_gain, path_loss, atmospheric_loss, noise_power)
        
        # SNR should be: tx_power + tx_gain + rx_gain - path_loss - atmospheric_loss - noise_power
        expected_snr = 20 + 20 + 20 - 120 - 2.0 - (-120)  # Note: noise_power is negative
        assert abs(snr - expected_snr) < 0.1  # Allow small floating point differences
        
        # Test SNR decreases with more path loss
        snr_1 = calculate_snr(20, 20, 20, 100, 2.0, -120)
        snr_2 = calculate_snr(20, 20, 20, 150, 2.0, -120)
        assert snr_2 < snr_1  # More path loss = lower SNR
    
    def test_simulate_signal_complete(self):
        """Test complete signal simulation with mock data"""
        signal_df = simulate_signal(MOCK_ORBIT_DATA, MOCK_SIGNAL_CONFIG)
        
        # Check DataFrame structure
        assert len(signal_df) == len(MOCK_ORBIT_DATA)
        assert 'time' in signal_df.columns
        assert 'doppler_shift' in signal_df.columns
        assert 'path_loss' in signal_df.columns
        assert 'snr' in signal_df.columns
        assert 'atmospheric_loss' in signal_df.columns
        assert 'below_horizon' in signal_df.columns
        
        # Check data types and ranges
        assert (~signal_df['doppler_shift'].isna()).all()
        assert (signal_df['path_loss'] > 0).all()
        assert (signal_df['atmospheric_loss'] >= 0).all()
        
        # Check that all satellites are above horizon (elevation > 0)
        assert (signal_df['below_horizon'] == False).all()
    
    def test_simulate_signal_below_horizon(self):
        """Test signal simulation with satellite below horizon"""
        # Create orbit data with negative elevation
        below_horizon_data = MOCK_ORBIT_DATA.copy()
        below_horizon_data.loc[0, 'elevation'] = -10.0  # Below horizon
        
        signal_df = simulate_signal(below_horizon_data, MOCK_SIGNAL_CONFIG)
        
        # Check that below horizon entries have NaN values
        below_horizon_mask = signal_df['below_horizon'] == True
        if below_horizon_mask.any():
            assert all(signal_df.loc[below_horizon_mask, 'doppler_shift'].isna())
            assert all(signal_df.loc[below_horizon_mask, 'path_loss'].isna())
            assert all(signal_df.loc[below_horizon_mask, 'snr'].isna())
    
    def test_simulate_signal_invalid_inputs(self):
        """Test signal simulation with invalid inputs"""
        # Test with invalid orbit data (missing required columns)
        invalid_orbit_data = pd.DataFrame({
            'time': ['2025-07-12 22:00:00'],
            'range': [500.0]
            # Missing velocity and elevation
        })
        
        with pytest.raises(KeyError):
            simulate_signal(invalid_orbit_data, MOCK_SIGNAL_CONFIG)
    
    def test_doppler_shift_edge_cases(self):
        """Test Doppler shift calculations with edge cases"""
        # Test very high velocity
        doppler = calculate_doppler_shift(100.0, 2400000000)  # 100 km/s
        assert doppler > 0
        
        # Test very low velocity
        doppler = calculate_doppler_shift(0.001, 2400000000)  # 1 m/s
        # The expected value is (0.001*1000/299792458)*2.4e9 = ~8.0055 Hz
        assert abs(doppler - 8.0055) < 0.1  # Should be about 8 Hz
        
        # Test zero frequency (should return zero)
        doppler = calculate_doppler_shift(1.0, 0.0)
        assert doppler == 0.0
    
    def test_path_loss_edge_cases(self):
        """Test path loss calculations with edge cases"""
        # Test very short range
        loss = calculate_path_loss(0.1, 2400000000)  # 100 m
        assert loss > 0
        
        # Test very long range
        loss = calculate_path_loss(10000.0, 2400000000)  # 10,000 km
        assert loss > 0
        
        # Test zero range (should raise error)
        with pytest.raises(ValueError):
            calculate_path_loss(0.0, 2400000000)
    
    def test_atmospheric_attenuation_edge_cases(self):
        """Test atmospheric attenuation with edge cases"""
        # Test exactly at threshold (10°)
        att = calculate_atmospheric_attenuation(10.0, 500.0)
        assert att == 0.0  # Should be exactly zero at threshold
        
        # Test very low elevation
        att = calculate_atmospheric_attenuation(1.0, 500.0)  # 1° elevation
        assert att > 0  # Should have attenuation
        
        # Test negative elevation
        att = calculate_atmospheric_attenuation(-10.0, 500.0)
        assert att > 0  # Should still have attenuation
    
    def test_snr_calculation_edge_cases(self):
        """Test SNR calculations with edge cases"""
        # Test very high SNR scenario
        snr = calculate_snr(50, 30, 30, 50, 0, -150)  # High power, low loss
        assert snr > 0
        
        # Test very low SNR scenario
        snr = calculate_snr(0, 0, 0, 200, 10, -50)  # Low power, high loss
        assert snr < 0  # Should be negative SNR


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 