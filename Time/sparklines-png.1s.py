#!/usr/bin/env python
# coding=utf-8
import base64
import mmap
import os
import png

height=16
barwidth=6

def getFileName():
    return os.environ['TMPDIR'] + '/status.tmp'

def getNumbersFromFile( fileName ):
    with open(fileName) as f:
        arr = [int(x) for line in f for x in line.split()]
    return arr

def generateSinglePixelSparklines( data ):
    win = lambda k: 1 if k == 1 else 0
    loss = lambda k: 1 if k == 2 else 0
    return [[func(i) for i in data] for func in (win, loss)]

def scalePixels( pixels, x, y ):
    return [[i for i in row for j in range(x)] for row in pixels for j in range(y)]

def encodePngFromPixels( pixels ):
    lfunc = lambda k: 0
    afunc = lambda k: 255 if k > 0 else 0
    pixels = [[f(x) for x in row for f in (lfunc, afunc)] for row in pixels]
    mm = mmap.mmap(-1, 10000)
    png.from_array(pixels, 'LA').save(mm)
    size = mm.tell() + 1
    mm.seek(0)
    imgData = base64.b64encode(mm.read(size))
    return imgData

data = getNumbersFromFile(getFileName())
pixels = generateSinglePixelSparklines(data)
pixels = scalePixels(pixels, barwidth, height / 2)
print("| templateImage=" + encodePngFromPixels(pixels))
print("---")
print(data)
