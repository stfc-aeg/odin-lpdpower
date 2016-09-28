import logging

from quad_data import QuadData
from parameter_tree import ParameterTree, ParameterTreeError
from pscu import PSCU


class TempData(object):
    """Data container for an individual temperature sensor."""

    def __init__(self, pscu, number):
        self.param_tree = ParameterTree({
            "setpoint": (self.getSetPoint, None),
            "temperature": (self.getTemp, None),
            "trace": (self.getTrace, None),
            "tripped": (self.getTripped, None),
            "disabled": (self.getDisabled, None),
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


class HumidityData(object):
    """Data container for an individual humidity sensor."""

    def __init__(self, pscu, number):
        self.param_tree = ParameterTree({
            "humidity": (self.getHumidity, None),
            "setpoint": (self.getSetPoint, None),
            "tripped": (self.getTripped, None),
            "trace": (self.getTrace, None),
            "disabled": (self.getDisabled, None),
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
        

class PSCUDataError(Exception):
    """Simple exception container to wrap lower-level exceptions."""

    pass


class PSCUData(object):
    """Data container for entire PSCU & Quads."""

    def __init__(self, *args, **kwargs):
#         if len(args) and isinstance(args[0], PSCU):
#             self.pscu = args[0]
#         else:
#             self.pscu = PSCU(*args, **kwargs)
        if 'pscu' in kwargs:
            self.pscu = kwargs['pscu']
        else:
            self.pscu = PSCU(*args, **kwargs)
        
        self.quadData = [QuadData(quad=q) for q in self.pscu.quad]
        
        self.tempData = [TempData(self.pscu, i) for i in range(11)]
        self.humidityData = [HumidityData(self.pscu, i) for i in range(2)]

        self.param_tree = ParameterTree({
            "quad": {
                "quads": [q.param_tree for q in self.quadData],
                'trace': (self.getQuadTraces, None),
            },
            "temperature": {
                "sensors": [t.param_tree for t in self.tempData],
                "overall": (self.pscu.getTempOutput,  None),
                "latched": (self.pscu.getTempLatched,  None),
            },
            "humidity": {
                "sensors": [h.param_tree for h in self.humidityData],
                "overall": (self.pscu.getHumidityOutput, None),
                "latched": (self.pscu.getHumidityLatched, None),
            },
            "fan": {
                "target": (self.pscu.getFanTarget, self.pscu.setFanTarget),
                "currentspeed": (self.pscu.getFanSpeed, None),
                "setpoint": (self.pscu.getFanSetPoint, None),
                "tripped": (self.pscu.getFanTripped, None),
                "overall": (self.pscu.getFanOutput, None),
                "latched": (self.pscu.getFanLatched, None),
            },
            "pump": {
                "flow": (self.pscu.getPumpFlow, None),
                "setpoint": (self.pscu.getPumpSetPoint, None),
                "tripped": (self.pscu.getPumpTripped, None),
                "overall": (self.pscu.getPumpOutput, None),
                "latched": (self.pscu.getPumpLatched, None),
            },
            "trace": {
                 "overall": (self.pscu.getTraceOutput, None),
                 "latched": (self.pscu.getTraceLatched,  None),
            },
            "position": (self.pscu.getPosition, None),
            "overall": (self.pscu.getHealth,  None),
            "latched": (self.getAllLatched, None),
            "armed": (self.pscu.getArmed, self.pscu.setArmed),
            "allEnabled": (self.pscu.getAllEnabled, self.pscu.enableAll),
            "enableInterval": (self.pscu.getEnableInterval, None),
            "displayError": (self.pscu.getDisplayError, None),
        })

    def get(self, path):
        """Get parameters from the underlying parameter tree.

        This method simply wraps underlying ParameterTree method so that an exceptions can be
        re-raised with an appropriate PSCUDataError.
        """
        try:
            return self.param_tree.get(path)
        except ParameterTreeError as e:
            raise PSCUDataError(e)

    def set(self, path, data):
        """Set parameters in underlying parameter tree.

        This method simply wraps underlying ParameterTree method so that an exceptions can be
        re-raised with an appropriate PSCUDataError.
        """
        try:
            self.param_tree.set(path, data)
        except ParameterTreeError as e:
            raise PSCUDataError(e)

    def getAllLatched(self):
        
        return all(self.pscu.getAllLatched())
    
    def getQuadTraces(self):
        return {str(q) : self.pscu.getQuadTrace(q) for q in range(self.pscu.numQuads)}
         