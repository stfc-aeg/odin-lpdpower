from quad import Quad
from DataTree import DataTree

#Data tree to represent one channel on a quad
class ChannelData(object):
	def __init__(self, quad, channel):
		self.quad = quad
		self.channel = channel

		self.dataTree = DataTree({
			"voltage" : self.getVoltage,
			"fusevoltage" : 0, #Placeholder
			"current" : self.getCurrent,
#			"fusevoltage" : self.getFuse,
			"feedback" : self.isEnabled,
			"enable" : self.quad.isEnabled(channel)
			})

		self.dataTree.addCallback("enable/", self.setChannel)

	def getVoltage(self):
		return self.quad.getChannelVoltage(self.channel)

#	def getFuse(self):
#		return self.quad.getFuseVoltage(self.channel)

	def getCurrent(self):
		return self.quad.getChannelCurrent(self.channel)

	def isEnabled(self):
		return self.quad.isEnabled(self.channel)

	def setChannel(self, path, val):
		self.quad.setChannel(self.channel, val)

#Data tree to represent an entire quad
class QuadData(object):
	def __init__(self, *args, **kwargs):
		if len(args) and isinstance(args[0], Quad):
			self.quad = args[0]
		else:
			self.quad = Quad(*args, **kwargs)

		self.channels = [ChannelData(self.quad, i) for i in range(4)]

		self.dataTree = DataTree({
			"channels" : [
				self.channels[0].dataTree,
				self.channels[1].dataTree,
				self.channels[2].dataTree,
				self.channels[3].dataTree
				],
			"supply" : 0
			})
