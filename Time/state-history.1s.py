#!/usr/bin/env python
# coding=utf-8

# Use a string to represent the possible combinations in a trinary format: 0 is
# nothing, 1 is work (up), 2 is a break (down).
#
# Note that the first character is an underline, even though (0,0) should
# be a space. This because there's no fixed-width block space character in
# Unicode. Preserving the width seems more important than showing nothing,
# but change this to an ASCII space to show nothing for pairs of zero.
sparklinePairs = u'▁▝▗▘▀▚▖▞▄'

emptyStatusString = u"no history"

import os

def encodeStatus( numberList ):
    size = len(numberList)
    if size == 0:
        return emptyStatusString
    i = 0
    output = ''
    # Since each character encodes two elements, pad the list with
    # a zero if there are an odd number of elements
    if size % 2 == 1:
        output += encodeTwoDigits(0, numberList[i])
        i += 1
    while i < size:
        output += encodeTwoDigits(numberList[i], numberList[i+1])
        i += 2
    return output

def encodeTwoDigits( first, second ):
    # Range checking
    if first > 2:
        first = 0 
    if second > 2:
        second = 0 
    index = first * 3 + second
    return sparklinePairs[index]

def getNumbersFromFile( fileName ):
    with open(fileName) as f:
        arr = [int(x) for line in f for x in line.split()]
    return arr

def getFileName():
    return os.environ['TMPDIR'] + '/status.tmp'

print(encodeStatus(getNumbersFromFile(getFileName()))).encode('utf-8')
print('Reset | bash=echo param1=">" param2="' + getFileName() + '" terminal=false refresh=true')
