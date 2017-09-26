#!/usr/bin/env python
# coding=utf-8
import base64
import mmap
import png

mm = mmap.mmap(-1, 10000)

# r=png.Reader(filename='../Downloads/icon.png')
# r2=r.asRGBA()

# pixels = list(r2[2])

pixels = ['110010010011',
          '101011010100',
          '110010110101',
          '100010010011']

lfunc = lambda k: 0
afunc = lambda k: 255 if k == '1' else 0

pixels = [[f(x) for x in row for f in (lfunc, afunc)] for row in pixels]

png.from_array(pixels, 'LA').save(mm)

size = mm.tell() + 1

mm.seek(0)

img = base64.b64encode(mm.read(size))

print("Test | templateImage=" + img)
print("---")
print(pixels)
