"""Test TempData, HumidityData and PSCUData classes from lpdpower.

Tim Nicholls, STFC Application Engineering Group
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
from lpdpower.pscu_data import TempData, HumidityData, PSCUData, PSCUDataError
from lpdpower.parameter_tree import ParameterAccessor

class TestTempData():
    
    @classmethod
    @patch('lpdpower.i2c_device.smbus.SMBus')
    def setup_class(cls, mock_bus):
        cls.pscu = Mock()
        cls.sensor_idx = 1
        cls.temp_data = TempData(cls.pscu, cls.sensor_idx)
        
    def test_setpoint_get(self):
        self.temp_data.param_tree.get('setpoint')
        self.pscu.get_temp_set_point.assert_called_with(self.sensor_idx)
        
    def test_temp_get(self):
        self.temp_data.param_tree.get('temperature')
        self.pscu.get_temperature.assert_called_with(self.sensor_idx)
        
    def test_trace_get(self):
        self.temp_data.param_tree.get('trace')
        self.pscu.get_temp_trace.assert_called_with(self.sensor_idx)

    def test_tripped_get(self):
        self.temp_data.param_tree.get('tripped')
        self.pscu.get_temp_tripped.assert_called_with(self.sensor_idx)

    def test_disabled_get(self):
        self.temp_data.param_tree.get('disabled')
        self.pscu.get_temp_disabled.assert_called_with(self.sensor_idx)

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
        
class TestPscuData():
    
    @classmethod
    def setup_class(cls):
        cls.pscu = Mock()
        cls.pscu.numQuads = 4
        cls.pscu.quad = [Mock()] * cls.pscu.numQuads
        cls.pscu.get_all_latched.return_value = [True]*4
        cls.pscu_data = PSCUData(pscu=cls.pscu)
        
    @patch('lpdpower.pscu_data.PSCU')
    def test_pscu_data_no_pscu_arg(self, mock_pscu):
        pd = PSCUData()
        assert(pd.pscu is not None)

    def test_get_param(self):
        
        val = self.pscu_data.get('position')
        self.pscu.get_position.assert_called()
        
    def test_set_param(self):
        
        enabled = True
        self.pscu_data.set('allEnabled', enabled)
        self.pscu.enable_all.assert_called_with(enabled)
        
    def test_get_missing_param(self):
        
        missing_param = 'missing_param'
        with assert_raises_regexp(PSCUDataError, 'The path {} is invalid'.format(missing_param)):
            self.pscu_data.get(missing_param)
    
    def test_set_missing_param(self):
        
        missing_param = 'missing_param'
        with assert_raises_regexp(PSCUDataError, 'Invalid path: {}'.format(missing_param)):
            self.pscu_data.set(missing_param, 0)
            
    def test_get_all_latched(self):
        
        self.pscu_data.get_all_latched()
        self.pscu.get_all_latched.assert_called()
        
    def test_get_quad_traces(self):
        
        traces = self.pscu_data.get_quad_traces()
        assert_equal(len(traces), self.pscu.numQuads)
        self.pscu.get_quad_trace.assert_has_calls([call(i) for i in range(self.pscu.numQuads)])    