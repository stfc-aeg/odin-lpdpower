from I2CDevice import I2CDevice, I2CException

import logging

#Class for the MCP23008 designed to be drop-in replacement for Adafruit class
class MCP23008(I2CDevice):

	IODIR    = 0x00
	GPPU     = 0x06
	GPIO     = 0x09
	
	IN       = 0
        OUT      = 1

	def __init__(self, address = 0x20, **kwargs):

		I2CDevice.__init__(self, address, **kwargs)

		# Synchronise local buffered registered values with state of device
		self.__iodir = self.readU8(self.IODIR) 
		self.__gppu = self.readU8(self.GPPU)
		self.__gpio = self.readU8(self.GPIO)


	#Get the input for a single pin
	def input(self, pin):
		return self.input_pins([pin])[0]
	
	#Get the input for multiple pins [pin, pin...]
	def input_pins(self, pins):
		
                #Read GPIO register
		buff = self.readU8(self.GPIO)
		
		return [bool(buff & (1 << pin)) for pin in pins]

	#Sets the output of a single pin
	def output(self, pin, value):
		self.output_pins({pin : value})

	#Sets the output of multiple pins {pin:MCP23008.OUT, pin:MCP230008.IN et}
	def output_pins(self, pins):
		for pin, val in pins.items():
			if val:
				self.__gpio |= 1 << pin
			else:
				self.__gpio &= ~(1 << pin)

		self.write8(self.GPIO, self.__gpio)

	#Sets all outputs low
	def disableOutputs(self):
		self.__gpio = 0
		self.write8(self.GPIO, self.__gpio)


	#Sets the pullup of a pin
	def pullup(self, pin, enabled):
		if enabled:
			self.__gppu |= 1 << pin
		else:
			self.__gppu &= ~(1 << pin)

		self.write8(self.GPPU, self.__gppu)
	
	#Sets whether a pin is an input or output
	def setup(self, pin, value):
                
		if value == self.IN:
			self.__iodir |= 1 << pin
		elif value == self.OUT:
			self.__iodir &= ~(1 << pin)
		else:
			raise ValueError("MCP23008::setup() expected a value of MCP23008.IN or MCP23008.OUT")

		self.write8(self.IODIR, self.__iodir)
