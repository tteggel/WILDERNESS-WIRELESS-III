from microDNSSrv import MicroDNSSrv
import logging
import picoweb
import ure as re
from machine import Pin
#import os

import btree

# Open DB
try:
    dbf = open("messages", "r+b")
except OSError:
    dbf = open("messages", "w+b")

db = btree.open(dbf)
key = b"0"
if not b"key" in db:
    db[b"key"] = b"0"
    db.flush()
else:
    key = db[b"key"]

for _key in db:
    print("{0}: {1}".format(_key, db[_key]))

# Resolve all DNS queries to local host
MicroDNSSrv.Create({'*':'10.0.0.1'})

# Start logging
log = logging.getLogger("BIB")

# Orange LED on Pin 10 will indicate this script is running
p27 = Pin(27, Pin.OUT)
p27.value(1)

# Yellow LED on Pin 09 will blink when HTTP request is received
p33 = Pin(33, Pin.OUT)
p33.value(0)

# Need some way of interrupting this app. Use GPIO 21
#p21 = Pin(21, Pin.IN, Pin.PULL_UP)
#p21.irq(trigger=Pin.IRQ_FALLING, handler=callback)

app = picoweb.WebApp(__name__)

@app.route(re.compile('/'), methods=['GET', 'POST'])
def home(req, resp):
    global key
    if req.method == "POST":
        yield from req.read_form_data()
        if req.form.get("message"):
            print(req.form.get("message"))
            db[key] = req.form.get("message")[0]
            key = str(int(key) + 1)
            db[b"key"] = key
            db.flush()

    p33.value(1)
    yield from app.sendfile(resp, "index.html")
    yield from resp.awrite("<ol>")
    for _key in db:
        if _key != b"key":
            yield from resp.awrite("<li>")
            yield from resp.awrite(db[_key])
            yield from resp.awrite("</li>")
    yield from resp.awrite("</ol>")
    yield from resp.awrite("</body></html>")
    p33.value(0)

#def callback(p):
#    print("Received an interrupt")

app.run(debug=1, host = "10.0.0.1", port = 80)
