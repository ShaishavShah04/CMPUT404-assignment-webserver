#  coding: utf-8 
from socket import socket
import socketserver
import os
from sys import path

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        # Init key global variables
        self.data = self.request.recv(1024).strip()
        method, orgRequested, httpV = self.getRequestPath(self.data)

        if method != "GET":
            self.request.send("HTTP/1.0 405\n".encode())
            return

        pathRequested = os.path.normpath(orgRequested)[1:]
        pathRequested = os.path.join(os.getcwd(), "www", pathRequested)

        redirectHeader = ""

        if (os.path.isdir(pathRequested) and pathRequested[-1] != "/"):
            pathRequested += "/"
            redirectHeader = "Content-Location: " + orgRequested + "/\n"

        
        # Default to index.html if passed in an directory
        if (os.path.isdir(pathRequested)):
            pathRequested = os.path.join(pathRequested, "index.html")

        # Return file
        if (os.path.exists(pathRequested)):
            _, ext = os.path.splitext(pathRequested)
            data = ""
            with open(pathRequested, "r") as f:
                data += f.read()
            h = self.getHeaders(200, ext[1:], len(data)) + redirectHeader
            
            self.request.send(h.encode())
            self.request.send("\n".encode())
            self.request.send(data.encode())

        else:
            
            h = "HTTP/1.0 404 FILE NOT FOUND\n"
            self.request.send(h.encode())


    def getRequestPath(self, data):
        data = data.decode("utf-8")
        return data.split("\r\n")[0].split(" ")

    def addStatusCode(self, code):
        return "HTTP/1.0 " + str(code) + "\n"

    def addFileType(self, ftype):
        return "Content-Type: text/" + ftype + "; encoding=utf8\n"

    def getHeaders(self, statusCode, ftype, l):
        h = ""
        h += self.addStatusCode(statusCode)
        h += self.addFileType(ftype)
        h += "Content-Length: " + str(l) + "\n"
        return h



if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
