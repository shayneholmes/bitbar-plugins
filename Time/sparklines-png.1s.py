#!/usr/bin/env python
# coding=utf-8
import base64
import mmap
import os
import png
import sys
import time

height=16
secondsperpixel=120
width=180
# workday length
lookback=width*secondsperpixel

def getFileName():
    return os.environ['TMPDIR'] + '/status.tmp'

def get_data( fileName ):
    arr = [[time.time()-lookback*2,0]]
    with open(fileName) as f:
        arr += [[int(x) for x in line.split('|')] for line in f]
    return arr

def get_time_points( time_points ):
    # poll over time, starting with the first data point
    inttime = int(time.time())
    earliesttime = inttime - lookback - (inttime % secondsperpixel)
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
        data.append(time_points[point - 1][1])
        slice_time += time_step
    return data

def generateSinglePixelSparklines( data ):
    win = lambda k: 1 if k == 1 else 0
    loss = lambda k: 1 if k == 2 else 0
    return [[func(i) for i in data] for func in (win, loss)]

def scalePixels( pixels, x, y ):
    return [[i for i in row for j in range(x)] for row in pixels for j in range(y)]

def addHorizontalLine( pixels, y ):
    linefunc = lambda pos, target, pixel: pixel + 1 if pos == target else pixel
    pixels = [[linefunc(pos, y, pixel) for pixel in pixels[pos]] for pos in range(len(pixels))]
    return pixels

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
pixels = addHorizontalLine(pixels, height / 2)

print("| templateImage=" + encodePngFromPixels(pixels))
print("---")
print('Reset | terminal=false refresh=true bash="' + os.path.abspath(__file__) + '" param1=reset')
print('Update | refresh=true')
print("{} transitions over {}".format(len(data), formattime(lookback)))
print("{} pixels".format(len(pixels[0])))
