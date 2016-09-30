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
        cls.number = 1
        cls.temp_data = TempData(cls.pscu, cls.number)
        
    def test_setpoint_get(self):
        self.temp_data.param_tree.get('setpoint')
        self.pscu.getTempSetPoint.assert_called_with(self.number)
        
    def test_temp_get(self):
        self.temp_data.param_tree.get('temperature')
        self.pscu.getTemperature.assert_called_with(self.number)
        
    def test_trace_get(self):
        self.temp_data.param_tree.get('trace')
        self.pscu.getTempTrace.assert_called_with(self.number)

    def test_tripped_get(self):
        self.temp_data.param_tree.get('tripped')
        self.pscu.getTempTripped.assert_called_with(self.number)

    def test_disabled_get(self):
        self.temp_data.param_tree.get('disabled')
        self.pscu.getTempDisabled.assert_called_with(self.number)

class TestHumidityData():
    
    @classmethod
    def setup_class(cls):
        cls.pscu = Mock()
        cls.number = 1
        cls.humidity_data = HumidityData(cls.pscu, cls.number)
        
    def test_setpoint_get(self):
        self.humidity_data.param_tree.get('setpoint')
        self.pscu.getHSetPoint.assert_called_with(self.number)
        
    def test_temp_get(self):
        self.humidity_data.param_tree.get('humidity')
        self.pscu.getHumidity.assert_called_with(self.number)
        
    def test_trace_get(self):
        self.humidity_data.param_tree.get('trace')
        self.pscu.getHTrace.assert_called_with(self.number)

    def test_tripped_get(self):
        self.humidity_data.param_tree.get('tripped')
        self.pscu.getHTripped.assert_called_with(self.number)

    def test_disabled_get(self):
        self.humidity_data.param_tree.get('disabled')
        self.pscu.getHDisabled.assert_called_with(self.number)
        
class TestPscuData():
    
    @classmethod
    def setup_class(cls):
        cls.pscu = Mock()
        cls.pscu.numQuads = 4
        cls.pscu.quad = [Mock()] * cls.pscu.numQuads
        cls.pscu.getAllLatched.return_value = [True]*4
        cls.pscu_data = PSCUData(pscu=cls.pscu)
        
    @patch('lpdpower.pscu_data.PSCU')
    def test_pscu_data_no_pscu_arg(self, mock_pscu):
        pd = PSCUData()
        assert(pd.pscu is not None)

    def test_get_param(self):
        
        val = self.pscu_data.get('position')
        self.pscu.getPosition.assert_called()
        
    def test_set_param(self):
        
        enabled = True
        self.pscu_data.set('allEnabled', enabled)
        self.pscu.enableAll.assert_called_with(enabled)
        
    def test_get_missing_param(self):
        
        missing_param = 'missing_param'
        with assert_raises_regexp(PSCUDataError, 'The path {} is invalid'.format(missing_param)):
            self.pscu_data.get(missing_param)
    
    def test_set_missing_param(self):
        
        missing_param = 'missing_param'
        with assert_raises_regexp(PSCUDataError, 'Invalid path: {}'.format(missing_param)):
            self.pscu_data.set(missing_param, 0)
            
    def test_get_all_latched(self):
        
        self.pscu_data.getAllLatched()
        self.pscu.getAllLatched.assert_called()
        
    def test_get_quad_traces(self):
        
        traces = self.pscu_data.getQuadTraces()
        assert_equal(len(traces), self.pscu.numQuads)
        self.pscu.getQuadTrace.assert_has_calls([call(i) for i in range(self.pscu.numQuads)])    