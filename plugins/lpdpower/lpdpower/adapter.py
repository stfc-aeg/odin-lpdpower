from odin.adapters.adapter import ApiAdapter, ApiAdapterResponse, request_types, response_types
from tornado.escape import json_decode
from concurrent import futures
from tornado.ioloop import IOLoop
from tornado.concurrent import run_on_executor
from pscu_data import PSCUData, PSCUDataError
import time
import sys
import logging


class NullDevice():

    def write(self, s):
        pass


class LPDPowerAdapter(ApiAdapter):

    def __init__(self, **kwargs):
        super(LPDPowerAdapter, self).__init__(**kwargs)

        sys.stdout = NullDevice()  # Prevent I2C spam if devices aren't connected

        # Retrieve adapter options from config file
        self.update_interval = float(self.options.get('update_interval', 0.05))
        quad_enable_interval = float(self.options.get('quad_enable_interval', 1.0))

        # Create a PSCUData instance
        self.pscuData = PSCUData(quad_enable_interval=quad_enable_interval)

        # Start the update loop
        self.update_loop()

    @request_types('application/json')
    @response_types('application/json')
    def get(self, path, request):
        try:
            response = self.pscuData.get(path)
            status_code = 200
        except PSCUDataError as e:
            response = {'error': str(e)}
            status_code = 400
        return ApiAdapterResponse(response, status_code=status_code)

    @request_types('application/json')
    @response_types('application/json')
    def put(self, path, request):
        try:
            data = json_decode(request.body)
            self.pscuData.set(path, data)
            response = self.pscuData.get(path)
            status_code = 200
        except PSCUDataError as e:
            response = {'error': str(e)}
            status_code = 400
        except (TypeError, ValueError) as e:
            response = {'error': 'Failed to decode PUT request body: {}'.format(str(e))}
            status_code = 400
        return ApiAdapterResponse(response, status_code=status_code)

    def update_loop(self):
        self.pscuData.pscu.handle_deferred()
        self.pscuData.pscu.updateLCD()
        self.pscuData.pscu.pollAllSensors()
        IOLoop.instance().call_later(self.update_interval, self.update_loop)
