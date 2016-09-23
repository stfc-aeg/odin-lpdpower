from i2c_device import I2CException
from i2c_container import I2CContainer
from tca9548 import TCA9548
from mcp23008 import MCP23008
from ad7998 import AD7998

import time
import logging


class Quad(I2CContainer):

    NUM_CHANNELS = 4

    def __init__(self):
        I2CContainer.__init__(self)

        # Set up internal I2C devices
        self.mcp = self.attach_device(MCP23008, 0x20)

        for i in range(self.NUM_CHANNELS):
            self.mcp.setup(i, MCP23008.OUT)
            # self.mcp.pullup(i, True)

        for i in range(self.NUM_CHANNELS, self.NUM_CHANNELS*2):
            self.mcp.setup(i, MCP23008.IN)

        self.adcPower = self.attach_device(AD7998, 0x22)
        self.adcFuse = self.attach_device(AD7998, 0x21)

        # Create internal buffers for all sensor channels
        self.__channelVoltage = [0.0] * self.NUM_CHANNELS
        self.__channelCurrent = [0.0] * self.NUM_CHANNELS
        self.__fuseVoltage = [0.0] * self.NUM_CHANNELS
        self.__channelEnable = [False] * self.NUM_CHANNELS
        self.__supplyVoltage = 0.0

    def getChannelVoltage(self, channel):
        if channel > 3 or channel < 0:
            raise I2CException(
                "%s is not a channel on the Quad. Must be between 0 & 3" % channel)

        return self.__channelVoltage[channel]

    def getChannelCurrent(self, channel):
        if channel > 3 or channel < 0:
            raise I2CException(
                "%s is not a channel on the Quad. Must be between 0 & 3" % channel)

        return self.__channelCurrent[channel]

    # Gets the voltage after the fuse should be more or less equal to 48V
    def getFuseVoltage(self, channel):
        if channel > 3 or channel < 0:
            raise I2CException("%s is not a channel on the Quad. Must be between 0 & 3" % channel)

        return self.__fuseVoltage[channel]

    # Checks whether a channel is enabled
    def getEnable(self, channel):
        if channel > 3 or channel < 0:
            raise I2CException("%s is not a channel on the Quad. Must be between 0 & 3" % channel)

        return self.__channelEnable[channel]

    def getSupplyVoltage(self):
        return self.__supplyVoltage

    # Sets an individual channel on or off
    def setEnable(self, channel, enabled):
        self.setEnables({channel: enabled})

    # Sets multiple channels on or off
    def setEnables(self, channels):
        data = {}

        for channel in channels:
            if channel > 3 or channel < 0:
                raise I2CException(
                    "%s is not a channel on the Quad. Must be between 0 & 3" % channel)

            # If the channel is not currently in the desired state (on/off)
            if self.getEnable(channel) != channels[channel]:
                data[channel] = True

        # No channels to toggle
        if not len(data):
            return

        self.mcp.disableOutputs()
        self.mcp.output_pins(data)
        self.mcp.disableOutputs()

    def pollAllSensors(self):
        """Poll all sensor channels into buffer variables."""

        enable_pins = range(4, 4 + self.NUM_CHANNELS)
        self.__channelEnable = self.mcp.input_pins(enable_pins)

        for channel in range(self.NUM_CHANNELS):
            self.__channelVoltage[channel] = self.adcPower.readInput01(channel) * 5 * 16
            self.__channelCurrent[channel] = self.adcPower.readInput01(channel + 4) * 5 * 4
            self.__fuseVoltage[channel] = self.adcFuse.readInput01(channel) * 5 * 16

        self.__supplyVoltage = self.adcFuse.readInput01(4) * 5 * 16

if __name__ == "__main__":
    tca = TCA9548(0x70)
    quad = tca.attach_device(0, Quad)

    quad.setEnables({0: True, 1: True, 2: True, 3: True})
    for chan in range(4):
        enabled = quad.getEnable(chan)

    # quad.printTest()
