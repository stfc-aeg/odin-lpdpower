from I2CContainer import I2CContainer
from tca9548 import TCA9548
from ad7998 import AD7998
from mcp23008 import MCP23008
from quad import Quad

#PSCU consisting of 4x Quads & Other sensors
class PSCU(I2CContainer):
	def __init__(self):
		self.tca = TCA9548(0x70)
		
		#Attach quads to tca
		self.quad = []
		for i in range(4):
			self.quad.append(self.tca.attachDevice(i, Quad))

		#Attach bus 4 devices
		#Temperature monitor AD7998s
		self.adcTempMon = []
		self.adcTempMon.append(self.tca.attachDevice(4, AD7998, 0x21))
		self.adcTempMon.append(self.tca.attachDevice(4, AD7998, 0x22))
		self.adcTempMon.append(self.tca.attachDevice(4, AD7998, 0x23))

		#Temperature control MCP23008s
		self.mcpTempMon = []
		self.mcpTempMon.append(self.tca.attachDevice(4, MCP23008, 0x24))
		self.mcpTempMon.append(self.tca.attachDevice(4, MCP23008, 0x25))
		self.mcpTempMon.append(self.tca.attachDevice(4, MCP23008, 0x26))
		self.mcpTempMon.append(self.tca.attachDevice(4, MCP23008, 0x27))

		#Attach bus 5 devices
		#Misc AD7998s
		self.adcMisc = []
		self.adcMisc.append(self.tca.attachDevice(5, AD7998, 0x21))
		self.adcMisc.append(self.tca.attachDevice(5, AD7998, 0x22))

		#Misc MCP23008s
		self.mcpMisc = []
		self.mcpMics.append(self.tca.attachDevice(5, MCP23008, 0x24))
		self.mcpMics.append(self.tca.attachDevice(5, MCP23008, 0x25))
		self.mcpMics.append(self.tca.attachDevice(5, MCP23008, 0x26))
		self.mcpMics.append(self.tca.attachDevice(5, MCP23008, 0x27))

		#Fan speed AD5321
		self.fanSpd = self.tca.attachDevice(5, AD5321, 0x0c)

	def enableAll(self):
		pass #Enable quads in turn	
