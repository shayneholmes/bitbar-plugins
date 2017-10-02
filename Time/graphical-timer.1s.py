#!/usr/bin/env python
# coding=utf-8
import base64
import mmap
import os
import png
import sys
import time

height=10
barwidth=48

durationmultiplier=60

statusinfo = {
        0: {
            'name': 'disabled',
            'duration': 0,
            'sprite': [
                '000000000',
                '000000000',
                '000000000',
                '000000000',
                '000010000',
                '000000000',
                '000000000',
                '000000000',
                '000000000',
                '000000000',
                '000000000',
                ]
            },
        1: {
            'name': 'work',
            'duration': 15*durationmultiplier,
            'completionsound': 'glass',
            'sprite': [
                '011111110',
                '100000001',
                '000000000',
                '000000000',
                '101000101',
                '101010101',
                '101010101',
                '100101001',
                '100000001',
                '011111110',
                ]
            },
        2: {
            'name': 'break',
            'duration': 5*durationmultiplier,
            'completionsound': 'glass',
            'sprite': [
                '000000000',
                '011111100',
                '010000010',
                '000000000',
                '000000000',
                '000000000',
                '011111100',
                '010000010',
                '010000010',
                '011111100',
                '000000000',
                ]
            },
        }
        
def getfield( field ):
    return statusinfo[status][field]

def getFileName():
    return os.environ['TMPDIR'] + '/simple-timer'

def getstatusfile():
    return os.environ['TMPDIR'] + '/status.tmp'

def loadStateFromFile( fileName ):
    try:
        with open(fileName) as f:
            arr = [int(x) for line in f for x in line.split('|')]
    except:
        arr = [time.time(), 0]
    return arr

def elapsedseconds():
    return time.time() - starttime

def totalseconds():
    return getfield('duration')

def remainingseconds():
    return max(0, totalseconds() - elapsedseconds())

def percentageelapsed():
    try:
        return elapsedseconds() / totalseconds()
    except:
        return 0

def formattime(secs):
    if secs == 0:
        return ""
    else:
        return "{:d}:{:02d}".format(int(secs / 60), int(secs % 60))

def getsprite():
    packed = getfield('sprite')
    pixels = [[int(x) for x in row] for row in packed]
    return pixels

def generateProgressBar( percentage ):
    filledpixels = percentage * barwidth
    pixels = [[1 if filledpixels - i > 0 else 0 for i in range(barwidth)] for i in range(height)]
    if status == 0:
        pixels = addHorizontalLine(pixels, height / 2)
    else:
        pixels = fillborders(pixels)
    return pixels

def joinwithpadding( leftpixels, rightpixels, padding):
    pixels = []
    rows = min(len(leftpixels),len(rightpixels))
    for y in range(rows):
        row = []
        row += leftpixels[y]
        row += [0 for i in range(padding)]
        row += rightpixels[y]
        pixels.append(row)
    return pixels

def addHorizontalLine( pixels, y ):
    linefunc = lambda pos, target, pixel: pixel + 1 if pos == target else pixel
    pixels = [[linefunc(pos, y, pixel) for pixel in pixels[pos]] for pos in range(len(pixels))]
    return pixels

def fillborders( pixels ):
    func = lambda x, y, cur: 1 if x == 0 or x == barwidth-1 or y == 0 or y == height-1 else cur
    return [[func(x, y, pixels[y][x]) for x in range(barwidth)] for y in range(height)]

def scalePixels( pixels, x, y ):
    return [[i for i in row for j in range(x)] for row in pixels for j in range(y)]

def encodePngFromPixels( pixels ):
    lfunc = lambda k: 0
    afunc = lambda k: min(int(255 * k),255)
    pixels = [[f(x) for x in row for f in (lfunc, afunc)] for row in pixels]
    mm = mmap.mmap(-1, 10000)
    png.from_array(pixels, 'LA').save(mm)
    size = mm.tell() + 1
    mm.seek(0)
    imgData = base64.b64encode(mm.read(size))
    return imgData

def bashcommand( param ):
    return 'bash="' + os.path.abspath(__file__) + '" param1=' + param

def record_active_timer():
    os.system('echo "{:.0f}|{:d}" > {:s}'.format(time.time(), status, getFileName()))

def record_new_timer():
    os.system('echo "{:.0f}|{:d}" >> {:s}'.format(time.time(), status, getstatusfile()))

def record_completion():
    # Write the disabled event at the end of the completed timer, even if it happened while we weren't running
    os.system('echo "{:.0f}|{:d}" >> {:s}'.format(starttime + totalseconds(), 0, getstatusfile()))

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
pixels = generateProgressBar(percent)
pixels = joinwithpadding(getsprite(), pixels, 3)

print("| templateImage=" + encodePngFromPixels(pixels))
print("---")
print(formattime(remainingseconds()))
print('Work | terminal=false refresh=true ' + bashcommand('work'))
print('Break | terminal=false refresh=true ' + bashcommand('break'))
print('Disable | terminal=false refresh=true ' + bashcommand('disable'))
