#!/usr/local/bin/python3
# coding=utf-8

# Potential areas for investment:
# - Implement custom timers for shorter tasks
# - Add an out-of-band timer that is separate from the main workflow one

from PIL import Image, ImageDraw, ImageFont
import base64
from datetime import datetime
from io import BytesIO
import itertools
import numpy as np
import os
import sys
import time

durationmultiplier=60

statusinfo = {
        0: {
            'name': 'disabled',
            'label': '',
            'duration': 0,
            'spritefile': 'disabled.png',
            'sprite': [
                '00000000000',
                '00000000000',
                '00000000000',
                '00000000000',
                '00000000000',
                '00011111000',
                '00000000000',
                '00000000000',
                '00000000000',
                '00000000000',
                '00000000000',
                ]
            },
        1: {
            'name': 'work',
            'label': 'w',
            'duration': 15*durationmultiplier,
            'completionsound': 'glass',
            'spritefile': 'work.png',
            'sprite': [
                '00111111100',
                '01000000010',
                '10010001001',
                '10010001001',
                '10010001001',
                '10010101001',
                '10010101001',
                '10010101001',
                '10001010001',
                '01000000010',
                '00111111100',
                ]
            },
        2: {
            'name': 'break',
            'label': 'b',
            'duration': 5*durationmultiplier,
            'completionsound': 'glass',
            'spritefile': 'break.png',
            'sprite': [
                '00111111100',
                '01000000010',
                '10011110001',
                '10010001001',
                '10010001001',
                '10011110001',
                '10010001001',
                '10010001001',
                '10011110001',
                '01000000010',
                '00111111100',
                ]
            },
        }
        
def getfield( field, which=-1 ):
    if which == -1:
        which = status
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

def elapsedseconds():
    return int(time.time() - starttime)

def totalseconds():
    return getfield('duration')

def remainingseconds():
    return max(0, totalseconds() - elapsedseconds())

def percentageelapsed():
    try:
        return min(1,max(0,elapsedseconds() / totalseconds()))
    except:
        return 0

def formattime(secs):
    if secs == 0:
        return ""
    else:
        return "{:d}:{:02d}".format(secs // 60, secs % 60)

exepath = os.path.realpath(os.path.dirname(sys.argv[0]))

def getsprite():
    # return Image.open(exepath + '/graphical-timer/' + getfield('spritefile'))
    packed = getfield('sprite')
    pixels = [[int(x) for x in row] for row in packed]
    w,h = len(packed[0]),len(packed)
    return Image.frombytes(mode='1', size=(w,h), data=np.packbits(pixels, axis=1))
    return Image.fromarray(np.asarray(pixels), "L")

def expandtosize( pixels, w, h ):
    currenth = len(pixels)
    currentw = len(pixels[0])
    newh = max(h, currenth)
    neww = max(w, currentw)
    paddingtop = (newh - currenth) // 2
    paddingbottom = (newh - currenth - paddingtop)
    paddingleft = (neww - currentw) // 2
    paddingright = (neww - currentw - paddingleft)
    paddedpixels = []
    paddedpixels += itertools.repeat(itertools.repeat(0,neww), paddingtop)
    for i in range(currenth):
        row = []
        row += itertools.repeat(0, paddingleft)
        row += pixels[i]
        row += itertools.repeat(0, paddingright)
        paddedpixels.append(row)
    paddedpixels += itertools.repeat(itertools.repeat(0,neww), paddingbottom)
    return paddedpixels

def base64encodeImage( image ):
    output = BytesIO()
    image.save(output, format="PNG", dpi=(72,72))
    # image.save("../out.png", format="PNG", dpi=(144,144))
    contents = output.getvalue()
    # output.close()
    size = output.tell() + 1
    output.seek(0)
    imgData = base64.b64encode(contents).decode("utf-8")
    return imgData

def bashcommand( param ):
    return 'bash="' + os.path.abspath(__file__) + '" param1=' + param

def write_status( timestamp, status ):
    os.system('echo "{:.0f}|{:d}" > {:s}'
            .format(
                timestamp,
                status,
                getFileName()))

def write_result( timestamp, status, name ):
    os.system('echo "{:.0f}|{:d}| {:s} - {:s}" >> {:s}'
            .format(
                timestamp,
                status,
                datetime.fromtimestamp(time.time()).isoformat(),
                name,
                getstatusfile()))

def record_active_timer():
    write_status(time.time(), status)

def record_new_timer():
    write_result(time.time(), status, getfield('name', status))

def record_completion():
    # Write the disabled event at the end of the completed timer, even if it happened while we weren't running
    write_result(starttime + totalseconds(), 0, 'completed')

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
    if status != 0 and remainingseconds() <= 0:
        complete()
        settimer(0)

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
percent = percentageelapsed()

def drawProgressBar(draw, percent):
    x1 = width - 1 - barwidth
    x2 = width - 1
    bartop = (height - barheight) // 2
    y1, y2 = bartop, bartop + barheight - 1
    lw = 1 # line width
    color = (0,255)
    if status == 0:
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

def drawLabel(draw):
    label = getfield('label')
    font = ImageFont.truetype("/System/Library/Fonts/HelveticaNeueDeskInterface.ttc", size=24)
    draw.text((128,0), label, font=font, fill=(0,255))

height = 15 # sprite is square, so width should be the same
sprite_height = 11

padding = 2
barheight = 13
barwidth = 64
width = height + padding + barwidth
im = Image.new("LA", (width, height))
draw = ImageDraw.Draw(im)
drawProgressBar(draw, percent)
# drawLabel(draw)
draw.bitmap((0,(height-sprite_height)//2), getsprite(), fill=(0,255))
del draw

print("| templateImage=" + base64encodeImage(im))
print("---")
print("%s (%d%%)"%(formattime(remainingseconds()),percent*100))
print('Work | terminal=false refresh=true ' + bashcommand('work'))
print('Break | terminal=false refresh=true ' + bashcommand('break'))
print('Disable | terminal=false refresh=true ' + bashcommand('disable'))
