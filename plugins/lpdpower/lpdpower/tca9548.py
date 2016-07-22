from I2CDevice import I2CDevice, I2CException

#Handles enabling/disabling I2C devices connected to a TCA9548
class TCA9548(I2CDevice):
	def __init__(self, address = 0x70, allowMultiple = True, **kwargs):
		#Initialise I2CDevice
		I2CDevice.__init__(self, address, **kwargs)

		#Store attached devices and currently enabled
		self.__attachedDevices = {}
		self.__enabledAddresses = {}
		self.__buff = 0
		self.write8(0,0) #Disable any already enabled devices

	def __deviceCallback(self, device):
		#Skip if already enabled
		if device.address in self.__enabledAddresses \
		and self.__enabledAddresses[device.address] == device:
			return

		if device in self.__attachedDevices:

			self.__enabledAddresses.clear()
			self.__buff = 0

			#Add device
			self.__buff |= 1 << self.__attachedDevices[device]
			self.__enabledAddresses[device.address] = device

			#Update TCA IC
			self.write8(0, self.__buff)

		else:
			raise I2CExpection("%s was not properly detached from the TCA" % device)	

	def attachDevice(self, line, device, *args, **kwargs):
		if callable(device):
			self.write8(0, 1 << line)
			device = device(*args, **kwargs)
			self.write8(0, self.__buff)

		if not isinstance(device, I2CDevice):
			raise I2CException("The device %s must be a type or an instance of I2CDevice" % device)

		self.__attachedDevices[device] = line
		device.preRead = self.__deviceCallback
		device.preWrite = self.__deviceCallback

		return device

	def removeDevice(self, device):
		if device in self.__attachedDevices:
			self.__attachedDevices.pop(device)
			device.preRead = None
			device.preWrite = None
		else:
			#Device is not attached to this TCA
			raise I2CException("The device %s is not attached to this TCA" % device)
