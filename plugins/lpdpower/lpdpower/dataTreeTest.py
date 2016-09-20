from DataTree import DataTree
import Adafruit_GPIO as GPIO
from lm92 import LM92
from mcp23008 import MCP23008

class LM92Data(object):

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

class MCP23008Data(object):

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

        def updateOutputs(self, path, val):
                pin = int(path[-2])
                self.device.output(pin, val)

