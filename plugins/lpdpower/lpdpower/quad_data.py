from quad import Quad
from DataTree import DataTree
import logging


class ChannelData(object):
    """Data tree to represent one channel on a quad."""

    def __init__(self, quad, channel):
        self.quad = quad
        self.channel = channel

        self.dataTree = DataTree({
            "voltage": self.getVoltage,
            "current": self.getCurrent,
            "fusevoltage": self.getFuse,
            "enabled": self.getEnable,
            "enable": False,  # Command
            })

        self.dataTree.addCallback("enable/", self.setEnable)

    def getVoltage(self):
        return self.quad.getChannelVoltage(self.channel)

    def getFuse(self):
        return self.quad.getFuseVoltage(self.channel)

    def getCurrent(self):
        return self.quad.getChannelCurrent(self.channel)

    def getEnable(self):
        return self.quad.getEnable(self.channel)

    def setEnable(self, path, val):
        self.quad.setEnable(self.channel, val)


class QuadData(object):
    """Data tree to represent an entire quad."""

    def __init__(self, *args, **kwargs):
        if len(args) and isinstance(args[0], Quad):
            self.quad = args[0]
        else:
            self.quad = Quad(*args, **kwargs)

        self.channels = [ChannelData(self.quad, i) for i in range(4)]

        self.dataTree = DataTree({
            "channels": [
                self.channels[0].dataTree,
                self.channels[1].dataTree,
                self.channels[2].dataTree,
                self.channels[3].dataTree
                ],
            "supply": self.getSupplyVoltage,
            })

    def getSupplyVoltage(self):
        return self.quad.getSupplyVoltage()
