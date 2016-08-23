#python-onionbutler
https://github.com/s4w3d0ff/
onionbutler.py
##A butler, for your onions...

####TODO:
[ ] Add tor logger access
[ ] Add Butler 'shutdown' process
  [x] Disconnect Onions
  [ ] Shutdown tor Popen (if one exists)
  [ ] Encrypt any touched data dirs (without keys)
  [ ] Delete dirs
[ ] TEST!!!

###System dependancies:
    `tor` (>= 0.2.7.1)
    `python` (>= 2.7)
    `pip`

###PIP requirements:
    `stem`
    `requests`
    
__WARNING__: This project is not yet complete. It _is not secure_ and very 
buggy. __Use at your own risk!__ OnionButler was developed on linux. It should 
work with most unix systems (osx) with minimal tweaking (if any).

Docstrings have been written!
```python
help(onionbutler)
help(onionbutler.Butler)
```

##Usage:
    The `onionbutler.Butler` needs an authenticated `stem.control.Controller` in 
order to create a hidden (onion) service. By default the Butler will attempt to 
create a _new_ tor process (using a custom config, random control port, and a 
random password), this new tor process will close when the parent thread closes.

```python
import onionbutler
butler = onionbutler.Butler()
butler.plantOnion(servPort=butler.ports.choose())
print(butler.onions)
butler.plantOnion(servPort=butler.ports.choose(), pubPort=butler.ports.choose())
print(butler.onions)
```

    You can specify a custom config to pass to the tor process on init by 
defining `Butler(config=myTorConfigDict)`. The Butler will automagicly generate 
(overwrite) the `'HashedControlPassword'` key in the config dict with a random 
one. You can also leave out the `'ControlPort'` key from the config dict and a 
random port will be chosen.

    You can also pass the Butler a pre-authenticated `stem.control.Controller` 
(`Butler(control=preAuthedControl)`) and the Butler will just use that 
controller (not starting a new tor process).

    The **onionbutler** module has a submodule `onionbutler.outil` that has 
a few useful 'stand-alone' tools:

`onionbutler.outil.genTorPassHash(password)`:
    This will start a tor `subprocess.Popen` with the `--hash-password` arg and 
returns the hashed password when the subprocess completes.

`onionbutler.outil.startTor(controlPass, config)`:
    This function starts a new tor subprocess using a custom config 
(`stem.process.launch_tor_with_config`), then authenticates a new 
`stem.control.Controller` with the new tor subprocess using the 'controlPass' 
supplied. The config must (at least) have 'HashedControlPassword' and 
'ControlPort' dict keys. The 'HashedControlPassword' being the tor hash that matches 
the supplied 'controlPass'. a Popen (tor) instance and an attached/authenticated
`stem.control.Controller`.

`onionbutler.outil.getAvailPorts(minport=1024)`:
    This function will first check if a local ports.json file can be loaded, 
if it can't, it downloads the csv file from `http://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.csv` 
and sorts through it finding all the ports marked as 'Unassigned' (by default 
above port 1024). It then saves a local 'ports.json' file (because the .csv file 
is sorta large and speeds things up when called again) and then returns a list 
of the 'Unassigned' ports.

