from quad import Quad
from parameter_tree import ParameterTree
import logging


class ChannelData(object):
    """Data tree to represent one channel on a quad."""

    def __init__(self, quad, channel):
        self.quad = quad
        self.channel = channel

        self.param_tree = ParameterTree({
            "voltage": (self.getVoltage, None),
            "current": (self.getCurrent, None),
            "fusevoltage": (self.getFuse, None),
            "enabled": (self.get_enable, None),
            "enable": (False,  self.set_enable),
            })

        #self.param_tree.addCallback("enable/", self.set_enable)

    def getVoltage(self):
        return self.quad.get_channel_voltage(self.channel)

    def getFuse(self):
        return self.quad.get_fuse_voltage(self.channel)

    def getCurrent(self):
        return self.quad.get_channel_current(self.channel)

    def get_enable(self):
        return self.quad.get_enable(self.channel)

    # def set_enable(self, path, val):
    def set_enable(self, val):
        self.quad.set_enable(self.channel, val)


class QuadData(object):
    """Data tree to represent an entire quad."""

    def __init__(self, *args, **kwargs):
        # if len(args) and isinstance(args[0], Quad):
        #     self.quad = args[0]
        # else:
        #     self.quad = Quad(*args, **kwargs)

        if 'quad' in kwargs:
            self.quad = kwargs['quad']
        else:
            self.quad = Quad(*args, **kwargs)

        self.channels = [ChannelData(self.quad, i) for i in range(4)]

        self.param_tree = ParameterTree({
            "channels": [
                self.channels[0].param_tree,
                self.channels[1].param_tree,
                self.channels[2].param_tree,
                self.channels[3].param_tree
                ],
            "supply": (self.get_supply_voltage, None),
            })

    def get_supply_voltage(self):
        return self.quad.get_supply_voltage()
