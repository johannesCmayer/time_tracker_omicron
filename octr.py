import socket
import yaml
import sys 
import os
import random
import argparse
import json
import diskcache
import os
import matplotlib.pyplot as plt
import logging
import subprocess
import time

parser = argparse.ArgumentParser(
                    prog = 'omicron',
                    description = 'Visualise toggle data')
parser.add_argument('--randomize-port', action='store_true', dest="randomize_port",
                    help="Change the config to use a different port.")
parser.add_argument('--restart', action='store_true', dest="restart",
                    help="Restart the systemd service.")
parser.add_argument('-s', '--show', action='store_true', dest="show",
                    help="Fetch data, generate plots, and show them.")
parser.add_argument('-g', '--goal-group', default='all', dest="goal_group",
                    help="Which goal group to show in goal plots.")
parser.add_argument('--prompt', action='store_true', dest="prompt",
                    help="Should a UI prompt the user for a goal-group filter?")
parser.add_argument('-p', '--show-project-info', action='store_true', dest="show_project_info",
                    help="Show information about projects.")
parser.add_argument('--show-project-info-plot', action='store_true', dest="show_project_info_plot",
                    help="Show a plot with project information, including the project color.")
parser.add_argument('--clear-plots', action='store_true', dest="clear_plots",
                    help="Delete all generated plots.")
parser.add_argument('--clear-name-cache', action='store_true', dest="clear_name_cache",
                    help="Clear the name cache. Call to automatically refetch all project names. This might make the --show-project-info command produce weight output if run at the same time, as it only shows cached project info.")
parser.add_argument('--render', action='store_true', dest="render",
                    help="Just render the plots.")
parser.add_argument('--fetch', action='store_true', dest="fetch",
                    help="Just fetch new data.")
args = parser.parse_args()

with open("config.yaml", 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    
with open("goals.yaml") as f:
    goals = yaml.load(f, Loader=yaml.FullLoader)

# TODO this is duplicated in server.ipynb. Refactor
project_dir = os.path.abspath('')

project_id_names = diskcache.Cache(f"{project_dir}/project_id_names_cache.cache")
if args.clear_name_cache:
    project_id_names_cache.clear()

if args.prompt:
    p = subprocess.run(["zenity", 
                             "--entry", 
                             "--text", 'Goal group to dislpay', 
                             "--entry-text", 'all'], text=True, stdout=subprocess.PIPE)
    if p.returncode != 0:
        raise Exception(f"zenity returned {p.returncode}")
    args.goal_group = p.stdout.strip()
            
valid_goal_groups = list(goals.keys()) + ['all']
assert args.goal_group in valid_goal_groups, \
    f"Not a valid goal group: {args.goal_group}\n" + \
    f"Value must be one of {valid_goal_groups}."

# TODO this is duplicated in server.ipynb. Refactor
def project_color(project_id):
    return project_id_names[project_id]['color']
        
def restart_service():
    print('restarting systemd service')
    os.system('systemctl restart omicron')

def main():
    if args.show:
        os.system(f'eog -f "{project_dir}/plots/" &')
        time.sleep(0.1)
        
    if args.randomize_port:
        with open(f"{project_dir}/config.yaml", 'w') as f:
            config['port'] = random.randint(20000, 65000)
            yaml.dump(config, f)
            print('new config:', config)
            
    if args.restart:
        restart_service()

    if args.show_project_info or args.show_project_info_plot:
        with open(f"{project_dir}/goals.yaml") as f:
            goals = yaml.load(f, Loader=yaml.FullLoader)

        for i, k in enumerate(project_id_names):
            c = f"{k} {project_id_names[k]['name']}"
            print(c)
            if args.show_project_info_plot:
                txt = plt.text(0, i*0.2, c, color=project_color(k), size=30)
                plt.axis('off')
        if args.show_project_info_plot:
            plt.show()
        
    if args.clear_plots:
        for f in glob(f"{project_dir}/plots/*"):
            os.remove(f)
            os.mkdir(f"{project_dir}/plots")
    
    # Send Args
    if any([args.show, args.render, args.fetch]):
        try:
            with socket.socket() as sock:
                data = json.dumps(vars(args)).encode()
                logging.debug('data:', data)
                sock.connect((config['ip'], config['port']))
                sock.send(data)
                data = sock.recv(1024)
                print(data.decode('UTF-8'))
        except Exception as e:
            os.system(f'notify-send "octr: Error" "{e}"')
            raise e
            
if __name__ == '__main__':
    main()