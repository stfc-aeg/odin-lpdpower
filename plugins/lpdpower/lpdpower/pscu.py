from I2CContainer import I2CContainer
from tca9548 import TCA9548
from ad7998 import AD7998
from ad5321 import AD5321
from mcp23008 import MCP23008
from quad import Quad
from usblcd import UsbLcd
import Adafruit_BBIO.GPIO as GPIO

import logging

#PSCU consisting of 4x Quads & Other sensors
class PSCU(I2CContainer):
	ALL_PINS = [0,1,2,3,4,5,6,7]

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
		
		#Temperature monitor MCP23008s
		self.mcpTempMon = []
		self.mcpTempMon.append(self.tca.attachDevice(4, MCP23008, 0x24))
		for i in range(8):
			self.mcpTempMon[0].setup(i, MCP23008.IN if i < 7 else MCP23008.IN)
		
		self.mcpTempMon.append(self.tca.attachDevice(4, MCP23008, 0x25))
		for i in range(8):
			self.mcpTempMon[1].setup(i, MCP23008.IN)
		
		self.mcpTempMon.append(self.tca.attachDevice(4, MCP23008, 0x26))
		for i in range(8):
                        self.mcpTempMon[2].setup(i, MCP23008.IN)
		
		self.mcpTempMon.append(self.tca.attachDevice(4, MCP23008, 0x27))
		for i in range(8):
                        self.mcpTempMon[3].setup(i, MCP23008.IN)
		
		#Attach bus 5 devices
		#Misc AD7998s
		self.adcMisc = []
		self.adcMisc.append(self.tca.attachDevice(5, AD7998, 0x21))
		self.adcMisc.append(self.tca.attachDevice(5, AD7998, 0x22))

		#Misc MCP23008s
		self.mcpMisc = []
		self.mcpMisc.append(self.tca.attachDevice(5, MCP23008, 0x24))
		for i in range(8):
			self.mcpMisc[0].setup(i, MCP23008.OUT if i < 2 else MCP23008.IN)
		self.mcpMisc.append(self.tca.attachDevice(5, MCP23008, 0x25))
		for i in range(8):
			self.mcpMisc[1].setup(i, MCP23008.IN)
		self.mcpMisc.append(self.tca.attachDevice(5, MCP23008, 0x26))
		for i in range(8):
			self.mcpMisc[2].setup(i, MCP23008.IN)
		self.mcpMisc.append(self.tca.attachDevice(5, MCP23008, 0x27))
		for i in range(8):
			self.mcpMisc[3].setup(i, MCP23008.IN)

		#Fan speed AD5321
                self.fanSpd = self.tca.attachDevice(5, AD5321, 0x0c)
		
                #Buffers for all I2C sensors
		#Temperature
                self.__tempValues = [0,0,0,0,0,0,0,0,0,0,0]
                self.__tempSetPoints = [0,0,0,0,0,0,0,0,0,0,0]
                self.__tempTrips = [0,0,0,0,0,0,0,0,0,0,0]
                self.__tempTraces = [0,0,0,0,0,0,0,0,0,0,0]
		self.__tempDisabled = [0,0,0,0,0,0,0,0,0,0,0]

		#Humidity
                self.__hValues = [0,0]
		self.__hSetPoints = [0,0]
		self.__hTrips = [0,0]
		self.__hTraces = [0,0]
		self.__hDisabled = [0,0]

		#Pump
		self.__pumpFlow = 0
		self.__pumpSetPoint = 0
		self.__pumpTrip = False

		#Fan
		self.__fanSpeed = 0
		self.__fanSetPoint = 0
		self.__fanPot = 0
		self.__fanTrip = False

		#Quad traces
		self.__qTraces = [0,0,0,0]

		#Overall
		self.__armed = False
		self.__healthy = False
		self.__sensorOutputs = [0,0,0,0,0] #Tmp, F, P, H, T
		self.__latchedOutputs = [0,0,0,0,0] #Tmp, F, P, T, H

                #LCD Display
                self.lcd = UsbLcd("/dev/ttyACM0", 57600, rows=4, cols=20)
                self.lcdScreen = 0
                self.lcdScreenCount = 5
		self.__lcdBuff = ""
		self.__lcdColor = 0
                GPIO.setup("P9_11", GPIO.IN)
                GPIO.setup("P9_12", GPIO.IN)
                GPIO.add_event_detect("P9_11", GPIO.RISING)
                GPIO.add_event_detect("P9_12", GPIO.RISING)

        def getTemperature(self, sensor):
                if sensor > 10 or sensor < 0:
                        raise I2CException("There is not sensor %s" % sensor)

		return self.__tempValues[sensor]

        def getTempSetPoint(self, sensor):
                if sensor > 10 or sensor < 0:
                        raise I2CException("There is not sensor %s" % sensor)

                return self.__tempSetPoints[sensor]

        def getTempTripped(self, sensor):
                if sensor > 10 or sensor < 0:
                        raise I2CException("There is not sensor %s" % sensor)

                return self.__tempTrips[sensor]

	def getTempTrace(self, sensor):
		if sensor > 10 or sensor < 0:
                        raise I2CException("There is not sensor %s" % sensor)

                return self.__tempTraces[sensor]

	def getTempDisabled(self, sensor):
		if sensor > 10 or sensor < 0:
                        raise I2CException("There is not sensor %s" % sensor)

                return self.__tempDisabled[sensor]
	
	def getHumidity(self, sensor):
		if sensor > 1 or sensor < 0:
                        raise I2CException("There is not sensor %s" % sensor)

                return self.__hValues[sensor]

	def getHSetPoint(self, sensor):
                if sensor > 1 or sensor < 0:
                        raise I2CException("There is not sensor %s" % sensor)

                return self.__hSetPoints[sensor]

	def getHTripped(self, sensor):
                if sensor > 1 or sensor < 0:
                        raise I2CException("There is not sensor %s" % sensor)

                return self.__hTrips[sensor]

	def getHTrace(self, sensor):
                if sensor > 1 or sensor < 0:
                        raise I2CException("There is not sensor %s" % sensor)

                return self.__hTraces[sensor]

	def getHDisabled(self, sensor):
                if sensor > 1 or sensor < 0:
                        raise I2CException("There is not sensor %s" % sensor)

                return self.__hDisabled[sensor]

	def getPumpFlow(self):
		return self.__pumpFlow
	
	def getPumpSetPoint(self):
		return self.__pumpSetPoint

	def getPumpTripped(self):
		return self.__pumpTrip

	def getFanSpeed(self):
		return self.__fanSpeed
	
	def getFanSetPoint(self):
		return self.__fanSetPoint

	def getFanPot(self):
		return self.__fanPot

	def getFanTripped(self):
		return self.__fanTrip

	def getQuadTrace(self, q):
		if q > 3 or q < 0:
                        raise I2CException("There is no quad %s" % q)

                return self.__qTraces[q]

	def getArmed(self):
		return self.__armed

	def getHealth(self):
		return self.__healthy

	def getTempOutput(self):
		return self.__sensorOutputs[0]

	def getTraceOutput(self):
                return self.__sensorOutputs[4]


	def getFanOutput(self):
                return self.__sensorOutputs[1]

	def getPumpOutput(self):
                return self.__sensorOutputs[2]

	def getHumidityOutput(self):
                return self.__sensorOutputs[3]

	def enableAll(self):
		pass #Enable quads in turn

	def setArmed(self, value):
		pin = 0 if value else 1
		self.mcpMisc[0].output(pin, MCP23008.LOW)
		self.mcpMisc[0].output(pin, MCP23008.HIGH)
		self.mcpMisc[0].output(pin, MCP23008.LOW)

	def setFanSpeed(self, value):
		self.fanSpd.setOutput01(1.0 - (value / 100.0))

	def updateLCD(self):
		#Get input
		if GPIO.event_detected("P9_11"):
			self.lcdScreen += 1
		elif GPIO.event_detected("P9_12"):
			self.lcdScreen -= 1

		self.lcdScreen %= self.lcdScreenCount

		if self.__healthy:
			col = UsbLcd.GREEN
		else:
			col = UsbLcd.RED
		
		if not col ==	self.__lcdColor:
			self.lcd.set_backlight_colour(col)
			self.__lcdColor = col

		#Redraw screen
		if self.lcdScreen == 0:
			if self.__armed:
				newDisplay = "Interlock System:\rArmed"
			else:
				newDisplay = "Interlock System:\rDisarmed"

		elif self.lcdScreen == 1:
			newDisplay = "Channel 0A: " + ("Enabled " if self.quad[0].isEnabled(0) else "Disabled") \
					+ "Channel 0B: " + ("Enabled " if self.quad[0].isEnabled(1) else "Disabled") \
					+ "Channel 0C: " + ("Enabled " if self.quad[0].isEnabled(2) else "Disabled") \
					+ "Channel 0D: " + ("Enabled " if self.quad[0].isEnabled(3) else "Disabled")

		elif self.lcdScreen == 2:
                        newDisplay = "Channel 1A: " + ("Enabled " if self.quad[1].isEnabled(0) else "Disabled") \
                        		 + "Channel 1B: " + ("Enabled " if self.quad[1].isEnabled(1) else "Disabled") \
                        		 + "Channel 1C: " + ("Enabled " if self.quad[1].isEnabled(2) else "Disabled") \
                        		 + "Channel 1D: " + ("Enabled " if self.quad[1].isEnabled(3) else "Disabled")

		elif self.lcdScreen == 3:
                        newDisplay = "Channel 2A: " + ("Enabled " if self.quad[2].isEnabled(0) else "Disabled") \
                        		 + "Channel 2B: " + ("Enabled " if self.quad[2].isEnabled(1) else "Disabled") \
                        		 + "Channel 2C: " + ("Enabled " if self.quad[2].isEnabled(2) else "Disabled") \
                        		 + "Channel 2D: " + ("Enabled " if self.quad[2].isEnabled(3) else "Disabled")

		elif self.lcdScreen == 4:
                        newDisplay = "Channel 3A: " + ("Enabled " if self.quad[3].isEnabled(0) else "Disabled") \
                        		 + "Channel 3B: " + ("Enabled " if self.quad[3].isEnabled(1) else "Disabled") \
                        		 + "Channel 3C: " + ("Enabled " if self.quad[3].isEnabled(2) else "Disabled") \
                        		 + "Channel 3D: " + ("Enabled " if self.quad[3].isEnabled(3) else "Disabled")

		if newDisplay != self.__lcdBuff:
			self.__lcdBuff = newDisplay
			self.lcd.clear()
			self.lcd.write(self.__lcdBuff)

	def convert_ad7998_temp(self, fs_val):

		temp_vref = 3.0
		temp_scale_v_kelvin = 0.005
		temp_val = ((fs_val * temp_vref) / temp_scale_v_kelvin) - 273.15

		return temp_val

	def pollAllSensors(self):
		
		#Temperature ADCs
		for i in range(8):
			adc_input_fs = self.adcTempMon[0].readInput01(i)
			set_point    = self.convert_ad7998_temp(adc_input_fs)
			#logging.debug("pollAllSensors %d %f %f %f " %( i, adc_input_fs, adc_input_fs*4095, set_point))
			self.__tempSetPoints[i] = set_point # self.convert_ad7998_temp(self.adcTempMon[0].readInput01(i))

		for i in range(8):
			self.__tempValues[i] = self.convert_ad7998_temp(self.adcTempMon[1].readInput01(i))

		for i in range(3):
			self.__tempValues[i + 8] = self.convert_ad7998_temp(self.adcTempMon[2].readInput01(i))

		for i in range(4, 7):
			self.__tempSetPoints[i + 4] = self.convert_ad7998_temp(self.adcTempMon[2].readInput01(i))
		
		
		#Temperature MCPs
		buff = self.mcpTempMon[0].input_pins([0,1,2,3,4,5,7])
		for i in range(4):
			self.__tempDisabled[i + 4] = buff[i]
		self.__tempDisabled[10] = buff[4]
		self.__hDisabled[1] = buff[5]
		self.__sensorOutputs[0] = buff[6]

		buff = self.mcpTempMon[1].input_pins(self.ALL_PINS)
		for i in range(8):
			self.__tempTrips[i] = not bool(buff[i])
		
		buff = self.mcpTempMon[2].input_pins(self.ALL_PINS)
		for i in range(8):
			self.__tempTraces[i] = bool(buff[i])
		
		buff = self.mcpTempMon[3].input_pins([0,1,2,3,4,5])
		for i in range(3):
			self.__tempTrips[i + 8] = not bool(buff[i])
		for i in range(3, 6):
			self.__tempTraces[i + 5] = bool(buff[i])
		
		#Misc. ADCs
		self.__fanSpeed = self.adcMisc[1].readInput01(0) * 5 / 4.5 * 50
		self.__hValues[0] = self.adcMisc[1].readInput01(1) * 100 * 5 / 3.9
		self.__hValues[1] = self.adcMisc[1].readInput01(2) * 100 * 5 / 3.9
		self.__pumpFlow = self.adcMisc[1].readInput01(3) * 5 / 4.32 * 35
		self.__fanPot = self.adcMisc[1].readInput01(4) * 100

		self.__fanSetPoint = self.adcMisc[0].readInput01(0) * 5 / 4.5 * 50
		self.__hSetPoints[0] = self.adcMisc[0].readInput01(1) * 100 * 5 / 3.9
		self.__hSetPoints[1] = self.adcMisc[0].readInput01(2) * 100 * 5 / 3.9
		self.__pumpSetPoint = self.adcMisc[0].readInput01(3) * 5 / 4.32 * 35

		#Misc. MCPs
		buff = self.mcpMisc[0].input_pins([2,3,4,5,6,7])
		self.__armed = bool(buff[0])
		for i in range(1, 5):
			self.__sensorOutputs[i] = bool(buff[i])
		self.__healthy = bool(buff[5])

		buff = self.mcpMisc[1].input_pins([0,1,2,3])
		self.__fanTrip = not bool(buff[0])
		self.__hTrips[0] = not bool(buff[1])
		self.__hTrips[1] = not bool(buff[2])
		self.__pumpTrip = not bool(buff[3])

		buff = self.mcpMisc[2].input_pins([1,2,4,5,6,7])
		self.__hTraces[0] = bool(buff[0])
		self.__hTraces[1] = bool(buff[1])
		for i in range(2, 6):
			self.__qTraces[i - 2] = bool(buff[i])

		buff = self.mcpMisc[3].input_pins([0,1,2,3,4])
		self.__latchedOutputs[i] = [bool(i) for i in buff]
