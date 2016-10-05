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
        return self.pscu.get_temp_set_point(self.number)

    def getTemp(self):
        return self.pscu.get_temperature(self.number)

    def getTrace(self):
        return self.pscu.get_temp_trace(self.number)

    def getTripped(self):
        return self.pscu.get_temp_tripped(self.number)

    def getDisabled(self):
        return self.pscu.get_temp_disabled(self.number)


class HumidityData(object):
    """Data container for an individual humidity sensor."""

    def __init__(self, pscu, number):
        self.param_tree = ParameterTree({
            "humidity": (self.get_humidity, None),
            "setpoint": (self.getSetPoint, None),
            "tripped": (self.getTripped, None),
            "trace": (self.getTrace, None),
            "disabled": (self.getDisabled, None),
        })

        self.pscu = pscu
        self.number = number

    def get_humidity(self):
        return self.pscu.get_humidity(self.number)

    def getSetPoint(self):
        return self.pscu.get_humidity_set_point(self.number)

    def getTripped(self):
        return self.pscu.get_humidity_tripped(self.number)

    def getTrace(self):
        return self.pscu.get_humidity_trace(self.number)

    def getDisabled(self):
        return self.pscu.get_humidity_disabled(self.number)
        

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
                "overall": (self.pscu.get_temp_output,  None),
                "latched": (self.pscu.get_temp_latched,  None),
            },
            "humidity": {
                "sensors": [h.param_tree for h in self.humidityData],
                "overall": (self.pscu.get_humidity_output, None),
                "latched": (self.pscu.get_humidity_latched, None),
            },
            "fan": {
                "target": (self.pscu.get_fan_target, self.pscu.set_fan_target),
                "currentspeed": (self.pscu.get_fan_speed, None),
                "setpoint": (self.pscu.get_fan_set_point, None),
                "tripped": (self.pscu.get_fan_tripped, None),
                "overall": (self.pscu.get_fan_output, None),
                "latched": (self.pscu.get_fan_latched, None),
            },
            "pump": {
                "flow": (self.pscu.get_pump_flow, None),
                "setpoint": (self.pscu.get_pump_set_point, None),
                "tripped": (self.pscu.get_pump_tripped, None),
                "overall": (self.pscu.get_pump_output, None),
                "latched": (self.pscu.get_pump_latched, None),
            },
            "trace": {
                 "overall": (self.pscu.getTraceOutput, None),
                 "latched": (self.pscu.getTraceLatched,  None),
            },
            "position": (self.pscu.get_position, None),
            "overall": (self.pscu.get_health,  None),
            "latched": (self.get_all_latched, None),
            "armed": (self.pscu.get_armed, self.pscu.set_armed),
            "allEnabled": (self.pscu.get_all_enabled, self.pscu.enable_all),
            "enableInterval": (self.pscu.get_enable_interval, None),
            "displayError": (self.pscu.get_display_error, None),
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

    def get_all_latched(self):
        
        return all(self.pscu.get_all_latched())
    
    def getQuadTraces(self):
        return {str(q) : self.pscu.get_quad_trace(q) for q in range(self.pscu.numQuads)}
         