#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Charles Guo'

#流状态定义：
notEnd=0
end=1


class Flow:
    validPacket = 0
    def __init__(self):
        self.packetNum=1
        self.startTime=0
        self.endTime=0
        self.status=notEnd
        Flow.validPacket+=1

    def addPacket(self):
        self.packetNum+=1
        Flow.validPacket+=1


