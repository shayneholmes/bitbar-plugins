#!/usr/local/bin/python3
# coding=utf-8

from PIL import Image, ImageDraw, ImageFont
import base64
from datetime import datetime
from io import BytesIO
import itertools
import os
import sys
import time
import bisect

height=15
secondsperpixel=180
timepoints_size=1 # pixels chunked together
workwindowhours=9
lookback=workwindowhours*3600
width=lookback//secondsperpixel
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

class FileSearcher(object):
    def __init__(self, file_pointer):
        self.f = file_pointer
        self.f.seek(0, os.SEEK_END)
        self.len = self.f.tell()
    def __len__(self):
        return self.len
    def __getitem__(self, item):
        self.f.seek(item)
        if (item):
            self.f.readline()
        row = self.f.readline()
        if not len(row):
            return sys.maxsize
        return int(row[0:row.find('|')])

def get_data( fileName, start_time = 0):
    arr = [(0,0)]
    with open(fileName, 'r') as f:
        # binary search for row with largest key s.t. key < start_time
        sf = FileSearcher(f)
        start = bisect.bisect_left(sf, start_time)
        f.seek(start)
        # read to the end of the file, with no intermediate readline; this will
        # start with the previous record thanks to bisect_left
        arr.extend([tuple(map(int, line.split('|')[0:2])) for line in f.readlines()])
    return arr

def get_time_points( time_points ):
    # poll over time, starting with the first data point
    inttime = int(current_time())
    earliesttime = today_start()
    timerange = lookback
    point = None
    maxtimepoint = len(time_points) - 1
    data = []
    time_step = float(timerange) / width * timepoints_size
    slice_time = earliesttime
    for i in range(width // timepoints_size):
        if point is None:
            # fast forward through time_points to the desired time
            point = bisect.bisect_right(time_points, (slice_time, 0)) - 1
        else:
            # already have an anchor point, move incrementally
            while point < maxtimepoint and time_points[point+1][0] <= slice_time:
                point += 1
        # point points to the entry that was in effect at slice_time
        assert point < 0 or time_points[point][0] <= slice_time
        assert point == maxtimepoint or time_points[point+1][0] > slice_time
        if point < 0:
            data.append(0) # not in history -> disabled
        else:
            data.append(time_points[point][1])
        slice_time += time_step
        if slice_time > inttime:
            slice_time -= day_offset
            point = None
    return data

def drawsparklines( im,draw,data ):
    win = lambda k: True if k == 1 else False
    loss = lambda k: True if k == 2 else False
    color = (0,255)
    w,h = im.size
    m = h // 2
    for i, d in enumerate(data):
        y = 0 if win(d) else h if loss(d) else m
        x = i * timepoints_size # data is as wide as the image
        draw.rectangle([(x,m),(x+timepoints_size-1,y)],fill=color)

def scalePixels( pixels, x, y ):
    return [[i for i in row for j in range(x)] for row in pixels for j in range(y)]

def drawcenterline( im, draw ):
    color = (0,255)
    lw = 1 # line width
    w, h = im.size
    y = h // 2
    draw.line([(0,y),(w,y)], fill=color, width=lw)

def blank_vertical( im, draw, x, width ):
    w,h = im.size
    draw.rectangle([(max(x,0),0),(min(x+width,w),h)], fill=(0,0))

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

def formattime(secs):
    mins = secs // 60
    if mins == 0:
        return ""
    else:
        return "{:d}:{:02d}".format(mins // 60, mins % 60)

data = get_data(getFileName(), int(current_time()) - day_offset)
time_points = get_time_points(data)
im = Image.new("LA", (width, height))
draw = ImageDraw.Draw(im)
drawsparklines(im,draw,time_points)
drawcenterline(im, draw)
blank_vertical(im, draw, int(current_time() - today_start()) // secondsperpixel + 1, blankspace)
del draw

print("| templateImage=" + base64encodeImage(im))
print("---")
print('Update | refresh=true')
print("{} transitions over {}".format(len(data), formattime(lookback)))
print("{} pixels".format(width))
