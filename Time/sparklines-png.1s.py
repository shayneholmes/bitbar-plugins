#!/usr/local/bin/python3
# coding=utf-8

"""
Future ideas:
    * Multi-day (past days leave traces on chart, either faded or shorter)
"""

from PIL import Image, ImageDraw, ImageFont
import base64
from datetime import datetime
from io import BytesIO
import math
import os
import sys
import time
import bisect

height=15
secondsperpixel=180
timepoints_size=1 # pixels chunked together
workwindowhours=9
historydays=3 # days to look back
historydecay=0.5 # exponential decay constant (per day)
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

def add_to_tuple( old, newval ):
    # aggregate newval into a tuple
    if old is None:
        return None
    if newval == 0:
        return old
    win,loss = old
    if newval > 0 and win < newval:
        win = newval
    if newval < 0 and loss < -newval:
        loss = -newval
    return (win,loss)

def get_time_points( time_points ):
    # poll over time, starting with the first data point
    currenttime = int(current_time())
    time_step = float(lookback) / width * timepoints_size
    maxtimepoint = len(time_points) - 1
    data = [(0,0)]*(width // timepoints_size)
    now = int((currenttime - today_start()) // time_step)
    data[now:now+blankspace] = [None]*blankspace # insert blanks
    for day in range(historydays):
        daystart = today_start() - day * day_offset
        barheight = pow(historydecay,day) # will decay with each day
        point = bisect.bisect_right(time_points, (daystart, 0)) - 1
        for i in range(len(data)):
            time_of_point = daystart + i * time_step
            if time_of_point > currenttime:
                break # move to previous day
            if data[i] is None:
                continue
            while point < maxtimepoint and time_points[point+1][0] <= time_of_point:
                point += 1
            # point points to the entry that was in effect at time_of_point
            assert point < 0 or time_points[point][0] <= time_of_point
            assert point == maxtimepoint or time_points[point+1][0] > time_of_point
            if point < 0:
                val = 0 # not in history -> disabled
            else:
                timer_type = time_points[point][1]
                if timer_type == 1:
                    val = barheight # win
                elif timer_type == 2:
                    val = -barheight # loss
                else:
                    val = 0
            data[i] = add_to_tuple(data[i], val)
    return data

def drawsparklines( im,draw,data ):
    color = (0,255)
    w,h = im.size
    m = h // 2
    for i, d in enumerate(data):
        if d is not None:
            top = m - math.floor(m * d[0])
            bottom = m + math.floor(m * d[1])
            x = i * timepoints_size # data is as wide as the image
            draw.rectangle([(x,top),(x+timepoints_size-1,bottom)],fill=color)

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

data = get_data(getFileName(), int(current_time()) - day_offset * historydays)
time_points = get_time_points(data)
im = Image.new("LA", (width, height))
draw = ImageDraw.Draw(im)
drawsparklines(im,draw,time_points)
del draw

print("| templateImage=" + base64encodeImage(im))
print("---")
print('Update | refresh=true')
print("{} transitions over {}".format(len(data), formattime(lookback)))
print("{} pixels".format(width))
