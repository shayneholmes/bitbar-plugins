#!/usr/local/bin/python3
# coding=utf-8

from PIL import Image, ImageDraw, ImageFont
import base64
from datetime import datetime
from io import BytesIO
import math
import os
import sys
import time
import bisect

goal=10

height=8
boxwidth=8
boxseparation=1
fillmargin=1 # space around fill
width=goal*(boxwidth+boxseparation)+boxseparation
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

def completed_timers( time_points, target_timer_type ):
    # count number of target timers that have been successfully completed (as denoted by a completed timer after it in the file)
    completed_count = 0
    active = False
    COMPLETED_ID = 3
    for point in time_points:
        timer_type = point[1]
        if timer_type == COMPLETED_ID and active:
            completed_count = completed_count + 1
        active = (timer_type == target_timer_type)
    return completed_count

def drawBox(draw, x, filled = False):
    x1 = x
    x2 = x + boxwidth - 1
    y1 = 0
    y2 = height - 1
    color = (0,255)
    draw.rectangle([(x1,y1),(x2,y2)],outline=color)
    if filled:
        filloffset = fillmargin + 1
        x1 = x1 + filloffset
        x2 = x2 - filloffset
        y1 = y1 + filloffset
        y2 = y2 - filloffset
        draw.rectangle([(x1,y1),(x2,y2)],fill=color)

def drawBoxes(draw, completed):
    for i in range(0,goal):
        x = i * (boxwidth + boxseparation) + boxseparation
        drawBox(draw, x, i < completed)

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

data = get_data(getFileName(), int(today_start()))
WORK_TIMER_ID = 1
completed_work = completed_timers(data, WORK_TIMER_ID)
im = Image.new("LA", (width, height))
draw = ImageDraw.Draw(im)
# drawBoxes(draw,5)
drawBoxes(draw,completed_work)
del draw

print("| templateImage=" + base64encodeImage(im))
print("---")
print('Update | refresh=true')
print("{:d} timers completed".format(completed_work))
