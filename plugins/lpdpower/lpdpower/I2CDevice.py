from Adafruit_I2C import Adafruit_I2C

#Exception to be used for I2C issues
class I2CException(Exception):
	pass

#Provides several callbacks to help when connecting devices to I2C expanders
class I2CDevice(Adafruit_I2C):
	def __init__(self, *args, **kwargs):
		Adafruit_I2C.__init__(self, *args, **kwargs)
		self.preRead = None
		self.postRead = None
		self.preWrite = None
		self.postWrite = None

	def write8(self, *args):
		if not self.preWrite == None: self.preWrite(self)
 		ret = Adafruit_I2C.write8(self, *args)
		if not self.postWrite == None: self.postWrite(self)
		return ret

	def write16(self, *args):
                if not self.preWrite == None: self.preWrite(self)
                ret = Adafruit_I2C.write16(self, *args)
                if not self.postWrite == None: self.postWrite(self)
                return ret

	def writeRaw8(self, *args):
                if not self.preWrite == None: self.preWrite(self)
                ret = Adafruit_I2C.writeRaw8(self, *args)
                if not self.postWrite == None: self.postWrite(self)
                return ret

	def writeList(self, *args):
                if not self.preWrite == None: self.preWrite(self)
                ret = Adafruit_I2C.writeList(self, *args)
                if not self.postWrite == None: self.postWrite(self)
                return ret

	def readList(self, *args):
                if not self.preRead == None: self.preRead(self)
                ret = Adafruit_I2C.readList(self, *args)
                if not self.postRead == None: self.postRead(self)
                return ret

	def readU8(self, *args):
                if not self.preRead == None: self.preRead(self)
                ret = Adafruit_I2C.readU8(self, *args)
                if not self.postRead == None: self.postRead(self)
                return ret

	def readS8(self, *args):
                if not self.preRead == None: self.preRead(self)
                ret = Adafruit_I2C.readS8(self, *args)
                if not self.postRead == None: self.postRead(self)
                return ret

	def readU16(self, *args):
                if not self.preRead == None: self.preRead(self)
                ret = Adafruit_I2C.readU16(self, *args)
                if not self.postRead == None: self.postRead(self)
                return ret

	def readS16(self, *args):
                if not self.preRead == None: self.preRead(self)
                ret = Adafruit_I2C.readS16(*args)
                if not self.postRead == None: self.postRead(self)
                return ret

