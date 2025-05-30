#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 28 16:47:10 2025

@author: kalishamay
"""

def stockAvg(dataLong,tickers,exceedPerc):
    twoHunDayAvg = {}
    sevenDayAvg = {}
    fiveDayAvg = {}
    oneHunDayAvg = {}
    fiftyDayAvg = {}
    thirtyDayAvg = {}
    long200Seven = {}
    long200Five = {}
    long100Seven = {}
    long100Five = {}
    mid50Seven = {}
    mid50Five = {}
    short30Seven = {}
    short30Five ={}
    for ticker in tickers:
        sevenDay = dataLong[ticker]['Close'][-8:-1]
        sevenDayAvg[ticker] = sevenDay.mean()
        fiveDay = dataLong[ticker]['Close'][-6:-1]
        fiveDayAvg[ticker] = fiveDay.mean()
        twoHunDay = dataLong[ticker]['Close'][-201:-1]
        twoHunDayAvg[ticker] = twoHunDay.mean()
        if twoHunDayAvg[ticker]*((100+exceedPerc)/100)<sevenDayAvg[ticker]:
            long200Seven[ticker] = "Bull"
        else:
            long200Seven[ticker] = "Bear"
        if twoHunDayAvg[ticker]*((100+exceedPerc)/100)<fiveDayAvg[ticker]:
            long200Five[ticker] = "Bull"
        else:
            long200Five[ticker] = "Bear"
        oneHunDay = dataLong[ticker]['Close'][-101:-1]
        oneHunDayAvg[ticker] = oneHunDay.mean()
        if oneHunDayAvg[ticker]*((100+exceedPerc)/100)<sevenDayAvg[ticker]:
            long100Seven[ticker] = "Bull"
        else:
            long100Seven[ticker] = "Bear"
        if oneHunDayAvg[ticker]*((100+exceedPerc)/100)<fiveDayAvg[ticker]:
            long100Five[ticker] = "Bull"
        else:
            long100Five[ticker] = "Bear"
        fiftyDay = dataLong[ticker]['Close'][-51:-1]
        fiftyDayAvg[ticker] = fiftyDay.mean()
        if fiftyDayAvg[ticker]*((100+exceedPerc)/100)<sevenDayAvg[ticker]:
            mid50Seven[ticker] = "Bull"
        else:
            mid50Seven[ticker]= "Bear"
        if fiftyDayAvg[ticker]*((100+exceedPerc)/100)<fiveDayAvg[ticker]:
            mid50Five[ticker] = "Bull"
        else:
            mid50Five[ticker] = "Bear"
        thirtyDay = dataLong[ticker]['Close'][-31:-1]
        thirtyDayAvg[ticker] = thirtyDay.mean()
        if thirtyDayAvg[ticker]*((100+exceedPerc)/100)<sevenDayAvg[ticker]:
            short30Seven[ticker] = "Bull"
        else:
            short30Seven[ticker] = "Bear"
        if thirtyDayAvg[ticker]*((100+exceedPerc)/100)<fiveDayAvg[ticker]:
            short30Five[ticker] = "Bull"
        else:
            short30Five[ticker] = "Bear"
        return long200Seven, long200Five, long100Seven, long100Five, mid50Seven, mid50Five, short30Seven, short30Five
