"""Test cases for the I2CTContainer class from lpdpower.

Tim Nicholls, STFC Application Engineering Group
"""

import sys

if sys.version_info[0] == 3:  # pragma: no cover
    from unittest.mock import Mock, call
else:                         # pragma: no cover
    from mock import Mock, call

from nose.tools import *
from functools import partial

smbus_mock = Mock()
sys.modules['smbus'] = smbus_mock

from lpdpower.i2c_device import I2CDevice, I2CException

def setup_i2c_device_exception(method):
    """
    Decorator method for generated test cases to allow exceptions to be enabled and disabled
    """
    def wrap(func):
        def wrapped_f(_self, exc_mode):

            print 'in wrapper with exc_mode', exc_mode, 'func', func.__name__, 'method', method

            if exc_mode == _self.EXC_MODE_NONE:
                smbus_mock.side_effect = None
                _self.device.disable_exceptions()
            elif exc_mode == _self.EXC_MODE_TRAP:
                smbus_mock.side_effect = IOError('boom')
                _self.device.disable_exceptions()
            elif exc_mode == _self.EXC_MODE_RAISE:
                smbus_mock.side_effect = IOError('boom')
                _self.device.enable_exceptions()
            else:
                raise Exception('Illegal exception test mode {}'.format(exc_mode))
            func(_self)
        return wrapped_f
    return wrap

class TestI2CDevice(object):

    EXC_MODE_NONE, EXC_MODE_TRAP, EXC_MODE_RAISE = range(3)
    EXC_MODES = [EXC_MODE_NONE, EXC_MODE_TRAP, EXC_MODE_RAISE]
    EXC_MODE_NAME = ['exc_mode_node', 'exc_mode_trap', 'exc_mode_raise']

    @classmethod
    def setup_class(cls):

        cls.device_busnum = 1
        cls.device_address = 0x70
        cls.device_debug = True
        cls.device = I2CDevice(cls.device_address, cls.device_busnum, cls.device_debug)
        cls.device.pre_access = Mock()

    def test_device_init(self):

        assert_equal(self.device_address, self.device.address)
        assert_equal(self.device_debug, self.device.debug)

    def test_pre_access_called(self):

        self.device.write8(1, 20)
        self.device.pre_access.assert_called_with(self.device)

    def test_enable_exceptions(self):

        self.device.enable_exceptions()
        assert_true(self.device._enable_exceptions)

    def test_disable_exceptions(self):

        self.device.disable_exceptions()
        assert_false(self.device._enable_exceptions)

    def test_handle_error_no_exception(self):

        smbus_mock_cached = smbus_mock.side_effect
        smbus_mock.side_effect = IOError("boom")
        self.device.disable_exceptions()
        rc = self.device.write8(1, 0)
        assert_equal(rc, -1)

    def test_generator(self):

        for (test, name) in [
            (self._test_one, 'test_one'),
            (self._test_two, 'test_two')
        ]:
            for exc_mode in self.EXC_MODES:
                test_func = partial(test, exc_mode)
                test_func.description = '{}.{}.{}_{}'.format(
                    __name__, type(self).__name__, name, self.EXC_MODE_NAME[exc_mode]
                )
                yield (test_func, )

    @setup_i2c_device_exception('write8')
    def _test_one(self):
        print("Test one with flag", self.device._enable_exceptions)
        self.device.write8(1, 0)

    @setup_i2c_device_exception
    def _test_two(self):
        print("Test two with flag", self.device._enable_exceptions)
