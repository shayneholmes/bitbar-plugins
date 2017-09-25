#!/usr/bin/env python
# coding=utf-8

# Use a string to represent the possible combinations in a trinary format: 0 is nothing, 1 is work (up), 2 is a break (down)

def encodeStatus( numberList ):
    size = len(numberList)
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
    status = u' ▝▗▘▀▚▖▞▄'
    # Range checking
    if first > 2:
        first = 0 
    if second > 2:
        second = 0 
    index = first * 3 + second
    return status[index]

print(encodeStatus([1,2,1,2,2,1,3,2])).encode('utf-8')
