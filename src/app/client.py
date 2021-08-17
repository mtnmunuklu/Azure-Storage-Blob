from azure.storage.common._http.httpclient import (
    _HTTPClient,
    HTTPResponse,
)
from azure.storage.common._serialization import _get_data_bytes_or_stream_only
import requests


class ExampleRawBodyReadingClient(_HTTPClient):
    def perform_request(self, request):
        '''
        Sends an HTTPRequest to Azure Storage and returns an HTTPResponse. If
        the response code indicates an error, raise an HTTPError.

        :param HTTPRequest request:
            The request to serialize and send.
        :return: An HTTPResponse containing the parsed HTTP response.
        :rtype: :class:`~azure.storage.common._http.HTTPResponse`
        '''
        # Verify the body is in bytes or either a file-like/stream object
        if request.body:
            request.body = _get_data_bytes_or_stream_only('request.body', request.body)

        # Construct the URI
        uri = self.protocol.lower() + '://' + request.host + request.path

        # Send the request
        response = self.session.request(request.method,
                                        uri,
                                        params=request.query,
                                        headers=request.headers,
                                        data=request.body or None,
                                        timeout=self.timeout,
                                        proxies=self.proxies,
                                        stream=True)

        # Parse the response
        status = int(response.status_code)
        response_headers = {}
        for key, name in response.headers.items():
            # Preserve the case of metadata
            if key.lower().startswith('x-ms-meta-'):
                response_headers[key] = name
            else:
                response_headers[key.lower()] = name

        wrap = HTTPResponse(status, response.reason, response_headers, response.raw.read())
        response.close()

        return wrap
