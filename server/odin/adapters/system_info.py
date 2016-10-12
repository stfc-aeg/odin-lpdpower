"""System info adapter class for the ODIN server.

This class implements a system information adapter for the ODIN server, providing system-level
information about the system to clients.

Tim Nicholls, STFC Application Engineering
"""
import logging
import tornado

from odin.adapters.adapter import ApiAdapter, ApiAdapterResponse, request_types, response_types
from odin.adapters.parameter_tree import ParameterTree, ParameterTreeError
from odin._version import get_versions

class SystemInfoAdapter(ApiAdapter):
    """System info adapter class for the ODIN server.

    This adapter provides ODIN clients with information about the server and the system that it is
    running on.
    """

    def __init__(self, **kwargs):
        """Initialize the SystemInfoAdapter object.

        This constructor Initializes the SystemInfoAdapter object, including resolving any
        system-level information that the adapter can provide to clients subsequently.

        :param kwargs: keyword arguments specifying options
        """
        super(SystemInfoAdapter, self).__init__(**kwargs)
        self.system_info = SystemInfo()
        logging.debug('SystemInfoAdapter loaded')

    @response_types('application/json', default='application/json')
    def get(self, path, request):
        """Handle an HTTP GET request.

        This method handles an HTTP GET request, returning a JSON response.

        :param path: URI path of request
        :param request: HTTP request object
        :return: an ApiAdapterResponse object containing the appropriate response
        """
        try:
            response = self.system_info.get(path)
            status_code = 200
        except ParameterTreeError as e:
            response = {'error': str(e)}
            status_code = 400

        logging.debug(response)
        content_type = 'application/json'

        return ApiAdapterResponse(response, content_type=content_type,
                                  status_code=status_code)

    @request_types('application/json')
    @response_types('application/json', default='application/json')
    def put(self, path, request):
        """Handle an HTTP PUT request.

        This method handles an HTTP PUT request, returning a JSON response.

        :param path: URI path of request
        :param request: HTTP request object
        :return: an ApiAdapterResponse object containing the appropriate response
        """
        response = {'response': 'SystemInfoAdapter: PUT on path {}'.format(path)}
        content_type = 'application/json'
        status_code = 200

        logging.debug(response)

        return ApiAdapterResponse(response, content_type=content_type,
                                  status_code=status_code)

    def delete(self, path, request):
        """Handle an HTTP DELETE request.

        This method handles an HTTP DELETE request, returning a JSON response.

        :param path: URI path of request
        :param request: HTTP request object
        :return: an ApiAdapterResponse object containing the appropriate response
        """
        response = 'SystemInfoAdapter: DELETE on path {}'.format(path)
        status_code = 200

        logging.debug(response)

        return ApiAdapterResponse(response, status_code=status_code)

class SystemInfo(object):

    def __init__(self):

        version_info = get_versions()

        self.param_tree = ParameterTree({
            'odin_version': version_info['version'],
            'tornado_version': tornado.version
        })

    def get(self, path):

        return self.param_tree.get(path)
