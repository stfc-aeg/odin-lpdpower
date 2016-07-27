from I2CDevice import I2CDevice, I2CException
from I2CContainer import I2CContainer
import sys

#Handles enabling/disabling I2C devices connected to a TCA9548
class TCA9548(I2CDevice):
	def __init__(self, address = 0x70, allowMultiple = True, **kwargs):
		#Initialise I2CDevice
		I2CDevice.__init__(self, address, **kwargs)
		
		#Store attached devices and currently enabled
		self.__attachedDevices = {}
		self.__enabledLine = None
		self.write8(0,0) #Disable any already enabled devices


	def __deviceCallback(self, device):
		if not device in self.__attachedDevices:
			raise I2CExpection("Device %s was not properly detached from the TCA" % device)

		#Call own callback (for chained TCAs)
		if self.preAccess != None:
			self.preAccess(self) 

		#Skip if already enabled
		if self.__attachedDevices[device] == self.__enabledLine:
			return

		self.__enabledLine = self.__attachedDevices[device]

		#Update TCA Register
		self.write8(0, 1 << self.__attachedDevices[device])

	def attachDevice(self, line, device, *args, **kwargs):
		if callable(device):
			self.write8(0, 1 << line)
			device = device(*args, **kwargs)
			self.__enabledLine = line

		if not isinstance(device, I2CDevice) and not isinstance(device, I2CContainer):
			raise I2CException("The device %s must be a type or an instance of I2CDevice" % device)

		self.__attachedDevices[device] = line
		device.preAccess = self.__deviceCallback
		return device

	def removeDevice(self, device):
		if device in self.__attachedDevices:
			self.__attachedDevices.pop(device)
			device.preAccess = None
		else:
			#Device is not attached to this TCA
			raise I2CException("The device %s is not attached to this TCA" % device)

if __name__ == "__main__" and len(sys.argv) > 1:
	tca = TCA9548(0x70)
	tca.write8(0, int(sys.argv[1]))
