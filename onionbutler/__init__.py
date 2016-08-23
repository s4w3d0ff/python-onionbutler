#    onionbutler/__init__.py
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

import outil
import shutil
import os
import random
import json

class Porter(object):
    """
    A port management tool
        Maintains a list of used and unused ports.
    """
    def __init__(self):
        """ 
        On init we get the port list from a local file or iana.
        See onionutil.getPorts() for more info.
        self.open = list of available ports
        self.used = list of ports picked by our Porter instance.
        """
        import random
        self.open = outil.getAvailPorts()
        self.used = []
                
    def choose(self):
        """ Return a random available port. """
        port = random.choice(self.open)
        self.open.remove(port)
        self.used.append(port)
        self.used.sort()
        return port
    
    def forget(self, port):
        """ Forget a port as a 'used' port, putting it back into the pool. """
        self.used.remove(port)
        self.open.append(port)
        self.open.sort()


# ------------------------------------------------------------------------------
    
class Butler(object):
    """ An Onion Service Manager """
    def __init__(self, control=False, config=False):
        """
            In order to create onion services we need a running tor process and 
        an athenticated 'stem.controller' instance authed with the running tor
        process.
        
            The Butler can start a new tor process (and auth a controller) 
        automagicly using a custom tor config (defined by you or generated),
        or a pre-authed 'stem.controller' instance can be passed
        in the 'control' param and the Butler will use that controller to
        spawn onion services.
        
            When passing a config, the Butler will automagicly generate a
        random control password, hash the password, and insert it into the
        config. It will also gen a random control port if one is missing from
        the config.
        
            The Butler will keep track of 'planted' onion services automagicly,
        saving them in the Butler.onions variable as a dict
        
            Paramaters:
        control = 'stem.control.Controller' instance the butler uses
        config = config dict for starting tor using 'launch_tor_from_config'
        
            Attributes:
        self.ports = a random port util (see 'onionbutler.Porter')
        self.control = a 'stem.controller' used to spawn onion services
        self.process = tor 'subprocess.Popen' instance (None if not generated)
        self.config = config used to create the tor process (None if no process)
        self.onions = dict of planted onions, key is the onion.service_id
        """
        self.ports = Porter()
        self.skeys, self.rmPortList = [skeys, rmPortList]
        # We have a (hopefully authed) 'stem.controller', lets use it!
        if control:
            self.control = control
            # we have no config and no tor subprocess
            config = self.process = None
        # We don't have a control but we have a config
        elif config:
                # if we are missing a controlport we generate a random one
                if not 'ControlPort' in config:
                    config['ControlPort'] = str(self.ports.choose())
                # make a random (42 length) password (needs improvement)
                randPass = '%0x' % random.getrandbits(42 * 4)
                # generate and insert the hashed password
                config['HashedControlPassword'] = outil.genTorPassHash(randPass)
                # create process and attach control
                self.process, self.control = outil.startTor(randPass, config)
        # We have no config and no control... lets make them
        else:
            # make a random (42 length) password (needs improvement)
            randPass = '%0x' % random.getrandbits(42 * 4)
            config = {
                    'Nickname': '%0x' % random.getrandbits(8 * 4),
                    'HashedControlPassword': outil.genTorPassHash(randPass),
                    'ControlPort': str(self.ports.choose()), # random port
                    'DataDirectory': 'tortemp',
                    'ExitPolicy': 'reject *:*'
                    }
            # create process and attach control
            self.process, self.control = outil.startTor(randPass, config)
        # store config and weave an onion basket
        self.config, self.onions = [config, {}]
        
    def plantOnion(self, servPort, keyType='NEW', key='BEST', pubPort=80):
        """ 
        Creates new onion service.
            Wraps 'control.create_ephemeral_hidden_service' and adds an
        exit policy for the new hidden service. Adds the onion service to the
        self.onions dict. Returns the newly created onion service and its
        corresponding key (in a dict).
        """
        host = '0.0.0.0'
        # create the onion serv
        onionServ = self.control.create_ephemeral_hidden_service(
                {pubPort: host+':'+str(servPort)},
                key_type=keyType,
                key_content=key,
                await_publication=True
                )
        # get current exit policy
        confMap = self.control.get_conf_map("ExitPolicy")
        # if only one entry, convert to list
        if isinstance(confMap['ExitPolicy'], basestring):
            confMap['ExitPolicy'] = list(confMap['ExitPolicy'])
        # update ExitPolicy for our onion serv (if we need to)
        if 'accept *:'+str(pubPort) not in confMap['ExitPolicy']:
            # add new policy for our hidden service before last (reject *:*)
            confMap['ExitPolicy'].insert\
                    (len(confMap)-1, 'accept *:'+str(pubPort))
            # update the tor config with new policy
            self.control.set_options(confMap)
        # find our keys
        if keyType == 'NEW':
            keyType = onionServ.private_key_type
        if key == 'BEST':
            key = onionServ.private_key
        # add to our onion dict
        self.onions[onionServ.service_id] = {
                    'service': onionServ,
                    'pubport': int(pubPort),
                    'servport': int(pubPort),
                    'key': {'type': keyType, 'hash': key}
                    }
        return onionServ, {'type': keyType, 'hash': key}
        
    def pullOnion(self, onionId):
        """ Removes an onion service """
        self.control.remove_ephemeral_hidden_service(onionId)
        del self.onions[onionId]
    
    def shutdown(self, saveKeys=False, rmPortList=False):
        """ Pulls all onions """
        if saveKeys:
            keychain = []
            for onion in self.onions:
                keychain.append({onion :self.onions[onion]['key']})
            with open('keys.json', 'w+') as f:
                json.dump\
                    (keychain, f, sort_keys=True, indent=4, ensure_ascii=False)
        for onionid in [onion for onion in self.onions]:
            self.pullOnion(onionid)
        if rmPortList:
            os.remove('ports.json')
        if self.process is not None:
            try:
                self.process.kill()
            except Exception as e:
                print(e)
            else:
                shutil.rmtree(self.config['DataDirectory'])

