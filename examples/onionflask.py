#    onionflask.py
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

from flask import Flask
from bs4 import BeautifulSoup as BS

from onionbutler import Butler

app = Flask("example")

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


@app.route('/')
def index():
    html = copy(HTML)
    html.title.string = baseonion.service_id+'.onion'
    html.body.center.append(BS('<h1>Available Onions!</h1>', 'html.parser'))
    for onion in tor.onions:
        html.body.center.append(BS(
            '<a href="http://'+onion+'.onion">'+onion+'.onion</a><br>', 
            'html.parser'))
    html.body.center.append(NewOnionButton)
    html.body.center.append(ShutdownButton)
    return html.prettify()

@app.route('/genonion')
def genonion():
    tor.plantOnion(FLASKPORT)
    raise cp.HTTPRedirect("/")

@app.route('/shtdwn')
def shtdwn():
    tor.shutdown(saveKeys=True, rmPortList=False)
    raise cp.HTTPRedirect("/")

if __name__ == '__main__':
    tor = Butler()
    FLASKPORT = tor.ports.choose()
    baseonion, basekey = tor.plantOnion(port)
    app.run(host='0.0.0.0', port=FLASKPORT)
