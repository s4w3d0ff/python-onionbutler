#    outil.py
#    Copyright (C) 2016  github.com/s4w3d0ff
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os.path
from csv import reader as csvreader
import json
from subprocess import Popen, PIPE
import logging

import requests
from stem.process import launch_tor_with_config
from stem.control import Controller

# url for retieving the unregistered portlist
IANAURL = 'http://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.csv'

def getAvailPorts(minport=1024):
    """
    Downloads the current iana.org port assignment csv
    Sorts the list for 'Unassigned'
    saves the port list in JSON to a local file
    returns a list of 'Unassigned' ports
    """
    # check if we have a saved port list
    if os.path.isfile('ports.json'):
        with open('ports.json') as f:
            portList = json.load(f)
            return portList
    # download the list
    else:
        logging.info("Downloading: '%s'" % IANAURL)
        logging.info("This could take awhile...")
        raw = requests.get(IANAURL)
        reader = csvreader(raw.iter_lines(), delimiter=',')
        portList = []
        logging.info("Generating portList...")
        for row in reader:
            if 'Unassigned' in row:
                if '-' in row[1]: # if port range
                    if int(row[1].split('-')[0]) > minport:
                        for i in range(
                                int(row[1].split('-')[0]),
                                int(row[1].split('-')[1])
                                ):
                            portList.append(i)
                elif int(row[1]) > minport:
                    portList.append(int(row[1]))
        logging.info("Found %s 'Unassigned' ports > %s" % (
                str(len(portList)), str(minport))
                )
        with open('ports.json', 'w+') as f:
            json.dump(portList, f, sort_keys=True, indent=4, ensure_ascii=False)
        return portList

#-------------------------------------------------------------------------------
def genTorPassHash(password):
    """	Launches a subprocess of tor to generate a hashed <password> """
    logging.info("Generating a hashed password")
    torP = Popen(
            ['tor', '--hush', '--hash-password', str(password)],
            stdout=PIPE,
            bufsize=1
            )
    try:
        with torP.stdout:
            for line in iter(torP.stdout.readline, b''):
                line = line.strip('\n')
                if "16:" not in line:
                    logging.debug(line)
                else:
                    passhash = line
        torP.wait()
        logging.info("Got hashed password")
        return passhash
    except Exception:
        raise

def startTor(controlPass, config):
    """
    Starts tor subprocess using a custom <config>,
    returns Popen and connected controller.
    """
    try:
        # start tor
        logging.info("Starting tor subprocess")
        process = launch_tor_with_config(
                config=config, 
                tor_cmd='tor', 
                completion_percent=50, 
                timeout=60, 
                take_ownership=True
                )
        logging.info("Connecting controller")
        # create controller
        control = Controller.from_port(
                address="127.0.0.1", 
                port=int(config['ControlPort'])
                )
        # auth controller
        control.authenticate(password=controlPass)
        logging.info("Connected to tor process")
        return process, control
    except Exception as e:
        logging.exception(e)
        raise e
