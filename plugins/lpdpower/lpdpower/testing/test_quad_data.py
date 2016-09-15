"""Test QuadData and ChannelData classes from lpdpower.

Tim Nicholls, STFC Application Engineering Group
"""

import sys
if sys.version_info[0] == 3:  # pragma: no cover
    from unittest.mock import Mock, call
else:                         # pragma: no cover
    from mock import Mock, call

from nose.tools import *

sys.modules['lpdpower.quad'] = Mock()
sys.modules['lpdqwer.quad.Quad'] = Mock()
Quad = Mock
from lpdpower.quad_data import ChannelData, QuadData

class TestChannelData():

    @classmethod
    def setup_class(cls):
        cls.quad = Mock()
        cls.channel = 1
        cls.channel_data = ChannelData(cls.quad, cls.channel)

    def test_channel_voltage_get(self):
        self.channel_data.param_tree.get('voltage')
        self.quad.getChannelVoltage.assert_called_with(self.channel)

    def test_channel_current_get(self):
        self.channel_data.param_tree.get('current')
        self.quad.getChannelCurrent.assert_called_with(self.channel)

    def test_channel_fuse_get(self):
        self.channel_data.param_tree.get('fusevoltage')
        self.quad.getFuseVoltage.assert_called_with(self.channel)

    def test_channel_enable_get(self):
        self.channel_data.param_tree.get('enabled')
        self.quad.getEnable.assert_called_with(self.channel)

    def test_channel_enable_set(self):
        enable = True
        self.channel_data.param_tree.set('enable', enable)
        self.quad.setEnable.assert_called_with(self.channel, enable)

class TestQuadData():

    @classmethod
    def setup_class(cls):
        cls.quad = Quad()
        cls.quad_data = QuadData(cls.quad)

    def test_quad_supply_voltage_get(self):
        self.quad_data.param_tree.get('supply')
