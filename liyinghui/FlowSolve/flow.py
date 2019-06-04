#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Charles Guo'

#流状态定义：
notEnd=0
end=1


class Flow:
    validPacket = 0
    def __init__(self):
        self.packetNum=0
        self.startTime=0
        self.endTime=0
        self.status=notEnd
        self.packetList = []
        # Flow.validPacket+=1

    def addPacket(self, index):
        self.packetNum+=1
        self.packetList.append(index)
        Flow.validPacket+=1


