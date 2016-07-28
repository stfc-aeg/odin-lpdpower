from odin.adapters.adapter import ApiAdapter, ApiAdapterResponse, request_types, response_types
from tornado.escape import json_decode
from concurrent import futures
from tornado.ioloop import IOLoop
from tornado.concurrent import run_on_executor
from tca9548 import TCA9548
from quad import Quad
from mcp23008 import MCP23008
from lm92 import LM92
from tca9548 import TCA9548
import Adafruit_GPIO as GPIO
from DataTree import DataTree
#from test_data import *
#from quad_data import QuadData
from pscu_data import PSCUData
import time

class LPDPowerAdapter(ApiAdapter):

	# Thread executor used for background tasks
	executor = futures.ThreadPoolExecutor(max_workers=1)

	def __init__(self, **kwargs):
		super(LPDPowerAdapter, self).__init__(**kwargs)

		#self.tca = TCA9548()

		#tmp = self.tca.attachDevice(1, LM92)
		#tmp.setHysteresis(0.5)
		#tmp.setLowPoint(24.0)
		#tmp.setHighPoint(29.0)
		#tmp.setCritical(31.0)

		#mcp = self.tca.attachDevice(0, MCP23008)

		#quad = self.tca.attachDevice(5, Quad)

		#self.sensorData = LM92Data(tmp)
		#self.outputData = MCP23008Data(mcp)
		#self.quadData = QuadData(quad)

		self.pscuData = PSCUData()

		self.update_interval = self.options.get('update_interval', 0.05)
		self.update_loop()

	@request_types('application/json')
	@response_types('application/json')
	def get(self, path, request):
		return ApiAdapterResponse(self.pscuData.dataTree.getData(path))	

	@request_types('application/json')
        @response_types('application/json')
        def put(self, path, request):
		data = json_decode(request.body)
		self.pscuData.dataTree.setData(path, data)
		return ApiAdapterResponse(self.pscuData.dataTree.getData(path))  

	#@run_on_executor
	def update_loop(self):	
		self.pscuData.pscu.updateLCD()
		self.pscuData.pscu.pollAllSensors()
		time.sleep(self.update_interval)
		IOLoop.instance().add_callback(self.update_loop)
