from I2CDevice import I2CDevice, I2CException
import Adafruit_GPIO as GPIO

#Class for the MCP23008 designed to be drop-in replacement for Adafruit class
class MCP23008(I2CDevice):
	def __init__(self, address = 0x20, **kwargs):
		I2CDevice.__init__(self, address, **kwargs)

		#Default settings
		self.write8(0, 0) #All outputs
		self.write8(6, 0) #All pullups disabled
		self.write8(9, 0)

		self.__gpioBuff = 0
		self.__pullupBuff = 0
		self.__ioBuff = 0
	
	#Get the input for a single pin
	def input(self, pin):
		return self.input_pins([pin])[0]
	
	#Get the input for multiple pins [pin, pin...]
	def input_pins(self, pins):
		#Read GPIO register
		buff = self.readU8(9)
		
		return [bool(buff & (1 << pin)) for pin in pins]

	#Sets the output of a single pin
	def output(self, pin, value):
		self.output_pins({pin : value})

	#Sets the output of multiple pins {pin:GPIO.OUT, pin:GPIO...}
	def output_pins(self, pins):
		for pin, val in pins.items():
			if val:
				self.__gpioBuff |= 1 << pin
			else:
				self.__gpioBuff &= ~(1 << pin)
		self.write8(9, self.__gpioBuff)

	#Sets all outputs low
	def disableOutputs(self):
		self.write8(9, 0)
		self.__gpioBuff = 0

	#Sets the pullup of a pin
	def pullup(self, pin, enabled):
		if enabled:
			self.__pullupBuff |= 1 << pin
		else:
			self.__pullupBuff &= ~(1 << pin)
		self.write8(6, self.__pullupBuff)
	
	#Sets whether a pin is an input or output
	def setup(self, pin, value):
		if value == GPIO.IN:
			self.__ioBuff |= 1 << pin
		elif value == GPIO.OUT:
			self.__ioBuff &= ~(1 << pin)
		else:
			raise ValueError("MCP23008::setup() expected a value of GPIO.IN or GPIO.OUT")
		
		self.write8(0, self.__ioBuff)
