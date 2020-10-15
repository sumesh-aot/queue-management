'''Copyright 2018 Province of British Columbia

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.'''

from pprint import pprint

from flask import g
import uuid


def print_with_requestid(value: str):
    """Print the value with unique request id per request."""

    if not value:
        return
    req_id = g.request_id if 'request_id' in g else ''
    pprint('Request ID ', req_id)

    if req_id is None:
        g.request_id = uuid.uuid4().hex
        pprint('g.request_id ', g.request_id)
        req_id = g.request_id
    pprint(f'{req_id} - {value}')
