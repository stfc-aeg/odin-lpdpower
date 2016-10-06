from i2c_device import I2CDevice, I2CException
from i2c_container import I2CContainer
from tca9548 import TCA9548
from ad7998 import AD7998
from ad5321 import AD5321
from mcp23008 import MCP23008
from quad import Quad
from lcd_display import LcdDisplay, LcdDisplayError
from deferred_executor import DeferredExecutor

import Adafruit_BBIO.GPIO as GPIO

import logging
import time

# PSCU consisting of 4x Quads & Other sensors


class PSCU(I2CContainer):
    ALL_PINS = [0, 1, 2, 3, 4, 5, 6, 7]
    DEFAULT_QUAD_ENABLE_INTERVAL = 1.0

    def __init__(self, quad_enable_interval=DEFAULT_QUAD_ENABLE_INTERVAL):

        I2CDevice.disable_exceptions()

        self.quad_enable_interval = quad_enable_interval

        self.tca = TCA9548(0x70)

        # Attach quads to tca
        self.numQuads = 4
        self.quad = []
        for i in range(self.numQuads):
            self.quad.append(self.tca.attach_device(i, Quad))

        # Attach bus 4 devices
        # Temperature monitor AD7998s
        self.adcTempMon = []
        self.adcTempMon.append(self.tca.attach_device(4, AD7998, 0x21))
        self.adcTempMon.append(self.tca.attach_device(4, AD7998, 0x22))
        self.adcTempMon.append(self.tca.attach_device(4, AD7998, 0x23))

        # Temperature monitor MCP23008s
        self.mcpTempMon = []
        self.mcpTempMon.append(self.tca.attach_device(4, MCP23008, 0x24))
        for i in range(8):
            self.mcpTempMon[0].setup(i, MCP23008.IN if i < 7 else MCP23008.IN)

        self.mcpTempMon.append(self.tca.attach_device(4, MCP23008, 0x25))
        for i in range(8):
            self.mcpTempMon[1].setup(i, MCP23008.IN)

        self.mcpTempMon.append(self.tca.attach_device(4, MCP23008, 0x26))
        for i in range(8):
            self.mcpTempMon[2].setup(i, MCP23008.IN)

        self.mcpTempMon.append(self.tca.attach_device(4, MCP23008, 0x27))
        for i in range(8):
            self.mcpTempMon[3].setup(i, MCP23008.IN)

        # Attach bus 5 devices
        # Misc AD7998s
        self.adcMisc = []
        self.adcMisc.append(self.tca.attach_device(5, AD7998, 0x21))
        self.adcMisc.append(self.tca.attach_device(5, AD7998, 0x22))

        # Misc MCP23008s
        self.mcpMisc = []
        self.mcpMisc.append(self.tca.attach_device(5, MCP23008, 0x24))
        for i in range(8):
            self.mcpMisc[0].setup(i, MCP23008.OUT if i < 2 else MCP23008.IN)
        self.mcpMisc.append(self.tca.attach_device(5, MCP23008, 0x25))
        for i in range(8):
            self.mcpMisc[1].setup(i, MCP23008.IN)
        self.mcpMisc.append(self.tca.attach_device(5, MCP23008, 0x26))
        for i in range(8):
            self.mcpMisc[2].setup(i, MCP23008.IN)
        self.mcpMisc.append(self.tca.attach_device(5, MCP23008, 0x27))
        for i in range(8):
            self.mcpMisc[3].setup(i, MCP23008.IN)

        # Fan speed AD5321
        self.fanSpd = self.tca.attach_device(5, AD5321, 0x0c)

        # Buffers for all I2C sensors
        # Temperature
        self.numTemperatures = 11
        self.__tempValues = [0.0] * self.numTemperatures
        self.__tempSetPoints = [0.0] * self.numTemperatures
        self.__tempTrips = [False] * self.numTemperatures
        self.__tempTraces = [False] * self.numTemperatures
        self.__tempDisabled = [False] * self.numTemperatures

        # Humidity
        self.numHumidities = 2
        self.__hValues = [0.0] * self.numHumidities
        self.__hSetPoints = [0.0] * self.numHumidities
        self.__hTrips = [False] * self.numHumidities
        self.__hTraces = [False] * self.numHumidities
        self.__hDisabled = [False] * self.numHumidities

        # Pump
        self.__pumpFlow = 0.0
        self.__pumpSetPoint = 0.0
        self.__pumpTrip = False

        # Fan
        self.__fanSpeed = 0.0
        self.__fanTarget = 100.0
        self.__fanSetPoint = 0.0
        self.__fanTrip = False

        # Position
        self.__position = 0.0

        # Quad traces
        self.__qTraces = [False] * self.numQuads

        # Overall
        self.__armed = False
        self.__healthy = False
        self.__sensorOutputs = [False] * 5  # Tmp, F, P, H, T
        self.__latchedOutputs = [False] * 5  # Tmp, F, P, T, H

        # LCD Display
        try:
            self.lcd = LcdDisplay(self, "/dev/ttyACM0", 57600, rows=4, cols=20)
            self.lcd_display_error = False
        except LcdDisplayError as e:
            logging.warning(e)
            self.lcd_display_error = True

        GPIO.setup("P9_11", GPIO.IN)
        GPIO.setup("P9_12", GPIO.IN)
        GPIO.add_event_detect("P9_11", GPIO.RISING)
        GPIO.add_event_detect("P9_12", GPIO.RISING)

        # Internal flag tracking state of quads 'enable all' command
        self.__allEnabled = False

        self.deferred_executor = DeferredExecutor()

    def handle_deferred(self):
        self.deferred_executor.process()

    def get_temperature(self, sensor):
        if sensor > 10 or sensor < 0:
            raise I2CException('Illegal sensor index {} specified'.format(sensor))

        return self.__tempValues[sensor]

    def get_temp_set_point(self, sensor):
        if sensor > 10 or sensor < 0:
            raise I2CException('Illegal sensor index {} specified'.format(sensor))

        return self.__tempSetPoints[sensor]

    def get_temp_tripped(self, sensor):
        if sensor > 10 or sensor < 0:
            raise I2CException('Illegal sensor index {} specified'.format(sensor))

        return self.__tempTrips[sensor]

    def get_temp_trace(self, sensor):
        if sensor > 10 or sensor < 0:
            raise I2CException('Illegal sensor index {} specified'.format(sensor))

        return self.__tempTraces[sensor]

    def get_temp_disabled(self, sensor):
        if sensor > 10 or sensor < 0:
            raise I2CException('Illegal sensor index {} specified'.format(sensor))

        return self.__tempDisabled[sensor]

    def get_humidity(self, sensor):
        if sensor > 1 or sensor < 0:
            raise I2CException('Illegal sensor index {} specified'.format(sensor))

        return self.__hValues[sensor]

    def get_humidity_set_point(self, sensor):
        if sensor > 1 or sensor < 0:
            raise I2CException('Illegal sensor index {} specified'.format(sensor))

        return self.__hSetPoints[sensor]

    def get_humidity_tripped(self, sensor):
        if sensor > 1 or sensor < 0:
            raise I2CException('Illegal sensor index {} specified'.format(sensor))

        return self.__hTrips[sensor]

    def get_humidity_trace(self, sensor):
        if sensor > 1 or sensor < 0:
            raise I2CException('Illegal sensor index {} specified'.format(sensor))

        return self.__hTraces[sensor]

    def get_humidity_disabled(self, sensor):
        if sensor > 1 or sensor < 0:
            raise I2CException('Illegal sensor index {} specified'.format(sensor))

        return self.__hDisabled[sensor]

    def get_pump_flow(self):
        return self.__pumpFlow

    def get_pump_set_point(self):
        return self.__pumpSetPoint

    def get_pump_tripped(self):
        return self.__pumpTrip

    def get_fan_speed(self):
        return self.__fanSpeed

    def get_fan_set_point(self):
        return self.__fanSetPoint

    def get_fan_target(self):
        return self.__fanTarget

    def get_fan_tripped(self):
        return self.__fanTrip

    def get_quad_trace(self, quad_idx):
        if quad_idx > 3 or quad_idx < 0:
            raise I2CException("Illegal quad index {} specified".format(quad_idx))

        return self.__qTraces[quad_idx]

    def get_position(self):
        return self.__position

    def get_armed(self):
        return self.__armed

    def get_all_enabled(self):
        return self.__allEnabled

    def get_health(self):
        return self.__healthy

    def get_temp_output(self):
        return self.__sensorOutputs[0]

    def get_temp_latched(self):
        return self.__latchedOutputs[0]

    def get_trace_output(self):
        return self.__sensorOutputs[4]

    def get_trace_latched(self):
        return self.__latchedOutputs[3]

    def get_fan_output(self):
        return self.__sensorOutputs[1]

    def get_fan_latched(self):
        return self.__latchedOutputs[1]

    def get_pump_output(self):
        return self.__sensorOutputs[2]

    def get_pump_latched(self):
        return self.__latchedOutputs[2]

    def get_humidity_output(self):
        return self.__sensorOutputs[3]

    def get_humidity_latched(self):
        return self.__latchedOutputs[4]

    def get_all_latched(self):
        return self.__latchedOutputs

    def get_enable_interval(self):
        return self.quad_enable_interval

    def quad_enable_channel(self, quad_idx, channel):

        if quad_idx > 3 or quad_idx < 0:
            raise I2CException("Illegal quad index {} specified".format(quad_idx))

        if channel >= Quad.NUM_CHANNELS or channel < 0:
            raise I2CException("Illegal channel index {} specified".format(channel))

        logging.debug("Enabling quad {} channel {} output".format(quad_idx, channel))
        self.quad[quad_idx].set_enable(channel, True)

    def enable_all(self, enable):
        logging.debug("Called enable_all with value {}".format(enable))

        if enable:
            # Loop over all quads and channels in system, adding enable command to deferred
            # executor queue
            for quad_idx in range(len(self.quad)):
                for channel in range(Quad.NUM_CHANNELS):
                    self.deferred_executor.enqueue(
                        self.quad_enable_channel, self.quad_enable_interval, quad_idx, channel
                    )
            self.__allEnabled = True
        else:
            # Clear any pending turn-on command from the queue first, then turn off all channels
            # immediately.
            num_enables_pending = self.deferred_executor.pending()
            if num_enables_pending > 0:
                logging.debug("Clearing {} pending quad enable commands from queue".format(
                    num_enables_pending
                ))
                self.deferred_executor.clear()
            for quad_idx in range(len(self.quad)):
                for channel in range(Quad.NUM_CHANNELS):
                    self.quad[quad_idx].set_enable(channel, False)
            self.__allEnabled = False

    def set_armed(self, value):
        pin = 0 if value else 1
        self.mcpMisc[0].output(pin, MCP23008.LOW)
        self.mcpMisc[0].output(pin, MCP23008.HIGH)
        self.mcpMisc[0].output(pin, MCP23008.LOW)

    def set_fan_target(self, value):
        self.__fanTarget = value
        self.fanSpd.set_output_scaled(1.0 - (value / 100.0))

    def get_display_error(self):
        return self.lcd_display_error

    def update_lcd(self):

        # Do nothing if display was not initlialised OK
        if self.lcd_display_error:
            return

        # Get input
        if GPIO.event_detected("P9_11"):
            self.lcd.previous_page()
        elif GPIO.event_detected("P9_12"):
            self.lcd.next_page()

        if self.__healthy:
            self.lcd.set_colour(LcdDisplay.GREEN)
        else:
            self.lcd.set_colour(LcdDisplay.RED)

        self.lcd.update()

    def convert_ad7998_temp(self, fs_val):

        temp_vref = 3.0
        temp_scale_v_kelvin = 0.005
        temp_val = ((fs_val * temp_vref) / temp_scale_v_kelvin) - 273.15

        return temp_val

    def poll_all_sensors(self):

        # Temperature ADCs
        for i in range(8):
            adc_input_fs = self.adcTempMon[0].read_input_scaled(i)
            set_point = self.convert_ad7998_temp(adc_input_fs)
            #logging.debug("poll_all_sensors %d %f %f %f " %( i, adc_input_fs, adc_input_fs*4095, set_point))
            # self.convert_ad7998_temp(self.adcTempMon[0].read_input_scaled(i))
            self.__tempSetPoints[i] = set_point

        for i in range(8):
            self.__tempValues[i] = self.convert_ad7998_temp(
                self.adcTempMon[1].read_input_scaled(i))

        for i in range(3):
            self.__tempValues[
                i + 8] = self.convert_ad7998_temp(self.adcTempMon[2].read_input_scaled(i))

        for i in range(4, 7):
            self.__tempSetPoints[
                i + 4] = self.convert_ad7998_temp(self.adcTempMon[2].read_input_scaled(i))

        # Temperature MCPs
        buff = self.mcpTempMon[0].input_pins([0, 1, 2, 3, 4, 5, 7])
        for i in range(4):
            self.__tempDisabled[i + 4] = buff[i]
        self.__tempDisabled[10] = buff[4]
        self.__hDisabled[1] = buff[5]
        self.__sensorOutputs[0] = buff[6]

        buff = self.mcpTempMon[1].input_pins(self.ALL_PINS)
        for i in range(8):
            self.__tempTrips[i] = not bool(buff[i])

        buff = self.mcpTempMon[2].input_pins(self.ALL_PINS)
        for i in range(8):
            self.__tempTraces[i] = bool(buff[i])

        buff = self.mcpTempMon[3].input_pins([0, 1, 2, 3, 4, 5])
        for i in range(3):
            self.__tempTrips[i + 8] = not bool(buff[i])
        for i in range(3, 6):
            self.__tempTraces[i + 5] = bool(buff[i])

        #Misc. ADCs
        self.__fanSpeed = self.adcMisc[1].read_input_scaled(0) * 5 / 4.5 * 50
        self.__hValues[0] = self.adcMisc[1].read_input_scaled(1) * 100 * 5 / 3.9
        self.__hValues[1] = self.adcMisc[1].read_input_scaled(2) * 100 * 5 / 3.9
        self.__pumpFlow = self.adcMisc[1].read_input_scaled(3) * 5 / 4.32 * 35
        self.__position = self.adcMisc[1].read_input_scaled(4) * 100

        self.__fanSetPoint = self.adcMisc[0].read_input_scaled(0) * 5 / 4.5 * 50
        self.__hSetPoints[0] = self.adcMisc[0].read_input_scaled(1) * 100 * 5 / 3.9
        self.__hSetPoints[1] = self.adcMisc[0].read_input_scaled(2) * 100 * 5 / 3.9
        self.__pumpSetPoint = self.adcMisc[0].read_input_scaled(3) * 5 / 4.32 * 35

        #Misc. MCPs
        buff = self.mcpMisc[0].input_pins([2, 3, 4, 5, 6, 7])
        self.__armed = bool(buff[0])
        for i in range(1, 5):
            self.__sensorOutputs[i] = bool(buff[i])
        self.__healthy = bool(buff[5])

        buff = self.mcpMisc[1].input_pins([0, 1, 2, 3])
        self.__fanTrip = not bool(buff[0])
        self.__hTrips[0] = not bool(buff[1])
        self.__hTrips[1] = not bool(buff[2])
        self.__pumpTrip = not bool(buff[3])

        buff = self.mcpMisc[2].input_pins([1, 2, 4, 5, 6, 7])
        self.__hTraces[0] = bool(buff[0])
        self.__hTraces[1] = bool(buff[1])
        for i in range(2, 6):
            self.__qTraces[i - 2] = bool(buff[i])

        buff = self.mcpMisc[3].input_pins([0, 1, 2, 3, 4])
        self.__latchedOutputs = [bool(i) for i in buff]

        # Update internal allEnabled state based on current armed state since being disarmed
        # automatically turns off all quad outputs
        if not self.__armed:
            self.__allEnabled = False

        # Poll sensors for all quads also
        for quad in self.quad:
            quad.poll_all_sensors()
