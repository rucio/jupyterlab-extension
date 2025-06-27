# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025
# - Enrique Garcia, <enrique.garcia.garcia@cern.ch>, 2025
import requests


class RucioAPIException(Exception):
    def __init__(self, response, fallback_msg=None):
        self.response = response

        if response is not None:
            self.status_code = getattr(response, 'status_code', None)
            self.reason = getattr(response, 'reason', 'Unknown')
            self.headers = getattr(response, 'headers', {})
            self.exception_class = self.headers.get('ExceptionClass', None)
            self.exception_message = self.headers.get('ExceptionMessage', None)
            self.message = self.exception_message or response.text if hasattr(response, 'text') else 'Unknown error'
        else:
            # No response --> fallback to connection/other error message
            self.status_code = None
            self.reason = 'No Response'
            self.headers = {}
            self.exception_class = None
            self.exception_message = fallback_msg or 'Unknown error (response is None)'
            self.message = fallback_msg or 'Unknown error (response is None)'

        error_msg = (f"Rucio API request failed: {self.status_code} {self.reason}. "
                     f"Message: {self.message}")

        super().__init__(error_msg)


class RucioAuthenticationException(RucioAPIException):
    def __init__(self, response, fallback_msg=None):
        super().__init__(response, fallback_msg=fallback_msg)
        error_msg = (f"Authentication failed: {self.status_code} {self.reason}. "
                     f"Message: {self.message}")

        self.args = (error_msg, )  # the trailing comma makes error_msg a tuple to avoid wrong parsing


class RucioRequestsException(RucioAPIException):
    """
    Exception for failures at the transport layer (e.g., DNS, connection, SSL).

    This is raised when a requests.exceptions.RequestException occurs,
    meaning no valid HTTP response was received from the Rucio server.
    """

    def __init__(self, original_exception: requests.exceptions.RequestException):
        # We call the parent's __init__ but provide default values,
        # as there is no 'response' object to parse.
        super().__init__(response=None)

        # Set a generic server error status code, as no response was received.
        # 503 Service Unavailable or 500 Internal Server Error are possibilities.
        self.status_code = 503

        # Extract details from the original networking exception
        self.exception_class = original_exception.__class__.__name__
        self.exception_message = str(original_exception)

        # Create a user-friendly, high-level error message
        self.message = (f"Rucio API request failed at the transport layer: {self.exception_class} - {self.exception_message}")

        # Set the args tuple for proper exception behavior
        self.args = (self.message,)


class RucioHTTPException(RucioAPIException):
    """
    Exception for HTTP errors returned by the Rucio API.

    This is raised when a valid HTTP response is received but indicates an error (e.g., 404, 500).
    """

    def __init__(self, response: requests.Response):
        super().__init__(response)

        # Create a user-friendly error message
        error_msg = (f"Authentication failed: {self.status_code} {self.reason}. "
                     f"Message: {self.message}")

        # Set the args tuple for proper exception behavior
        self.args = (error_msg,)
