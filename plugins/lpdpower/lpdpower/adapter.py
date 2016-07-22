from odin.adapters.adapter import ApiAdapter, ApiAdapterResponse, request_types, response_types
from tornado.escape import json_decode
from tca9548 import TCA9548
from lm92 import LM92
from mcp23008 import MCP23008
from tca9548 import TCA9548
import Adafruit_GPIO as GPIO
from DataTree import DataTree

class LM92Handler(object):

	#Get the associated sensor and assign an ID
	def __init__(self, sensor):
		if isinstance(sensor, LM92):
			self.tempsensor = sensor
		else:
			self.tempsensor = LM92(sensor)

		self.dataTree = DataTree({
                        'temperature' : self.tempsensor.readTemperatureDegrees,
                        'flags' : {
                                'critical' : self.tempsensor.isCritical,
                                'high' : self.tempsensor.isHigh,
                                'low' : self.tempsensor.isLow
                        	},
			'enable' : self.tempsensor.isEnabled()})

		self.dataTree.addCallback('enable/', self.updateEnabled)
	
	def updateEnabled(self, path, val):
		self.tempsensor.enable(val)

	#Handles a GET request to the temp. sensor
	def handleGet(self, path):
		return self.dataTree.getData(path)

	#Handle a PUT request to the temp. sensor
	def handlePut(self, path, data):
		self.dataTree.setData(path, data)

class MCP23008Handler(object):

	#Get the associated MCP23008
	def __init__(self, device):
		if isinstance(device, MCP23008):
			self.device = device
		else:
			self.device = MCP23008(device)

		self.dataTree = DataTree({
			'outputs' : [False, False, False],
			'input' : self.__getPushButton})
		self.dataTree.addCallback('outputs/', self.updateOutputs)		

		self.device.setup(0, GPIO.OUT)
		self.device.setup(1, GPIO.OUT)
		self.device.setup(2, GPIO.OUT)
		self.device.setup(3, GPIO.IN)

	def __getPushButton(self):
		return self.device.input(3)

	def handlePut(self, path):
		self.dataTree.getData(path)

	def handleGet(self, path, data):
		self.dataTree.setData(path, data)

	def updateOutputs(self, path, val):
		pin = int(path[-2])
		print pin
		self.device.output(pin, val)		


class LPDPowerAdapter(ApiAdapter):

	def __init__(self, **kwargs):
		super(LPDPowerAdapter, self).__init__(**kwargs)

		tmp = LM92()
		mcp = MCP23008()

		#TCA setup
		self.tca = TCA9548()
		self.tca.attachDevice(mcp, 0)
		self.tca.attachDevice(tmp, 1)

		self.sensorHandler = LM92Handler(tmp)
		self.outputHandler = MCP23008Handler(mcp)
		self.dataTree = DataTree({'temp0' : self.sensorHandler.dataTree, 'output' : self.outputHandler.dataTree})

	@request_types('application/json')
	@response_types('application/json')
	def get(self, path, request):
		return ApiAdapterResponse(self.dataTree.getData(path))	

	@request_types('application/json')
        @response_types('application/json')
        def put(self, path, request):
		data = json_decode(request.body)
		self.dataTree.setData(path, data)
		return ApiAdapterResponse(self.dataTree.getData(path))  


