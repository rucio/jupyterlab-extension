# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025
# - Enrique Garcia, <enrique.garcia.garcia@cern.ch>, 2025

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
    def __init__(self, response):
        super().__init__(response)
        error_msg = (f"Authentication failed: {self.status_code} {self.reason}. "
                     f"Message: {self.message}")
        
        self.args = (error_msg, ) # the trailing comma makes error_msg a tuple to avoid wrong parsing