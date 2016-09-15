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
            "enabled": (self.getEnable, None),
            "enable": (False,  self.setEnable),
            })

        #self.param_tree.addCallback("enable/", self.setEnable)

    def getVoltage(self):
        return self.quad.getChannelVoltage(self.channel)

    def getFuse(self):
        return self.quad.getFuseVoltage(self.channel)

    def getCurrent(self):
        return self.quad.getChannelCurrent(self.channel)

    def getEnable(self):
        return self.quad.getEnable(self.channel)

    # def setEnable(self, path, val):
    def setEnable(self, val):
        self.quad.setEnable(self.channel, val)


class QuadData(object):
    """Data tree to represent an entire quad."""

    def __init__(self, *args, **kwargs):
        if len(args) and isinstance(args[0], Quad):
            self.quad = args[0]
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
            "supply": self.getSupplyVoltage,
            })

    def getSupplyVoltage(self):
        return self.quad.getSupplyVoltage()
