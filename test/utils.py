import argparse
from sys import platform as _platform
import subprocess
from time import sleep

import os
from bs4 import BeautifulSoup
import requests
from app import app
from test.models import Jar


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', help='Set web server listening host', default='127.0.0.1')
    parser.add_argument('-P', '--port', type=int, help='Set web server listening port', default=5000)
    parser.add_argument('--db', help='Connection String to be used. (default: sqlite)',
                        default='sqlite')
    parser.add_argument('-d', '--debug', type=str.lower, help='Debug Level [info|debug]', default=None)

    return parser.parse_args()


def scrap_jars_and_save():
    page = requests.get('https://mcversions.net/')
    soup = BeautifulSoup(page.content, 'html.parser')
    for link in soup.find_all('a'):
        link_class = link.get('class')
        if type(link_class) is list and 'server' in link_class:
            parent = link.parent.parent.parent
            name = link.get('download')
            if parent.get('id') == "snapshot":
                prefix = "Snapshot "
            else:
                prefix = "Minecraft "
            inner_name = prefix + ".".join(name.split('.')[1:-1])
            Jar.get_or_create(
                name=name,
                defaults={'type': parent.get('id'),
                          'inner_name': inner_name,
                          'url': link.get('href')})


def is_online(status):
    return "online" in status


def execute(command):
    old_path = os.getcwd()
    script_path = app.config['SCRIPTS_FOLDER']

    os.chdir(script_path)
    if _platform.startswith('linux'):
        output = subprocess.check_output(command)
    elif command[1] == "status":
        output = "offline"
    elif command[1] == "start":
        sleep(3)
        output = "success"
    elif command[1] == "stop":
        sleep(10)
        output = "success"
    else:
        output = "null"
    os.chdir(old_path)
    return output


def is_name_valid(server_name):
    chars = set('/\\:*?\"<>|.')
    if any((c in chars) for c in server_name):
        return False
    elif server_name == "." or server_name == "..":
        return False
    return True
