from .endpoints import *
from numpy import diff

import decimal

decimal.getcontext().prec = 6
D = decimal.Decimal

secx = 1
minx = secx * 60
hrx = minx * 60
dayx = hrx * 24
weex = dayx * 7

candlex = {
    'S5'   : secx * 5,
    'S10'  : secx * 10,
    'S30'  : secx * 30,
    'M1'   : minx,
    'M2'   : minx * 2,
    'M4'   : minx * 4,
    'M5'   : minx * 5,
    'M10'  : minx * 10,
    'M30'  : minx * 30,
    'H1'   : hrx,
    'H2'   : hrx * 2,
    'H4'   : hrx * 4,
    'H6'   : hrx * 6,
    'H8'   : hrx * 8,
    'H12'  : hrx * 12,
    'D'    : dayx,
    'W'    : weex,
    'M'    : dayx * 30 ## problematic
}



def moving_average(data, period=10):
    mas = []
    for i in range(period):
        mas.append(None)
    for j in range(len(data)):
        if j < period: continue
        total = sum([data[k] for k in range(j-period, j)])
        mas.append(total/period)
    return mas

def standard_deviation(values):
    mean = sum(values)/len(values)
    ss = 0
    for i in values:
        ss += (i - mean) ** D(2)
    return ((ss/len(values)) ** D(0.5),mean)

def std_indicator(data, period=10):
    stds = []
    for i in range(period):
        stds.append(None)
    for j in range(len(data)):
        if j < period: continue
        std  = standard_deviation([data[k] for k in range(j-period, j)])
        stds.append(std)
    return stds






