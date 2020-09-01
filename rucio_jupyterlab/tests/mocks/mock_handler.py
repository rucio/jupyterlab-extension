# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

class MockHandler:
    def finish(*args, **kwargs):
        pass

    def current_user(*args, **kwargs):
        return None

    def get_json_body(*args, **kwargs):
        pass

    def get_query_argument(*args, **kwargs):
        pass

    def set_status(*args, **kwargs):
        pass
