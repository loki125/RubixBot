import http.server
import json
import socketserver
import os
import time


# * Root() -> bool: Sets up cube in place of the device.
def root() -> bool:
    time.sleep(2)
    return True

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/uhh'):
            pass
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/Root'):
            self.call_function(root)

    def call_function(self, function, *args, **kwargs):
        """Handles requests starting with /func."""
        result = function(*args, **kwargs)
        if result is None:
            self.send_response(400) # bad request
            self.end_headers()
            return
        self.send_response(200)
        self.send_header('Content-type', 'json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

def run(port=8000):
    """Run the server on the specified port."""
    try:
        with socketserver.TCPServer(("", port), CustomHandler) as httpd:
            print(f"Serving at port {port}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Goodbye")
        httpd.server_close()

if __name__ == "__main__":
    run()