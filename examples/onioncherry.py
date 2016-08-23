#    onioncherry.py
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

from copy import copy

import cherrypy as cp
from bs4 import BeautifulSoup as BS

from onionbutler import Butler


HTML = BS("""
        <!DOCTYPE html><html>
        <head><title></title></head>
        <body><center><center></body>
        </html>""", 'html.parser')

NewOnionButton = BS("""
        <script type="text/javascript">
            function newonion() {
                alert("This can take awhile... You will be redirected automagicly!");
                window.location.href = "/genonion";
            }
        </script>
        <br><br>
        <button onclick="newonion()">New Onion!</button>
        """, 'html.parser')

ShutdownButton = BS("""
        <script type="text/javascript">
            function shutdown() {
                alert("Shutting down onions!");
                window.location.href = "/shtdwn";
                }
        </script>
        <button onclick="shutdown()">Shutdown</button>
        """, 'html.parser')

class TorContext(object):
    """Context manager so butler can shutdown gracefully"""
    def __init__(self, control=False, config=False, skeys=False, rmPortList=False):
        self.ctl=control
        self.cnf=config
        self.sky=skeys
        self.rmp=rmPortList
    def __enter__(self):
        return Butler(control=self.ctl, config=self.cnf)
    def __exit__(self, *args):
        tor.shutdown(saveKeys=self.sky,  rmPortList=self.rmp)
        return True


class Root(object):
    def __init__(self, baseonion, port):
        self.baseonion, self.basekey = baseonion
        self.httpPort = port
    
    @cp.expose
    def index(self):
        html = copy(HTML)
        html.title.string = self.baseonion.service_id+'.onion'
        html.body.center.append(BS('<h1>Available Onions!</h1>', 'html.parser'))
        for onion in tor.onions:
            html.body.center.append(BS(
                '<a href="http://'+onion+'.onion">'+onion+'.onion</a><br>', 
                'html.parser'))
        html.body.center.append(NewOnionButton)
        html.body.center.append(ShutdownButton)
        return html.prettify()

    @cp.expose
    def genonion(self):
        tor.plantOnion(self.httpPort)
        raise cp.HTTPRedirect("/")

    @cp.expose
    def shtdwn(self):
        tor.shutdown(saveKeys=True, rmPortList=False)
        raise cp.HTTPRedirect("/")

if __name__ == "__main__":
    tor = Butler():
    httpPort = tor.ports.choose()
    # set the cherrypy server port
    cp.config.update({'server.socket_port': httpPort})
    # run the application
    cp.quickstart(Root(tor.plantOnion(httpPort), httpPort), '/')

