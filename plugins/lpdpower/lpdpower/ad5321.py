import sys
from i2c_device import I2CDevice, I2CException

class AD5321(I2CDevice):
	def __init__(self, address = 0xc, **kwargs):
		I2CDevice.__init__(self, address, **kwargs)

	#Sets the output voltage of the DAC (value must be bound to [0-1])
	def setOutput01(self, value):
		value = int(value * 4096)
		if value == 4096:
			value = 4095
		msb = (value & 0xFF00) >> 8
		lsb = (value & 0xFF)
		self.write8(msb, lsb)

	#Reads the current value
	def readValue(self):
		value = self.readU16(0)
		#Reverse bytes
		value = ((value & 0xff00) >> 8) + ((value & 0xff) << 8)
		return value / 4096.0

if __name__ == "__main__":
	dac = AD5321()

        set_point = 0.0

	if len(sys.argv) > 1:
	    set_point = float(sys.argv[1])

	dac.setOutput01(set_point)
	dac_val = dac.readU16(0)
	dac_val = ((dac_val & 0xFF00) >> 8) | ((dac_val & 0x00FF) << 8)
	print dac_val
	print dac_val / 4096.0
