import os
from ctypes import *

class ExcaliburFemConfig(Structure):

    _fields_ = [
                ('fem_number',  c_int),
                ('fem_address',  c_char_p),
                ('fem_port',     c_int),
                ('data_address', c_char_p),
                ]

class ExcaliburFemError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ExcaliburFem(object):

    FEM_RTN_OK = 0
    FEM_RTN_UNKNOWNOPID = 1
    FEM_RTN_ILLEGALCHIP = 2
    FEM_RTN_BADSIZE = 3
    FEM_RTN_INITFAILED = 4

    use_stub_library = False
    library_stem = 'fem_api'

    def __init__(self, fem_id, fem_addr='192.168.0.1', fem_port=6969, data_addr='10.0.2.1'):

        self.fem_handle = None

        base_path = os.path.dirname(os.path.abspath(__file__))
        if ExcaliburFem.use_stub_library:
            lib_name = os.path.join(base_path, '{}_stub.so'.format(ExcaliburFem.library_stem))
        else:
            lib_name = os.path.join(base_path, '{}.so'.format(ExcaliburFem.library_stem))

        try:
            self._api = cdll.LoadLibrary(lib_name)
        except OSError as e:
            raise ExcaliburFemError('Error loading API library: {}'.format(lib_name))

        self._api.femErrorCode.restype = c_int
        self._api.femErrorMsg.restype = c_char_p

        self._api.femInitialise.argtypes = [c_void_p, c_void_p, c_void_p]
        self._api.femInitialise.restype = c_void_p

        self._api.femGetId.argtypes = [c_void_p]
        self._api.femGetId.restype = c_int

        self._api.femGetInt.argtypes = [c_void_p, c_int, c_int, c_size_t, c_void_p]
        self._api.femGetInt.restype = c_int

        self._api.femSetInt.argtypes = [c_void_p, c_int, c_int, c_size_t, c_void_p]
        self._api.femSetInt.restype = c_int

        self._api.femCmd.argtypes = [c_void_p, c_int, c_int]
        self._api.femCmd.restype = c_int

        fem_config = ExcaliburFemConfig(fem_id, fem_addr, fem_port, data_addr)
        self.fem_handle = self._api.femInitialise(None, None, byref(fem_config))

        if self.fem_handle == None:
            raise ExcaliburFemError(self._api.femErrorMsg())


    def _validate_fem_handle(self):

        if self.fem_handle == None:

            # Resolve calling function name and raise an exception
            import inspect
            calling_name = inspect.stack()[1][3]
            raise ExcaliburFemError('{}: FEM handle is not initialised'.format(calling_name))

    def close(self):

        self._validate_fem_handle()

        self._api.femClose(self.fem_handle)
        self.fem_handle = None

    def get_id(self):

        self._validate_fem_handle()
        fem_id = self._api.femGetId(self.fem_handle)

        return fem_id

    def get_int(self, chip_id, param_id, size):

        self._validate_fem_handle()

        int_vals = (c_int * size)()

        rc = self._api.femGetInt(self.fem_handle, chip_id, param_id, size, int_vals)

        #TODO decode rc and raise exception for errors rather than returning rc?
        return (rc, [int_vals[i] for i in range(size)])

    def set_int(self, chip_id, param_id, values):

        self._validate_fem_handle()

        if type(values) is list:
            size = len(values)
        else:
            size = 1
            values = [values]

        try:
            int_vals = (c_int * size)(*values)
        except TypeError as e:
            raise ExcaliburFemError('set_int: {}'.format(str(e)))

        rc = self._api.femSetInt(self.fem_handle, chip_id, param_id, size, int_vals)

        return rc

    def cmd(self, chip_id, cmd_id):

        self._validate_fem_handle()

        rc = self._api.femCmd(self.fem_handle, chip_id, cmd_id)

        return rc
