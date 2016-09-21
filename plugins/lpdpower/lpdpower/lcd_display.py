from usblcd import UsbLcd

from functools import partial
import logging
import time

class LcdDisplayError(Exception):
    pass

class LcdDisplay(object):

    GREEN = UsbLcd.GREEN
    RED   = UsbLcd.RED

    def __init__(self, pscu, serial_dev, baud=57600, rows=4, cols=20):

        self.pscu = pscu

        try:
            self.lcd = UsbLcd(serial_dev, baud, rows, cols)
        except Exception as e:
            raise LcdDisplayError("Failed to initialise LCD: {}".format(e))

        self.lcd.clear()

        self.current_page = 0
        self.registered_pages = []

        self.registered_pages.append(self.overview_page)

        self.temps_per_page = 4
        self.num_temp_pages = int(round(float(self.pscu.numTemperatures) / self.temps_per_page))

        for page in range(self.num_temp_pages):
            self.registered_pages.append(partial(self.temperature_page, page))

        self.registered_pages.append(self.humidity_page)
        self.registered_pages.append(self.fan_page)
        self.registered_pages.append(self.pump_page)

        self.registered_pages.append(self.trace_page)

        self.registered_pages.append(self.quad_supply_page)
        
        for quad in range(4):
            for chan in range(2):
                self.registered_pages.append(partial(self.quad_page, quad, chan*2))

        self.registered_pages.append(self.system_page)

        self.lcd_buffer = ""
        self.lcd_colour = 0

        self.time_format = '%H:%M:%S' # %d-%b-%y'

    def set_colour(self, colour):
        
        if colour != self.lcd_colour:
            self.lcd.set_backlight_colour(colour)
            self.lcd_colour = colour

    def next_page(self):
        
        self.current_page += 1
        self.current_page %= len(self.registered_pages)

    def previous_page(self):

        self.current_page -= 1
        self.current_page %= len(self.registered_pages)

    def update(self):

        content = self.registered_pages[self.current_page]()

        if content != self.lcd_buffer:
            self.lcd_buffer = content
            self.lcd.home()
            self.lcd.write(self.lcd_buffer)

    def page_header(self):

        header = '{:9s}      {:2d}/{:2d}'.format(
            time.strftime(self.time_format), self.current_page+1, len(self.registered_pages)
        )
        
        return header

    def overview_page(self):

        healthy = self.pscu.getHealth()
        all_latched = all(self.pscu.getAllLatched())
        armed = self.pscu.getArmed()

        content = self.page_header()
        content += 'System  : {}\r'.format('Healthy' if healthy else 'ERROR')
        content += 'Latched : {}\r'.format('No' if all_latched else 'YES')
        content += 'Armed   : {}\r'.format('Yes' if armed else 'No')

        return content

    def format_state_str(self, output, latched):
        
        state_str = ''
        if output:
            state_str = 'OK{}'.format('' if latched else '/Latch')
        else:
            state_str = 'TRIPPED'

        return state_str

    def temperature_page(self, page):

        content = self.page_header()

        num_temp_vals = self.pscu.numTemperatures

        start_chan = page * self.temps_per_page
        end_chan = start_chan + self.temps_per_page

        state_str = self.format_state_str(self.pscu.getTempOutput(), self.pscu.getTempLatched())

        content += 'Temp {}/{}: {}\r'.format(page+1, self.num_temp_pages, state_str)

        for chan in range(start_chan, end_chan):
            if chan < num_temp_vals:
                chan_temp = self.pscu.getTemperature(chan)
                chan_trip = '*' if self.pscu.getTempTripped(chan) else ' '
                temp_disp = '{:2d}:{:4.1f}C{} '.format(chan+1, chan_temp, chan_trip)
            else:
                temp_disp = '\r'

            content += temp_disp
        
        return content

    def humidity_page(self):

        content = self.page_header()

        state_str = self.format_state_str(self.pscu.getHumidityOutput(), self.pscu.getHumidityLatched())

        content += 'Humidity: {}\r'.format(state_str)

        for chan in range(self.pscu.numHumidities):
            chan_humid = self.pscu.getHumidity(chan)
            chan_trip  = '*' if self.pscu.getHTripped(chan) else ' '
            content += '{}:{:4.1f}%{} '.format(chan+1, chan_humid, chan_trip)

        content += '\r\r'

        return content

    def fan_page(self):

        content = self.page_header()

        state_str = self.format_state_str(self.pscu.getFanOutput(), self.pscu.getFanLatched())

        content += 'Fan: {}\r'.format(state_str)
        content += 'Target:  {:3d}%\r'.format(self.pscu.getFanTarget())
        content += 'Speed : {:4.1f}Hz\r'.format(self.pscu.getFanSpeed())
        content += time.strftime(self.time_format)

        return content

    def pump_page(self):
        
        content = self.page_header()

        state_str = self.format_state_str(self.pscu.getPumpOutput(), self.pscu.getPumpLatched())

        content += 'Pump: {}\r'.format(state_str)
        content += 'Flow: {:.1f}l/min\r'.format(self.pscu.getPumpFlow())
        content += '\r'

        return content

    def format_trace_str(self, traces):

        trace_str = ''.join(['*' if trace else '_' for trace in traces])
        return trace_str

    def trace_page(self):

        content = self.page_header()

        state_str = self.format_state_str(self.pscu.getTraceOutput(), self.pscu.getTraceLatched())
        
        temp_traces = [self.pscu.getTempTrace(chan) for chan in range(self.pscu.numTemperatures)]
        humidity_traces = [self.pscu.getHTrace(chan) for chan in range(self.pscu.numHumidities)]
        quad_traces = [self.pscu.getQuadTrace(chan) for chan in range(self.pscu.numQuads)]

        content += 'Trace: {}\r'.format(state_str)
        content += 'Temp: {}\r'.format(self.format_trace_str(temp_traces))
        content += 'Hum: {} Quad: {}\r'.format(
            self.format_trace_str(humidity_traces),
            self.format_trace_str(quad_traces)
        )

        return content
    
    def quad_supply_page(self):
        
        content = self.page_header()
        
        content += 'Quad supplies\r'
        
        quad_supply_volts = [self.pscu.quad[quad].getSupplyVoltage() for quad in range(4)]
        
        content += '1: {:4.1f}V 2:{:4.1f}V\r'.format(quad_supply_volts[0], quad_supply_volts[1])
        content += '3: {:4.1f}V 4:{:4.1f}V\r'.format(quad_supply_volts[2], quad_supply_volts[3])
        
        return content

    def quad_page(self, quad, start_chan):

        content = self.page_header()

        quad_chans = [start_chan, start_chan+1]                                                                                                                     

        quad_supply_volts = self.pscu.quad[quad].getSupplyVoltage()
        
        content += 'Quad: {} Chans: {}/{} \r'.format(quad + 1, *[chan+1 for chan in quad_chans])

        for quad_chan in quad_chans:
            quad_enable = ('ON ' if self.pscu.quad[quad].getEnable(quad_chan) else 'OFF')
            quad_volts = self.pscu.quad[quad].getChannelVoltage(quad_chan)
            quad_fuse_volts = self.pscu.quad[quad].getFuseVoltage(quad_chan)
            quad_current = self.pscu.quad[quad].getChannelCurrent(quad_chan)

            fuse_ok = True
            if quad_supply_volts > 24.0:
                fuse_delta_volts = abs(quad_fuse_volts - quad_supply_volts)
                if fuse_delta_volts > 2.0:
                    fuse_ok = False
            
            if fuse_ok:          
                content += '{}:{} {:4.1f}V {:4.1f}A OK'.format(
                    quad_chan+1, quad_enable, quad_volts, quad_current)
            else:
                content += '{}:Fuse blow? ({:4.1f}V)'.format(
                    quad_chan+1, quad_fuse_volts)

        return content

    def system_page(self):

        content = self.page_header()
        content += 'System Info\r'
        content += 'TODO'
        content += '\r\r'
        
        return content

