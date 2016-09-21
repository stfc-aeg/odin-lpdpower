from i2c_device import I2CDevice, I2CException

#Represents a class containing multiple I2CDevice classes
class I2CContainer(object):
	def __init__(self):
		self.__attachedDevices = []
		self.pre_access = None

	#Add a device to this I2CContainer
	def attachDevice(self, device, *args, **kwargs):
		if callable(device):
			if self.pre_access != None:
				self.pre_access(self)
			self.__attachedDevices.append(device(*args, **kwargs))
		elif isinstance(device, I2CDevice) or isinstance(device, I2CContainer):
			self.__attachedDevices.append(device)
		else:
			raise I2CException("I2CContainer::attachDevice expects a device of type I2CDevice or I2CContainer")

		#Attach device callback
		self.__attachedDevices[-1].pre_access = self.__deviceCallback
		return self.__attachedDevices[-1]

	#Pass through callbacks from child devices
	def __deviceCallback(self, device):
		if self.pre_access != None:
			self.pre_access(self)

	def removeDevice(self, device):
		if device in self.__attachedDevices:
			self.__attachedDevices.remove(device)
			device.pre_access = None
		else:
			raise I2CException("%d was not attached to this I2CContainer" % device)
