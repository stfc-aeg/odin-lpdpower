"""Quad - device class for the LPD Quad power supply box.

This class implements support tor the I2C control and monitoring functionality of the
LPD Quad power supply box. This allows all elements of the device to be accessed via
the I2C bus.

James Hogge, STFC Application Engineering Group.
"""
from lpdpower.i2c_device import I2CException
from lpdpower.i2c_container import I2CContainer
from lpdpower.mcp23008 import MCP23008
from lpdpower.ad7998 import AD7998


class Quad(I2CContainer):
    """Quad class.

    This class implements support for the LPD Quad power supply box.
    """

    # Number of output channels on the Quad box
    NUM_CHANNELS = 4

    def __init__(self):
        """Initialise the Quad device.

        This method initialises the Quad device, setting up the internal
        I2C devices into the appropriate modes and creating internal buffer variables
        for all sensor channels.
        """
        I2CContainer.__init__(self)

        self.num_channels = Quad.NUM_CHANNELS

        # Set up MCP GPIO device - first 4 channels are output enables, second 4 channels
        # are enable status inputs
        self.mcp = self.attach_device(MCP23008, 0x20)

        for i in range(self.num_channels):
            self.mcp.setup(i, MCP23008.OUT)

        for i in range(self.num_channels, self.num_channels*2):
            self.mcp.setup(i, MCP23008.IN)

        # Attach ADC devices for monitoring
        self.adcPower = self.attach_device(AD7998, 0x22)
        self.adcFuse = self.attach_device(AD7998, 0x21)

        # Create internal buffers for all sensor channels
        self.__channelVoltage = [0.0] * self.num_channels
        self.__channelCurrent = [0.0] * self.num_channels
        self.__fuseVoltage = [0.0] * self.num_channels
        self.__channelEnable = [False] * self.num_channels
        self.__supplyVoltage = 0.0

    def get_channel_voltage(self, channel):
        """Get output channel voltage.

        This method returns the current voltage on the specified output channel.

        :param channel: channel to get value for
        :return channel output voltage in volts
        """
        if channel > 3 or channel < 0:
            raise I2CException(
                "%s is not a channel on the Quad. Must be between 0 & 3" % channel)

        return self.__channelVoltage[channel]

    def get_channel_current(self, channel):
        """Get output channel current.

        This method returns the current current on the specified output channel.

        :param channel: channel to get value for
        :return channel output current in amps
        """
        if channel > 3 or channel < 0:
            raise I2CException(
                "%s is not a channel on the Quad. Must be between 0 & 3" % channel)

        return self.__channelCurrent[channel]

    def get_fuse_voltage(self, channel):
        """Get output channel fuse voltage.

        This method returns the current voltage before the fuse on the specified channel.

        :param channel: channel to get value for
        :return channel output fuse voltage in volts
        """
        if channel > 3 or channel < 0:
            raise I2CException("%s is not a channel on the Quad. Must be between 0 & 3" % channel)

        return self.__fuseVoltage[channel]

    def get_enable(self, channel):
        """Get output channel enable.

        This method returns the enable status for the specified channel.

        :param channel: channel to get value for
        :return channel enable status as bool
        """
        if channel > 3 or channel < 0:
            raise I2CException("%s is not a channel on the Quad. Must be between 0 & 3" % channel)

        return self.__channelEnable[channel]

    def get_supply_voltage(self):
        """Get the Quad box supply voltage.

        This method returns the Quad supply voltage.

        :return supply voltage in volts
        """
        return self.__supplyVoltage

    def set_enable(self, channel, enabled):
        """Set the output enable for a given channel.

        This method sets the ouput enable for given channel to the specified state.

        :param channel: channel to set enable for
        :param enabled: bool enabled value for the channel
        """
        self.set_enables({channel: enabled})

    # Sets multiple channels on or off
    def set_enables(self, channels):
        """Set the output enable for multiple channels.

        This method sets the output enable state of multiple channels specified in a
        dict of channel: enabled pairs, e.g. {0: True, 1: False, ...}.

        :param channels: dict of channel enables to set
        """
        data = {}

        for channel in channels:
            if channel > 3 or channel < 0:
                raise I2CException(
                    "%s is not a channel on the Quad. Must be between 0 & 3" % channel)

            # If the channel is not currently in the desired state (on/off)
            if self.get_enable(channel) != channels[channel]:
                data[channel] = True

        # No channels to toggle
        if not len(data):
            return

        # Toggle the output enable of the Quad to set the appropriate enable state.
        # A 0-1-0 transition is required by the control circuit to enable a channel.
        self.mcp.disable_outputs()
        self.mcp.output_pins(data)
        self.mcp.disable_outputs()

    def poll_all_sensors(self):
        """Poll all sensor channels into buffer variables.

        This method polls all sensor channels into the internal buffer variables. This mechanism
        allows the polling rate to be controlled independently of any get_xxx calls being made
        by client software.
        """
        # Read and udpate the output enable states
        enable_pins = range(4, 4 + self.NUM_CHANNELS)
        self.__channelEnable = self.mcp.input_pins(enable_pins)

        # For each channel read an dupate the voltage and current values
        for channel in range(self.NUM_CHANNELS):
            self.__channelVoltage[channel] = self.adcPower.read_input_scaled(channel) * 5 * 16
            self.__channelCurrent[channel] = self.adcPower.read_input_scaled(channel + 4) * 5 * 4
            self.__fuseVoltage[channel] = self.adcFuse.read_input_scaled(channel) * 5 * 16

        # Read and update the supply voltage
        self.__supplyVoltage = self.adcFuse.read_input_scaled(4) * 5 * 16
