"""Test HumidityData class from lpdpower.

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
from lpdpower.humidity_data import HumidityData

class TestHumidityData():

    @classmethod
    def setup_class(cls):
        cls.pscu = Mock()
        cls.sensor_idx = 1
        cls.humidity_data = HumidityData(cls.pscu, cls.sensor_idx)

    def test_setpoint_get(self):
        self.humidity_data.param_tree.get('setpoint')
        self.pscu.get_humidity_set_point.assert_called_with(self.sensor_idx)

    def test_temp_get(self):
        self.humidity_data.param_tree.get('humidity')
        self.pscu.get_humidity.assert_called_with(self.sensor_idx)

    def test_trace_get(self):
        self.humidity_data.param_tree.get('trace')
        self.pscu.get_humidity_trace.assert_called_with(self.sensor_idx)

    def test_tripped_get(self):
        self.humidity_data.param_tree.get('tripped')
        self.pscu.get_humidity_tripped.assert_called_with(self.sensor_idx)

    def test_disabled_get(self):
        self.humidity_data.param_tree.get('disabled')
        self.pscu.get_humidity_disabled.assert_called_with(self.sensor_idx)

    def test_name_get(self):
        self.humidity_data.param_tree.get('sensor_name')
        self.pscu.get_humidity_name.assert_called_with(self.sensor_idx)

    def test_mode_get(self):
        self.humidity_data.param_tree.get('mode')
        self.pscu.get_humidity_mode.assert_called_with(self.sensor_idx)