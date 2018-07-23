#!/usr/local/bin/python3
# coding=utf-8

# Potential areas for investment:
# - Implement custom timers for shorter tasks
# - Add an out-of-band timer that is separate from the main workflow one

from PIL import Image, ImageDraw
import base64
from datetime import datetime
from io import BytesIO
import os
import sys
import time

durationmultiplier=60

statusinfo = {
        0: {
            'name': 'disabled',
            'duration': 0,
            'spritedata': 'iVBORw0KGgoAAAANSUhEUgAAAA8AAAAPCAAAAAAevcqWAAAACXBIWXMAABYlAAAWJQFJUiTwAAAAB3RJTUUH4gIcEzYlKy/zdQAAABhJREFUCNdj/M+AClD5/5nQpIcanxHNfwC4oAQXpQbj4gAAAABJRU5ErkJggg==',
            },
        1: {
            'name': 'work',
            'duration': 15*durationmultiplier,
            'completionsound': 'glass',
            'spritedata': 'iVBORw0KGgoAAAANSUhEUgAAAA8AAAAPCAAAAAAevcqWAAAACXBIWXMAABYlAAAWJQFJUiTwAAAAB3RJTUUH4gMBDyYyaBGYBQAAADVJREFUCNdj/M+AClD5/5mQRf4zMDAxYKr/j8RkQjMGm3qG/1CIpJ4Bn3qoJuLVI3iMaP4DAJT/Fvy6pMB/AAAAAElFTkSuQmCC',
            },
        2: {
            'name': 'break',
            'duration': 5*durationmultiplier,
            'completionsound': 'glass',
            'spritedata': 'iVBORw0KGgoAAAANSUhEUgAAAA8AAAAPCAAAAAAevcqWAAAACXBIWXMAABYlAAAWJQFJUiTwAAAAB3RJTUUH4gIcFAANksncfwAAAC9JREFUCNdj/M+AClD5/5nQpFmQlDBC+QyMUMWMDAzo6rHphxlALf2MeNQzovkPADmXCSY5FP/rAAAAAElFTkSuQmCC',
            },
        3: {
            'name': 'completed',
            'duration': 0,
            'spritedata': 'iVBORw0KGgoAAAANSUhEUgAAAA8AAAAPCAAAAAAevcqWAAAACXBIWXMAABYlAAAWJQFJUiTwAAAAB3RJTUUH4gIcEzYlKy/zdQAAABhJREFUCNdj/M+AClD5/5nQpIcanxHNfwC4oAQXpQbj4gAAAABJRU5ErkJggg==', # same as disabled for now, could be a gold star?
            },
        }

def getfield( field, which=None ):
    if which is None:
        which = status
    if which == 3: # completed; this shouldn't happen!
        which = 0 # disabled
    return statusinfo[which][field]

def getFileName():
    return os.environ['HOME'] + '/.simple-timer'

def getstatusfile():
    return os.environ['HOME'] + '/.timer-results'

def loadStateFromFile( fileName ):
    try:
        with open(fileName) as f:
            arr = [int(x) for line in f for x in line.split('|')[0:2]][0:2]
    except:
        arr = []
    if len(arr) == 0:
        arr = [time.time(), 0]
    return arr

def elapsed_secs():
    return int(time.time() - starttime)

def duration_secs():
    return getfield('duration')

def remaining_secs():
    return max(0, duration_secs() - elapsed_secs())

def elapsed_percent():
    try:
        return min(1,max(0,elapsed_secs() / duration_secs()))
    except:
        return 0

def formattime(secs):
    if secs == 0:
        return ""
    else:
        return "{:d}:{:02d}".format(secs // 60, secs % 60)

exepath = os.path.realpath(os.path.dirname(sys.argv[0]))

def getsprite():
    return Image.open(BytesIO(base64.b64decode(getfield('spritedata'))))

def base64encodeImage( image ):
    output = BytesIO()
    image.save(output, format="PNG", dpi=(72,72))
    contents = output.getvalue()
    imgData = base64.b64encode(contents).decode("utf-8")
    return imgData

def bashcommand( param ):
    return 'bash="' + os.path.abspath(__file__) + '" param1=' + param

def write_status( timestamp, status ):
    with open(getFileName(),'w') as f:
        f.write("{:.0f}|{:d}"
            .format(
                timestamp,
                status))

def write_history( timestamp, status, name ):
    with open(getstatusfile(),'a') as f:
        f.write("{:.0f}|{:d}| {:s} - {:s}\n"
            .format(
                timestamp,
                status,
                datetime.fromtimestamp(time.time()).isoformat(),
                name))

def record_active_timer():
    write_status(time.time(), status)

def record_new_timer():
    write_history(time.time(), status, getfield('name'))

def record_completion():
    # Write the completed event at the end of the completed timer, even if it happened while we weren't running
    write_history(starttime + duration_secs(), 3, 'completed')

def complete():
    record_completion()
    command = 'osascript -e "display notification \\"Finished {}\\" with title \\"{}\\" sound name \\"{}\\"" &> /dev/null'.format(
        getfield('name'), getfield('name'), getfield('completionsound'))
    os.system(command)

def settimer( newstatus ):
    global status
    status = newstatus
    record_active_timer()

def setwork():
    settimer(1)
    record_new_timer()

def setbreak():
    settimer(2)
    record_new_timer()

def setdisabled():
    settimer(0)
    record_new_timer()

def checkforcompletion():
    if (status != 0 and status != 3) and remaining_secs() <= 0:
        complete()
        settimer(3)

commands = {
        'work': setwork,
        'break': setbreak,
        'disable': setdisabled,
        }

if len(sys.argv) > 1:
    # commands
    if commands[sys.argv[1]]:
        commands[sys.argv[1]]()
        sys.exit()

starttime, status = loadStateFromFile(getFileName())
checkforcompletion()
percent = elapsed_percent()

def drawProgressBar(draw, percent):
    x1 = width - 1 - barwidth
    x2 = width - 1
    bartop = (height - barheight) // 2
    y1, y2 = bartop, bartop + barheight - 1
    lw = 1 # line width
    color = (0,255)
    if status == 0 or status == 3:
        # simple line
        mid = (y2 + y1) // 2
        draw.line([(x1,mid),(x2,mid)], fill=color, width=lw)
    else:
        # draw outline
        for i in range(lw):
            draw.rectangle([(x1+i,y1+i),(x2-i,y2-i)],outline=color)
        pad = 2
        # fill percentage
        x1 += lw+pad
        x2 -= lw+pad
        draw.rectangle([(x1,y1+lw+pad),(int(x1 + (x2 - x1) * percent),y2-(lw+pad))],fill=color)

height = 15 # sprite is square, so width should be the same

padding = 2
barheight = 15
barwidth = 64
width = height + padding + barwidth
im = Image.new("LA", (width, height))
draw = ImageDraw.Draw(im)
drawProgressBar(draw, percent)
draw.bitmap((0,0), getsprite(), fill=(0,255))
del draw

print("| templateImage=" + base64encodeImage(im))
print("---")
print("%s (%d%%)"%(formattime(remaining_secs()),percent*100))
print('Work | terminal=false refresh=true ' + bashcommand('work'))
print('Break | terminal=false refresh=true ' + bashcommand('break'))
print('Disable | terminal=false refresh=true ' + bashcommand('disable'))
