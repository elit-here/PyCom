import http.server
import socketserver
import json
import subprocess
import os

PORT = 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/run':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)
            code = data['code']

            # Write code to a temporary file
            with open('temp_code.py', 'w') as f:
                f.write(code)

            # Execute the code
            try:
                result = subprocess.run(['python3', 'temp_code.py'], capture_output=True, text=True, timeout=5)
                output = result.stdout
                error = result.stderr
            except Exception as e:
                output = ''
                error = str(e)
            finally:
                os.remove('temp_code.py')

            # Send response
            response = {
                'output': output,
                'error': error
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
