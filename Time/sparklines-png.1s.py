#!/usr/bin/env python
# coding=utf-8
import base64
import mmap
import png

height=16
barwidth=6

def generateSinglePixelSparklines( data ):
    pos = lambda k: 1 if k > 0 else 0
    neg = lambda k: 0 if k > 0 else 1
    return [[func(i) for i in data] for func in (pos, neg)]

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

data = [1,-1,1,-1,1,-1,1,1,1,-1]
pixels = generateSinglePixelSparklines(data)
pixels = scalePixels(pixels, barwidth, height / 2)
print("Test | templateImage=" + encodePngFromPixels(pixels))
print("---")
print(pixels)
