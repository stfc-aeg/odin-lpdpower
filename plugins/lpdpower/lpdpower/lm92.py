from I2CDevice import I2CDevice
import time

class LM92(I2CDevice):
	def __init__(self, address = 0x4b, **kwargs):
		I2CDevice.__init__(self, address, **kwargs)
		self.__stored = None
		self.__last_poll = -9999

	def __pollSensor(self):
		if time.time() - self.__last_poll > 0.5:
			self.__stored = self.readU16(0)
			self.__last_poll = time.time()
		
		return self.__stored

	def __reverse2Bytes(self, data):
		return ((data & 0xff) << 8) + ((data & 0xff00) >> 8)

	def __convertTemp(self, temp):
		var = int(temp / 0.0625)
		if var < 0:
			var += 8192
		return self.__reverse2Bytes(var << 3)
		

	def readTemperatureRaw(self):
		return self.__pollSensor()

	def readTemperatureDegrees(self):
		data = self.__reverse2Bytes(self.__pollSensor()) >> 3
		if data & 4096:
			data -= 8192
		return data * 0.0625

	def enable(self, value):
		config = self.readU8(1)
		if value:
			config &= ~1
		else:
			config |= 1
		self.write8(1, config)

	def isEnabled(self):
		return bool(~self.readU8(1) & 1)

	def setHysteresis(self, val):
		self.write16(2, self.__convertTemp(val))

	def setCritical(self, val):
		self.write16(3, self.__convertTemp(val))

	def setLowPoint(self, val):
                self.write16(4, self.__convertTemp(val))

	def setHighPoint(self, val):
                self.write16(5, self.__convertTemp(val))

	def isCritical(self):
		return bool(self.__reverse2Bytes(self.__pollSensor()) & 4)

	def isHigh(self):
                return bool(self.__reverse2Bytes(self.__pollSensor()) & 2)

	def isLow(self):
                return bool(self.__reverse2Bytes(self.__pollSensor()) & 1)



		
if __name__ == "__main__":
	temp = LM92(ADDRESS)
	temp.enable(True)
	temp.setCritical(33)
	temp.setHysteresis(2)
	temp.setLowPoint(24)
	temp.setHighPoint(29)
	while True:
		print "\n\n" + str(temp.readTemperatureDegrees())
		if temp.isCritical(): print "Critical"
		if temp.isHigh(): print "High"
		if temp.isLow(): print "Low"
		time.sleep(0.2)
