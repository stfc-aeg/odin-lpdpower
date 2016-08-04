from usblcd import UsbLcd

from functools import partial
import logging
import time

class LcdDisplay(object):

    GREEN = UsbLcd.GREEN
    RED   = UsbLcd.RED

    def __init__(self, pscu, serial_dev, baud=57600, rows=4, cols=20):

        self.pscu = pscu

        self.lcd = UsbLcd(serial_dev, baud, rows, cols)
      
        self.current_screen = 0
        self.registered_screens = []

        self.registered_screens.append(self.system_screen)
        for quad in range(4):
            for chan in range(2):
                self.registered_screens.append(partial(self.quad_screen, quad, chan*2))
        self.registered_screens.append(self.temperature_screen)
        self.registered_screens.append(self.humidity_screen)
        self.registered_screens.append(self.fan_screen)
        self.registered_screens.append(self.pump_screen)

        self.lcd_buffer = ""
        self.lcd_colour = 0

        self.time_format = '%H:%M:%S %d-%b-%y'

    def set_colour(self, colour):
        
        if colour != self.lcd_colour:
            self.lcd.set_backlight_colour(colour)
            self.lcd_colour = colour

    def next_screen(self):
        
        self.current_screen += 1
        self.current_screen %= len(self.registered_screens)

    def previous_screen(self):

        self.current_screen -= 1
        self.current_screen %= len(self.registered_screens)

    def update(self):

        content = self.registered_screens[self.current_screen]()
        if content != self.lcd_buffer:
            self.lcd_buffer = content
            self.lcd.clear()
            self.lcd.write(self.lcd_buffer)

    def system_screen(self):

        healthy = self.pscu.getHealth()
        all_latched = all(self.pscu.getAllLatched())
        armed = self.pscu.getArmed()

        content = \
            "System  : " + ("Healthy" if healthy else "ERROR") + '\r' + \
            "Latched : " + ("No" if all_latched else "YES") + '\r' + \
            "Armed   : " + ("Yes" if armed else "No") + '\r' + \
            time.strftime(self.time_format)

        return content

    def quad_screen(self, quad, start_chan):

        quad_chans = [start_chan, start_chan+1]                                                                                                                     

        content = 'Quad: {} Chans: {}/{} \r'.format(quad + 1, *[chan+1 for chan in quad_chans])

        for quad_chan in quad_chans:
            quad_enable = ('ON ' if self.pscu.quad[quad].isEnabled(quad_chan) else 'OFF')
            quad_volts = self.pscu.quad[quad].getChannelVoltage(quad_chan)
            quad_fuse = 'OK'
            quad_current = self.pscu.quad[quad].getChannelCurrent(quad_chan)

            content = content + '{}:{} {:04.1f}V {:04.1f}A {}'.format(
                quad_chan+1, quad_enable, quad_volts, quad_current, quad_fuse)

        content = content + time.strftime(self.time_format)
        return content

    def temperature_screen(self):

        return "Temperatures\rTODO\r" + time.strftime(self.time_format)

    def humidity_screen(self):

        return "Humidity\rTODO\r" + time.strftime(self.time_format)

    def fan_screen(self):

        return "Fan\rTODO\r" + time.strftime(self.time_format)

    def pump_screen(self):

        return "Pump\rTODO\r" + time.strftime(self.time_format)
