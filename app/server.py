from http.server import BaseHTTPRequestHandler, HTTPServer
import os, json, socket

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            body = json.dumps({"status": "healthy", "hostname": socket.gethostname()}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        body = b"""<!doctype html><html><head><title>DevOps Capstone 3</title></head>
        <body style="font-family:Arial;max-width:760px;margin:60px auto">
        <h1>Capstone Project 3: Zero-Touch Deployments</h1>
        <p>Terraform + GitHub Actions + Amazon ECS Fargate</p>
        <p>Deployment pipeline demo application.</p><p>Health endpoint: <a href="/health">/health</a></p>
        </body></html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))

port = int(os.getenv("PORT", "8080"))
HTTPServer(("0.0.0.0", port), Handler).serve_forever()
