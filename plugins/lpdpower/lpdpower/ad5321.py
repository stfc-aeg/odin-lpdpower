from I2CDevice import I2CDevice

class AD5321(I2CDevice):
	def __init__(self, address = 0xc, **kwargs):
		I2CDevice.__init__(self, address, **kwargs)

	#Sets the output voltage of the DAC (value must be bound to [0-1])
	def setOutput01(self, value):
		value = int(value * 4096)
		self.write16(0, value)

if __name__ == "__main__":
	dac = AD5321()
	dac.setOutput01(0.2)
	print dac.readU16(0) / 4096.0
