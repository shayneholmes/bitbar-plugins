#!/usr/bin/env python
# coding=utf-8
import base64
import mmap
import os
import png
import sys
import time

height=16
secondsperpixel=60

def getFileName():
    return os.environ['TMPDIR'] + '/status.tmp'

def get_data( fileName ):
    with open(fileName) as f:
        arr = [[int(x) for x in line.split('|')] for line in f]
    if len(arr) == 0:
        arr = [[time.time()-secondsperpixel,0]]
    return arr

def get_time_points( time_points ):
    # poll over time, starting with the first data point
    earliesttime = time_points[0][0]
    point = 0
    maxtimepoint = len(time_points)
    data = []
    for slice_time in xrange(int(earliesttime), int(time.time()), secondsperpixel):
        # fast forward through time_points to the desired time
        while point < maxtimepoint and time_points[point][0] < slice_time:
            point += 1
        data.append(time_points[point - 1][1])
    return data

def generateSinglePixelSparklines( data ):
    win = lambda k: 1 if k == 1 else 0
    loss = lambda k: 1 if k == 2 else 0
    return [[func(i) for i in data] for func in (win, loss)]

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

if len(sys.argv) > 1:
    if sys.argv[1] == 'reset':
        os.system('>' + getFileName())
        sys.exit()

data = get_data(getFileName())
data = get_time_points(data)
pixels = generateSinglePixelSparklines(data)
pixels = scalePixels(pixels, 1, height / 2)

print("| templateImage=" + encodePngFromPixels(pixels))
print("---")
print(data)
print('Reset | terminal=false refresh=true bash="' + os.path.abspath(__file__) + '" param1=reset')
