
"""humidity_data - humidity data container classes.

This module implements the HumidityData class used to represent the data associated
with humidity channels on the LPD power supply control unit.

Tim Nicholls, STFC Detector Systems Software Group.
"""
from odin.adapters.parameter_tree import ParameterTree

class HumidityData(object):
    """Data container for a PSCU humidity sensor.

    This class implements a data container and parameter tree for a PSCU
    humidity sensor, which, in addition to having a readable value, also
    has parameters indicated set point, trace, trip state, and disable.
    """

    def __init__(self, pscu, sensor_idx):
        """Initialise the temperature data container for a sensor.

        This constructor initalises the data container for a humidity
        sensor, creating the parameter tree and associating it with a
        particular sensor on the PSCU.

        :param pscu: PSCU object to use to access the sensor
        :param sensor_idx: sensor index on PSCU
        """
        self.pscu = pscu
        self.sensor_idx = sensor_idx

        self.param_tree = ParameterTree({
            "humidity": (self.get_humidity, None),
            "humidity_volts": (self.get_humidity_volts, None),
            "setpoint": (self.get_set_point, None),
            "setpoint_volts": (self.get_set_point_volts, None),
            "tripped": (self.get_tripped, None),
            "trace": (self.get_trace, None),
            "disabled": (self.get_disabled, None),
            "sensor_name": (self.get_name, None),
            "mode": (self.get_mode, None),
        })


    def get_humidity(self):
        """Get the current humidity read by the sensor.

        This method returns the humidity read by the sensor from the PSCU.

        :returns: humidity in percent
        """
        return self.pscu.get_humidity(self.sensor_idx)

    def get_humidity_volts(self):
        """Get the current raw humidity read by the sensor.

        This method returns the raw humidity read by the sensor from the PSCU.

        :returns: raw humidity in volts
        """
        return self.pscu.get_humidity_volts(self.sensor_idx)

    def get_set_point(self):
        """Get the setpoint value of the humidity sensor.

        This method returns the set point value of the humidity sensor from the PSCU.

        :returns: set point value in percent
        """
        return self.pscu.get_humidity_set_point(self.sensor_idx)

    def get_set_point_volts(self):
        """Get the raw setpoint value of the humidity sensor.

        This method returns the raw set point value of the humidity sensor from the PSCU.

        :returns: set raw point value in volts
        """
        return self.pscu.get_humidity_set_point_volts(self.sensor_idx)

    def get_tripped(self):
        """Get the trip status of the humidity sensor.

        This method returns the trip status of the sensor from the PSCU, i.e. if it has
        exceeded the specified set point.

        :returns: trip status as boolean.
        """
        return self.pscu.get_humidity_tripped(self.sensor_idx)

    def get_trace(self):
        """Get the trace status of the humidity sensor.

        This method returns the trace status (signal connection) of the sensor from the PSCU.

        :returns: trace status as boolean.
        """
        return self.pscu.get_humidity_trace(self.sensor_idx)

    def get_disabled(self):
        """Get the disabled status of the humidity sensor.

        This method returns the disabled status of the humidity sensor, i.e. if it
        has been disabled from the overall interlock state by a jumper connection.

        :returns: disabled status as boolean.
        """
        return self.pscu.get_humidity_disabled(self.sensor_idx)

    def get_name(self):
        """Get the name of the humidity sensor.

        This method returns the descriptive name of the humidity sensor.

        :returns: sensor name as a string
        """
        return self.pscu.get_humidity_name(self.sensor_idx)

    def get_mode(self):
        """Get the mode of the humidity sensor.

        This method returns the descriptive mode of the humidity sensor.

        :returns: sensor mode as a string
        """
        return self.pscu.get_humidity_mode(self.sensor_idx)
