#!/usr/bin/env python3
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# SPDX-License-Identifier: Apache-2.0

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib, json, threading, urllib.request

PROVIDER_URL = "http://127.0.0.1:9090/ingest"

def forward(payload):
    def _():
        try:
            req = urllib.request.Request(
                PROVIDER_URL,
                json.dumps(payload).encode(),
                {"Content-Type": "application/json"},
                method="POST"
            )
            urllib.request.urlopen(req, timeout=2)
        except:
            pass
    threading.Thread(target=_, daemon=True).start()

class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        size = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(size)

        ctx = self.headers.get("X-Verification-Context", "")
        token = self.headers.get("X-Provider-Token", "")
        request_hash = hashlib.sha256(body).hexdigest()

        artifact = {
            "request_repr": request_hash,
            "verification_context": ctx,
            "provider_token": token
        }

        forward(artifact)
        self.send_response(204)
        self.end_headers()

ThreadingHTTPServer(("0.0.0.0", 8080), H).serve_forever()
