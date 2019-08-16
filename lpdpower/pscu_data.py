"""pscu_data - PSCU data container classes.

This module implements PSCUData and associated classes needed to represent the
parameter data from the LPD power supply control unit. PSCUData acts as a bridge
between the API adapter and the underlying PSCU object instance. Other classes
provide data containers for sensors on the PSCU, such as temperature and humidity.

James Hogge, STFC Application Engineering Group.
"""
from odin.adapters.parameter_tree import ParameterTree, ParameterTreeError
from lpdpower.temp_data import TempData
from lpdpower.humidity_data import HumidityData
from lpdpower.quad_data import QuadData
from lpdpower.pscu import PSCU

class PSCUDataError(Exception):
    """Simple exception class for PSCUData to wrap lower-level exceptions."""

    pass


class PSCUData(object):
    """Data container for a PSCU and associated quads.

    This class implements a data container and parameter tree of a PSCU,
    its assocated quad boxes and all sensors contained therein. A PSCUData
    object, asociated with a PSCU instance, forms the primary interface between,
    and data model for, the adapter and the underlying devices.
    """

    def __init__(self, *args, **kwargs):
        """Initialise the PSCUData instance.

        This constructor initialises the PSCUData instance. If an existing PSCU instance
        is passed in as a keyword argument, that is used for accessing data, otherwise
        a new instance is created.

        :param args: positional arguments to be passed if creating a new PSCU
        :param kwargs: keyword arguments to be passed if creating a new PSCU, or if
        a pscu key is present, that is used as an existing PSCU object instance
        """
        # If a PSCU has been passed in keyword arguments use that, otherwise create a new one
        if 'pscu' in kwargs:
            self.pscu = kwargs['pscu']
        else:
            self.pscu = PSCU(*args, **kwargs)

        # Get the QuadData containers associated with the PSCU
        self.quad_data = [QuadData(quad=q) for q in self.pscu.quad]

        # Get the temperature and humidity containers associated with the PSCU
        self.temperature_data = [
            TempData(self.pscu, i) for i in range(self.pscu.num_temperatures)
        ]
        self.humidity_data = [
            HumidityData(self.pscu, i) for i in range(self.pscu.num_humidities)
        ]

        # Build the parameter tree of the PSCU
        self.param_tree = ParameterTree({
            "quad": {
                "quads": [q.param_tree for q in self.quad_data],
                'trace': (self.get_quad_traces, None),
            },
            "temperature": {
                "sensors": [t.param_tree for t in self.temperature_data],
                "overall": (self.pscu.get_temperature_state,  None),
                "latched": (self.pscu.get_temperature_latched,  None),
            },
            "humidity": {
                "sensors": [h.param_tree for h in self.humidity_data],
                "overall": (self.pscu.get_humidity_state, None),
                "latched": (self.pscu.get_humidity_latched, None),
            },
            "fan": {
                "target": (self.pscu.get_fan_target, self.pscu.set_fan_target),
                "currentspeed_volts": (self.pscu.get_fan_speed_volts, None),
                "currentspeed": (self.pscu.get_fan_speed, None),
                "setpoint": (self.pscu.get_fan_set_point, None),
                "setpoint_volts": (self.pscu.get_fan_set_point_volts, None),
                "tripped": (self.pscu.get_fan_tripped, None),
                "overall": (self.pscu.get_fan_state, None),
                "latched": (self.pscu.get_fan_latched, None),
                "mode": (self.pscu.get_fan_mode, None),
            },
            "pump": {
                "flow": (self.pscu.get_pump_flow, None),
                "flow_volts": (self.pscu.get_pump_flow_volts, None),
                "setpoint": (self.pscu.get_pump_set_point, None),
                "setpoint_volts": (self.pscu.get_pump_set_point_volts, None),
                "tripped": (self.pscu.get_pump_tripped, None),
                "overall": (self.pscu.get_pump_state, None),
                "latched": (self.pscu.get_pump_latched, None),
                "mode": (self.pscu.get_pump_mode, None),
            },
            "trace": {
                 "overall": (self.pscu.get_trace_state, None),
                 "latched": (self.pscu.get_trace_latched,  None),
            },
            "position": (self.pscu.get_position, None),
            "position_volts": (self.pscu.get_position_volts, None),
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

        :param path: path of parameter tree to get
        :returns: parameter tree at that path as a dictionary
        """
        try:
            return self.param_tree.get(path)
        except ParameterTreeError as e:
            raise PSCUDataError(e)

    def set(self, path, data):
        """Set parameters in underlying parameter tree.

        This method simply wraps underlying ParameterTree method so that an exceptions can be
        re-raised with an appropriate PSCUDataError.

        :param path: path of parameter tree to set values for
        :param data: dictionary of new data values to set in the parameter tree
        """
        try:
            self.param_tree.set(path, data)
        except ParameterTreeError as e:
            raise PSCUDataError(e)

    def get_all_latched(self):
        """Return the global latch status of the PSCU.

        This method returns the global latch status for the PSCU, which is the logical AND of
        PSCU latch channels

        :returns: global latch status as bool
        """
        return all(self.pscu.get_all_latched())

    def get_quad_traces(self):
        """Return the trace status for the quads in the PSCU.

        This method returns a dictionary of the quad trace status values for the PSCU.

        :returns: dictionary of the quad trace status
        """
        return {str(q): self.pscu.get_quad_trace(q) for q in range(self.pscu.num_quads)}
