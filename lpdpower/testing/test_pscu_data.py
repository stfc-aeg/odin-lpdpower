"""Test PSCUData class from lpdpower.

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
from odin.adapters.parameter_tree import ParameterAccessor
from lpdpower.pscu_data import PSCUData, PSCUDataError


class TestPscuData():

    @classmethod
    def setup_class(cls):
        cls.pscu = Mock()
        cls.pscu.num_humidities = 2
        cls.pscu.num_temperatures = 11
        cls.pscu.num_quads = 4
        cls.pscu.num_leak_sensors = 1
        cls.pscu.quad = [Mock()] * cls.pscu.num_quads
        for quad in cls.pscu.quad:
            quad.num_channels = 4
        cls.pscu.get_all_latched.return_value = [True]*4
        cls.pscu_data = PSCUData(pscu=cls.pscu)

    @patch('lpdpower.pscu_data.PSCU')
    def test_pscu_data_no_pscu_arg(self, mock_pscu):
        pd = PSCUData()
        assert(pd.pscu is not None)

    def test_get_param(self):

        val = self.pscu_data.get('position')
        self.pscu.get_position.assert_called_with()

    def test_set_param(self):

        enabled = True
        self.pscu_data.param_tree._tree['allEnabled']._type = bool
        self.pscu_data.set('allEnabled', enabled)
        self.pscu.enable_all.assert_called_with(enabled)

    def test_get_missing_param(self):

        missing_param = 'missing_param'
        with assert_raises_regexp(PSCUDataError, 'Invalid path: {}'.format(missing_param)):
            self.pscu_data.get(missing_param)

    def test_set_missing_param(self):

        missing_param = 'missing_param'
        with assert_raises_regexp(PSCUDataError, 'Invalid path: {}'.format(missing_param)):
            self.pscu_data.set(missing_param, 0)

    def test_get_all_latched(self):

        self.pscu_data.get_all_latched()
        self.pscu.get_all_latched.assert_called_with()

    def test_get_quad_traces(self):

        traces = self.pscu_data.get_quad_traces()
        assert_equal(len(traces), self.pscu.num_quads)
        self.pscu.get_quad_trace.assert_has_calls([call(i) for i in range(self.pscu.num_quads)])
