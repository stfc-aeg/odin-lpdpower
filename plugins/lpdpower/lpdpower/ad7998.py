from i2c_device import I2CDevice, I2CException

class AD7998(I2CDevice):
	def __init__(self, address = 0x20, **kwargs):
		I2CDevice.__init__(self, address, **kwargs)

		#Set cycle register to fastest
		self.write8(3, 1)

	#Gets the raw input from a conversion
	def readInputRaw(self, channel):

		#Trigger a conversion on channel
		#Sets upper 4 bits of addr pointer
		self.write8(0x70 + ((channel + 1) << 4), 0)

		#Read conversion data
		return self.readU16(0)
	
	#Gets the input from a conversion bound to a 0-1 range
	def readInput01(self, channel):
		data = self.readInputRaw(channel)

		#Swap bytes
		data = ((data & 0xff) << 8) + ((data & 0xff00) >> 8)
		
		#Ignore channel identifier
		data &= 0xfff

		return data / 4095.0
