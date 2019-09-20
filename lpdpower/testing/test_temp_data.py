"""Test TempData class from lpdpower.

Tim Nicholls, STFC Detector Systems Software Group
"""

import sys
if sys.version_info[0] == 3:  # pragma: no cover
    from unittest.mock import Mock, call, patch
else:                         # pragma: no cover
    from mock import Mock, call, patch

from nose.tools import *

sys.modules['smbus'] = Mock()
sys.modules['serial'] = Mock()
sys.modules['Adafruit_BBIO'] = Mock()
sys.modules['Adafruit_BBIO.GPIO'] = Mock()
from lpdpower.temp_data import TempData

class TestTempData():

    @classmethod
    @patch('lpdpower.i2c_device.smbus.SMBus')
    def setup_class(cls, mock_bus):
        cls.pscu = Mock()
        cls.sensor_idx = 1
        cls.temp_data = TempData(cls.pscu, cls.sensor_idx)

    def test_setpoint_get(self):
        self.temp_data.param_tree.get('setpoint')
        self.pscu.get_temperature_set_point.assert_called_with(self.sensor_idx)

    def test_temp_get(self):
        self.temp_data.param_tree.get('temperature')
        self.pscu.get_temperature.assert_called_with(self.sensor_idx)

    def test_trace_get(self):
        self.temp_data.param_tree.get('trace')
        self.pscu.get_temperature_trace.assert_called_with(self.sensor_idx)

    def test_tripped_get(self):
        self.temp_data.param_tree.get('tripped')
        self.pscu.get_temperature_tripped.assert_called_with(self.sensor_idx)

    def test_disabled_get(self):
        self.temp_data.param_tree.get('disabled')
        self.pscu.get_temperature_disabled.assert_called_with(self.sensor_idx)

    def test_name_get(self):
        self.temp_data.param_tree.get('sensor_name')
        self.pscu.get_temperature_name.assert_called_with(self.sensor_idx)

    def test_mode_get(self):
        self.temp_data.param_tree.get('mode')
        self.pscu.get_temperature_mode.assert_called_with(self.sensor_idx)