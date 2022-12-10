import socket
import yaml
import sys 
import os
import random

def restart_service():
    print('restarting systemd service')
    os.system('systemctl restart omicron')

with open("config.yaml", 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

for arg in sys.argv[1:]:
    if arg == 'rnd-port':
        with open("config.yaml", 'w') as f:
            config['port'] = random.randint(20000, 65000)
            yaml.dump(config, f)
            print('new config:', config)
            restart_service()
    elif arg == 'restart':
        restart_service()
    else:
        if arg == 'show':
            os.system('eog -f "$HOME"/projects/time_tracker_omicron/plots/ &')
        with socket.socket() as sock:
            sock.connect((config['ip'], config['port']))
            sock.send(arg.encode())
            data = sock.recv(1024)
            print(data.decode('UTF-8'))