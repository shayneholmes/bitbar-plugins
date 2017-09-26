#!/usr/bin/env python
# coding=utf-8
import base64
import mmap
import png

pixels = ['110010010011',
          '101011010100',
          '110010110101',
          '100010010011']

pixels = [[int(x) for x in row] for row in pixels]

def scalePixels( pixels, x, y ):
    return [[i for i in row for j in range(x)] for row in pixels for j in range(y)]

pixels = scalePixels(pixels, 2, 2)

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

print("Test | templateImage=" + encodePngFromPixels(pixels))
print("---")
print(pixels)
