import socket
import yaml
import sys 
import os

with open("config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

for arg in sys.argv[1:]:
    if arg == 'show':
        os.system('eog -f "$HOME"/projects/time_tracker_omicron/plots/ &')
    with socket.socket() as sock:
        sock.connect((config['ip'], config['port']))
        sock.send(arg.encode())
        data = sock.recv(1024)
        print(data.decode('UTF-8'))