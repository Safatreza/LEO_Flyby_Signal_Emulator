"""
Test suite for orbit_sim.py module
Tests orbital calculations, TLE parsing, and error handling for LEO satellite flyby emulator
"""
import pytest
import sys
import os
import tempfile
import yaml
import numpy as np
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from flyby_model.orbit_sim import load_config, load_tle, simulate_flyby
    from skyfield.api import load
    SKYFIELD_AVAILABLE = True
except ImportError:
    SKYFIELD_AVAILABLE = False

# Sample TLE data for testing
SAMPLE_TLE = """ISS (ZARYA)
1 25544U 98067A   21073.51041667  .00001264  00000-0  29621-4 0  9993
2 25544  51.6462  21.4372 0002187  80.3702  37.2822 15.48915322273626"""

# Sample ground station data
SAMPLE_GROUND_STATION = {
    'latitude_deg': 37.7749,
    'longitude_deg': -122.4194,
    'elevation_m': 10
}

# Sample simulation parameters
SAMPLE_SIMULATION = {
    'duration_sec': 60,  # Short duration for testing
    'time_step_sec': 10  # Larger time step for faster tests
}


class TestOrbitSimulator:
    """Test class for orbit simulation functionality"""
    
    @pytest.fixture
    def temp_tle_file(self):
        """Create a temporary TLE file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(SAMPLE_TLE)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        os.unlink(temp_path)
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file for testing"""
        config = {
            'ground_station': SAMPLE_GROUND_STATION,
            'simulation': SAMPLE_SIMULATION
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        os.unlink(temp_path)
    
    def test_load_config_valid(self, temp_config_file):
        """Test loading valid configuration from YAML file"""
        if not SKYFIELD_AVAILABLE:
            pytest.skip("Skyfield not available")
        
        gs, sim = load_config(temp_config_file)
        
        assert gs['latitude_deg'] == 37.7749
        assert gs['longitude_deg'] == -122.4194
        assert gs['elevation_m'] == 10
        assert sim['duration_sec'] == 60
        assert sim['time_step_sec'] == 10
    
    def test_load_config_invalid_path(self):
        """Test loading configuration from non-existent file"""
        with pytest.raises(RuntimeError, match="Failed to load config"):
            load_config("nonexistent_file.yaml")
    
    def test_load_tle_valid(self, temp_tle_file):
        """Test loading valid TLE from file"""
        if not SKYFIELD_AVAILABLE:
            pytest.skip("Skyfield not available")
        
        name, line1, line2 = load_tle(temp_tle_file)
        
        assert name == "ISS (ZARYA)"
        assert line1.startswith("1 25544U")
        assert line2.startswith("2 25544")
    
    def test_load_tle_invalid_path(self):
        """Test loading TLE from non-existent file"""
        with pytest.raises(RuntimeError, match="Failed to load TLE"):
            load_tle("nonexistent_file.txt")
    
    def test_load_tle_incomplete(self):
        """Test loading incomplete TLE file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("ISS (ZARYA)\n1 25544U 98067A")  # Missing line 2
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="TLE file must have at least 3 lines"):
                load_tle(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_simulate_flyby_valid_data(self, temp_tle_file, temp_config_file):
        """Test complete flyby simulation with valid data"""
        if not SKYFIELD_AVAILABLE:
            pytest.skip("Skyfield not available")
        
        gs, sim = load_config(temp_config_file)
        tle_lines = load_tle(temp_tle_file)
        
        df = simulate_flyby(gs, sim, tle_lines)
        
        # Check DataFrame structure
        assert len(df) > 0
        assert 'time' in df.columns
        assert 'azimuth' in df.columns
        assert 'elevation' in df.columns
        assert 'range' in df.columns
        assert 'velocity' in df.columns
        assert 'below_horizon' in df.columns
        
        # Check data types and ranges
        assert all(0 <= az <= 360 for az in df['azimuth'] if not np.isnan(az))
        assert all(-90 <= el <= 90 for el in df['elevation'] if not np.isnan(el))
        assert all(r > 0 for r in df['range'] if not np.isnan(r))
        assert all(v > 0 for v in df['velocity'] if not np.isnan(v))
        
        # Check that below_horizon flag works
        below_horizon_mask = df['elevation'] < 0
        assert all(df.loc[below_horizon_mask, 'below_horizon'] == True)
    
    def test_simulate_flyby_invalid_ground_station(self, temp_tle_file):
        """Test simulation with invalid ground station coordinates"""
        if not SKYFIELD_AVAILABLE:
            pytest.skip("Skyfield not available")
        
        # Invalid ground station (non-numeric coordinates)
        invalid_gs = {
            'latitude_deg': 'invalid',
            'longitude_deg': -122.4194,
            'elevation_m': 10
        }
        
        sim = SAMPLE_SIMULATION
        tle_lines = load_tle(temp_tle_file)
        
        with pytest.raises(ValueError, match="Invalid ground station coordinates"):
            simulate_flyby(invalid_gs, sim, tle_lines)
    
    def test_simulate_flyby_invalid_tle(self, temp_config_file):
        """Test simulation with invalid TLE data"""
        if not SKYFIELD_AVAILABLE:
            pytest.skip("Skyfield not available")
        
        gs, sim = load_config(temp_config_file)
        
        # Invalid TLE lines
        invalid_tle = ("INVALID", "invalid line 1", "invalid line 2")
        
        with pytest.raises(ValueError, match="Invalid TLE"):
            simulate_flyby(gs, sim, invalid_tle)
    
    def test_satellite_below_horizon(self, temp_tle_file, temp_config_file):
        """Test handling of satellite below horizon"""
        if not SKYFIELD_AVAILABLE:
            pytest.skip("Skyfield not available")
        
        gs, sim = load_config(temp_config_file)
        tle_lines = load_tle(temp_tle_file)
        
        df = simulate_flyby(gs, sim, tle_lines)
        
        # Check that below_horizon flag is correctly set
        below_horizon_count = df['below_horizon'].sum()
        negative_elevation_count = (df['elevation'] < 0).sum()
        
        # All negative elevations should be marked as below horizon
        assert below_horizon_count == negative_elevation_count
        
        # Check that below horizon entries have negative elevation
        below_horizon_data = df[df['below_horizon'] == True]
        if len(below_horizon_data) > 0:
            assert all(below_horizon_data['elevation'] < 0)
    
    def test_time_formatting(self, temp_tle_file, temp_config_file):
        """Test that time column is properly formatted"""
        if not SKYFIELD_AVAILABLE:
            pytest.skip("Skyfield not available")
        
        gs, sim = load_config(temp_config_file)
        tle_lines = load_tle(temp_tle_file)
        
        df = simulate_flyby(gs, sim, tle_lines)
        
        # Check time format (should be YYYY-MM-DD HH:MM:SS)
        for time_str in df['time']:
            try:
                datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pytest.fail(f"Invalid time format: {time_str}")
    
    def test_simulation_duration(self, temp_tle_file, temp_config_file):
        """Test that simulation generates correct number of data points"""
        if not SKYFIELD_AVAILABLE:
            pytest.skip("Skyfield not available")
        
        gs, sim = load_config(temp_config_file)
        tle_lines = load_tle(temp_tle_file)
        
        df = simulate_flyby(gs, sim, tle_lines)
        
        # Expected number of points: duration / time_step + 1
        expected_points = (sim['duration_sec'] // sim['time_step_sec']) + 1
        assert len(df) == expected_points


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 