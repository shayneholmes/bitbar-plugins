#!/usr/bin/env python
# coding=utf-8
import base64
from datetime import datetime
import mmap
import os
import png
import sys
import time

height=10
secondsperpixel=120
width=270
# workday length
lookback=width*secondsperpixel
# one day in seconds
day_offset=86400
# blank space after now, in pixels
blankspace=5

def getFileName():
    return os.environ['HOME'] + '/.timer-results'

def current_time():
    return time.mktime(time.localtime())

def today_start():
    now = datetime.now().replace(hour=6, minute=30, second=0, microsecond=0)
    return time.mktime(now.timetuple())

def get_data( fileName ):
    arr = [[0,0]]
    with open(fileName) as f:
        arr += [[int(x) for x in line.split('|')[0:2]] for line in f]
    return arr

def get_time_points( time_points ):
    # poll over time, starting with the first data point
    inttime = int(current_time())
    earliesttime = today_start()
    timerange = lookback
    point = 0
    maxtimepoint = len(time_points)
    data = []
    time_step = float(timerange) / width
    slice_time = earliesttime
    for i in range(width):
        # fast forward through time_points to the desired time
        while point < maxtimepoint and time_points[point][0] <= slice_time:
            point += 1
        data.append(time_points[0 if point <= 0 else point - 1][1])
        slice_time += time_step
        if slice_time > inttime:
            slice_time -= day_offset
            point = 0
    return data

def generateSinglePixelSparklines( data ):
    win = lambda k: 1 if k == 1 else 0
    loss = lambda k: 1 if k == 2 else 0
    return [[func(i) for i in data] for func in (win, loss)]

def scalePixels( pixels, x, y ):
    return [[i for i in row for j in range(x)] for row in pixels for j in range(y)]

def addHorizontalLine( pixels, y ):
    for i in range(0, len(pixels[0])):
        pixels[y][i] += + 1

def blank_vertical( pixels, x, width ):
    xmax = len(pixels[0])
    for i in range(0, len(pixels)):
        for j in range(max(x,0), min(xmax,x+width)):
            pixels[i][j] = 0

def encodePngFromPixels( pixels ):
    lfunc = lambda k: 0
    afunc = lambda k: min(int(255 * k),255)
    pixels = [[f(x) for x in row for f in (lfunc, afunc)] for row in pixels]
    maxpngsize = 10000
    mm = mmap.mmap(-1, maxpngsize)
    png.from_array(pixels, 'LA').save(mm)
    size = mm.tell() + 1
    mm.seek(0)
    imgData = base64.b64encode(mm.read(size))
    return imgData

def formattime(secs):
    mins = secs / 60
    if mins == 0:
        return ""
    else:
        return "{:d}:{:02d}".format(int(mins / 60), int(mins % 60))

if len(sys.argv) > 1:
    if sys.argv[1] == 'reset':
        os.system('>' + getFileName())
        sys.exit()

data = get_data(getFileName())
time_points = get_time_points(data)
pixels = generateSinglePixelSparklines(time_points)
pixels = scalePixels(pixels, 1, height / 2)
addHorizontalLine(pixels, height / 2)
blank_vertical(pixels, int(current_time() - today_start()) / secondsperpixel + 1, blankspace)

print("| templateImage=" + encodePngFromPixels(pixels))
print("---")
print('Reset | terminal=false refresh=true bash="' + os.path.abspath(__file__) + '" param1=reset')
print('Update | refresh=true')
print("{} transitions over {}".format(len(data), formattime(lookback)))
print("{} pixels".format(len(pixels[0])))
