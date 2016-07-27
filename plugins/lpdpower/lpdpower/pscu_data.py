from quad_data import QuadData
from DataTree import DataTree
#from pscu import PSCU
from quad import Quad
from tca9548 import TCA9548

#Dummy class
class PSCU(object):
	def __init__(self):
		self.tca = TCA9548(0x70)
		quad = self.tca.attachDevice(5, Quad)
		self.quads = [quad] * 4

#Data container for an individual temp sensor
class TempData(object):
	def __init__(self, pscu, number):
		self.dataTree = DataTree({
			"setpoint" : 0,
			"temperature" : 0,
			"trace" : True, #Output
			"tripped" : False,
			"disable" : False, #Output
		})

#Data container for an individual humidity sensor
class HumidityData(object):
	def __init__(self, pscu, number):
		self.dataTree = DataTree({
			"humidity" : 0,
			"setpoint" : 0,
			"tripped" : False,
			"trace" : True, #Output
			"disable" : False #Output
		})

#Data container for entire PSCU & Quads
class PSCUData(object):
	def __init__(self, *args, **kwargs):
		if len(args) and isinstance(args[0], PSCU):
			self.pscu = args[0]
		else:
			self.pscu = PSCU(*args, **kwargs)

		self.quadData = [QuadData(q) for q in self.pscu.quads]
		self.tempData = [TempData(self.pscu, i) for i in range(11)]
		self.humidityData = [HumidityData(self.pscu, i) for i in range(2)]

		self.dataTree = DataTree({
			"quad" : {
				"quads" : [q.dataTree for q in self.quadData],
				"trace" : [True, True, True, True]
			},
			"temperature" : {
				"sensors" : [t.dataTree for t in self.tempData],
				"overall" : True
			},
			"humidity" : {
				"sensors" : [h.dataTree for h in self.humidityData],
				"overall" : True
			},
			"fan" : {
				"target" : 0,
				"currentspeed" : 0,
				"setpoint" : 0,
				"potentiometer" : 0,
				"tripped" : False,
				"overall" : True
			},
			"pump" : {
				"flow" : 0,	
				"setpoint" : 0,
				"tripped" : False,
				"overall" : True
			},
			"trace" : True,
			"overall": True,
			"arm" : True, #Output
			"isarmed" : True,
			"enableall" : False
		})

		self.dataTree.addCallback("enableall/", self.enableAll)

	def enableAll(self):
		self.pscu.enableAll()
