from http.server import BaseHTTPRequestHandler, HTTPServer

class Server(BaseHTTPRequestHandler):

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def do_GET(self):
