from quad_data import QuadData
from DataTree import DataTree
from pscu import PSCU
from quad import Quad
from tca9548 import TCA9548

#Dummy class
#class PSCU(object):
#	def __init__(self):
#		self.tca = TCA9548(0x70)
#		quad = self.tca.attachDevice(5, Quad)
#		self.quads = [quad] * 4

#Data container for an individual temp sensor
class TempData(object):
	def __init__(self, pscu, number):
		self.dataTree = DataTree({
			"setpoint" : self.getSetPoint,
			"temperature" : self.getTemp,
			"trace" : self.getTrace,
			"tripped" : self.getTripped,
			"disabled" : self.getDisabled
		})

		self.pscu = pscu
		self.number = number

	def getSetPoint(self):
		return self.pscu.getTempSetPoint(self.number)

	def getTemp(self):
		return self.pscu.getTemperature(self.number)

	def getTrace(self):
		return self.pscu.getTempTrace(self.number)

	def getTripped(self):
		return self.pscu.getTempTripped(self.number)

	def getDisabled(self):
		return self.pscu.getTempDisabled(self.number)

#Data container for an individual humidity sensor
class HumidityData(object):
	def __init__(self, pscu, number):
		self.dataTree = DataTree({
			"humidity" : self.getHumidity,
			"setpoint" : self.getSetPoint,
			"tripped" : self.getTripped,
			"trace" : self.getTrace,
			"disabled" : self.getDisabled,
		})

		self.pscu = pscu
		self.number = number

	def getHumidity(self):
		return self.pscu.getHumidity(self.number)

	def getSetPoint(self):
                return self.pscu.getHSetPoint(self.number)

	def getTripped(self):
                return self.pscu.getHTripped(self.number)

	def getTrace(self):
                return self.pscu.getHTrace(self.number)

	def getDisabled(self):
		return self.pscu.getHDisabled(self.number)

#Data container for entire PSCU & Quads
class PSCUData(object):
	def __init__(self, *args, **kwargs):
		if len(args) and isinstance(args[0], PSCU):
			self.pscu = args[0]
		else:
			self.pscu = PSCU(*args, **kwargs)

		self.quadData = [QuadData(q) for q in self.pscu.quad]
		self.tempData = [TempData(self.pscu, i) for i in range(11)]
		self.humidityData = [HumidityData(self.pscu, i) for i in range(2)]

		self.dataTree = DataTree({
			"quad" : {
				"quads" : [q.dataTree for q in self.quadData],
				"trace" : [self.traceQ0, self.traceQ1, self.traceQ2, self.traceQ3]
			},
			"temperature" : {
				"sensors" : [t.dataTree for t in self.tempData],
				"overall" : self.pscu.getTempOutput,
				"latched" : self.pscu.getTempLatched,
			},
			"humidity" : {
				"sensors" : [h.dataTree for h in self.humidityData],
				"overall" : self.pscu.getHumidityOutput,
				"latched" : self.pscu.getHumidityLatched,
			},
			"fan" : {
				"target" : 0,
				"currentspeed" : self.pscu.getFanSpeed,
				"setpoint" : self.pscu.getFanSetPoint,
				"potentiometer" : self.pscu.getFanPot,
				"tripped" : self.pscu.getFanTripped,
				"overall" : self.pscu.getFanOutput,
				"latched" : self.pscu.getFanLatched,
			},
			"pump" : {
				"flow" : self.pscu.getPumpFlow,	
				"setpoint" : self.pscu.getPumpSetPoint,
				"tripped" : self.pscu.getPumpTripped,
				"overall" : self.pscu.getPumpOutput,
				"latched" : self.pscu.getPumpLatched,
			},
			"trace" : {
				 "overall" : self.pscu.getTraceOutput,
				 "latched" : self.pscu.getTraceLatched,
                        },
			"overall": self.pscu.getHealth,
			"arm" : True, #Output
			"isarmed" : self.pscu.getArmed,
			"enableall" : False #Output
		})

		self.dataTree.addCallback("enableall/", self.enableAll)
		self.dataTree.addCallback("arm/", self.setArmed)
		self.dataTree.addCallback("fan/target/", self.fanTarget)

	def enableAll(self, path, value):
		self.pscu.enableAll()

	def setArmed(self, path, value):
		self.pscu.setArmed(value)

	def fanTarget(self, path, value):
		self.pscu.setFanSpeed(value)

	def traceQ0(self):
		return self.pscu.getQuadTrace(0)

	def traceQ1(self):
                return self.pscu.getQuadTrace(1)

	def traceQ2(self):
                return self.pscu.getQuadTrace(2)

	def traceQ3(self):
                return self.pscu.getQuadTrace(3)

