from I2CDevice import I2CException
from I2CContainer import I2CContainer
from tca9548 import TCA9548
from mcp23008 import MCP23008
from ad7998 import AD7998
import Adafruit_BBIO.GPIO as GPIO
import time
import logging

class Quad(I2CContainer):
	
	def __init__(self):
		I2CContainer.__init__(self)
	
		#Set up internal I2C devices
		self.mcp = self.attachDevice(MCP23008, 0x20)

		for i in range(4):
			self.mcp.setup(i, GPIO.OUT)
			#self.mcp.pullup(i, True)

		for i in range(4, 8):
			self.mcp.setup(i, GPIO.IN)

		self.adcPower = self.attachDevice(AD7998, 0x22)
#		self.adcFuse = self.attachDevice(AD7998, 0x21)

	def getChannelVoltage(self, channel):
		if channel > 3 or channel < 0:
                	raise I2CException("%s is not a channel on the Quad. Must be between 0 & 3" % channel)

		return self.adcPower.readInput01(channel) * 5 * 16

	def getChannelCurrent(self, channel):
		if channel > 3 or channel < 0:
                	raise I2CException("%s is not a channel on the Quad. Must be between 0 & 3" % channel)

                return self.adcPower.readInput01(channel + 4) * 5 * 4

	#Gets the voltage after the fuse should be more or less equal to 48V
#	def getFuseVoltage(self, channel):
#		if channel > 3 or channel < 0:
#			raise I2CException("%s is not a channel on the Quad. Must be between 0 & 3" % channel)
#		
#		return self.adcFuse.readInput01(channel) * 5 * 16

	#Sets an individual channel on or off
	def setChannel(self, channel, enabled):
		self.setChannels({channel : enabled})

	#Sets multiple channels on or off
	def setChannels(self, channels):
		data = {}

		for channel in channels:
			if channel > 3 or channel < 0:
                        	raise I2CException("%s is not a channel on the Quad. Must be between 0 & 3" % channel)

			#If the channel is not currently in the desired state (on/off)
			if self.isEnabled(channel) != channels[channel]:
				data[channel] = True


		#No channels to toggle
                if not len(data):
                        return

		self.mcp.disableOutputs()
                self.mcp.output_pins(data)
                self.mcp.disableOutputs()

	#Checks whether a channel is enabled
	def isEnabled(self, i):
		if i > 3 or i < 0:
                        raise I2CException("%s is not a channel on the Quad. Must be between 0 & 3" % i)

		return self.mcp.input(i + 4) == GPIO.HIGH

if __name__ == "__main__":
	tca = TCA9548(0x70)
	quad = tca.attachDevice(0, Quad)

	quad.setChannels({0: True, 1: True, 2: True, 3:True})
	for chan in range(4):
		enabled = quad.isEnabled(chan)

	#quad.printTest()
