

import json
import decimal
import os
import time

from requests import get, put, post
from datetime import datetime
from copy import deepcopy
from re import sub
from string import printable
from matplotlib import pyplot
from numpy import array

from oandapysuite.endpoints import *
from oandapysuite.stats import *
from oandapysuite.exceptions import *

time_format = '%Y-%m-%dT%X'
decimal.getcontext().prec = 6
D = decimal.Decimal


class CandleCluster:
    """This class serializes JSON data received when using
    OANDAAPIObject to retreive candledata. It can be iterated
    over like a list, and each individual candle is its own
    object. The CandlesObject class is essentially a list of
    individual candle objects."""

    class Candle:
        """Serializes candle data."""
    
        def __init__(self, candledata, ins, gran):
            global time_format
            self.open = D(candledata['mid']['o'])
            self.close = D(candledata['mid']['c'])
            self.low = D(candledata['mid']['l'])
            self.high = D(candledata['mid']['h'])
            self.oc_displacement = self.close - self.open
            self.total_displacement = self.high - self.low
            self.complete = True if candledata['complete'] == 'true' else False
            self.time = datetime.strptime(candledata['time'][:-11], time_format)
            self.volume = int(candledata['volume'])
            self.gran = gran
            self.instrument = ins
            self.reversal = None
            self.is_bull = None
            self.is_bear = None
        
        def __str__(self):
            return f'<{self.time}, close: {self.close}>'

        def __repr__(self):
            return self.__str__()

    
    def __init__(self, candsjson):
            self.candledata = json.loads(candsjson)
            self.candles = []
            self.ind = 0
            self.gran = self.candledata['granularity']
            self.instrument = self.candledata['instrument'].replace('/', '_')
            for candle in self.candledata['candles']:
                self.candles.append(self.Candle(candle, self.instrument, self.gran))
            for i in range(len(self.candles)):
                if i == 0: continue
                if self.candles[i].close > self.candles[i-1].close:
                    self.candles[i].is_bull = True
                    self.candles[i].is_bear = False
                else:
                    self.candles[i].is_bull = False
                    self.candles[i].is_bear = True
                if self.candles[i].is_bull == self.candles[i-1].is_bull:
                    self.candles[i].reversal = False
                else:
                    self.candles[i].reversal = True
            self.std = standard_deviation([i.close for i in self.candles[-30:]])
    
    def __str__(self):
        return f'<{len(self.candles)} candles, time: {self.candles[0].time} thru {self.candles[-1].time}>'
    
    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        return iter(self.candles)

    def __next__(self):
        ind = self.ind
        self.ind += 1
        return ind
    
    def __getitem__(self, index):
        return self.candles[index]

    def __len__(self):
        return len(self.candles)

    def __add__(self, b):
        if not self.instrument == b.instrument:
            raise ClusterConcatException(self.instrument, b.instrument)
        if self[0].time > b[-1].time:
            result = deepcopy(b)
            for candle in self:
                result.candles.append(candle)
        elif b[0].time > self[-1].time:
            result = deepcopy(self)
            for candle in b:
                result.candles.append(candle)
        return


    def history(self, valuex=None, valuey=None):
        """Returns historic data from every `Candle` in a `CandleCluster` 
        object in the form of a list. For example, in order to get the close 
        on every candle in a CandleCluster object `x`, you would use 
        `x.history('close')`. You can also retreive historic data in the form 
        of a two dimensional tuple, by passing in your specified values for `valuex` 
        and `valuey`. All values passed in must be attributes of the `Candle` object."""

        historic_data = {'x' : [],
                         'y' : []}
        if valuex and valuey:
            for candle in self.candles:
                historic_data['x'].append(getattr(candle, valuex))
                historic_data['y'].append(getattr(candle, valuey))
            return (historic_data['x'], historic_data['y'])
        if not valuey:
            return [getattr(candle, valuex) for candle in self.candles]


class APIObject:
    """Object that allows the user to access OANDA's REST API endpoints. In order to
    initialize this class, the constructor must be passed a file URI containing the
    user's API auth token. For example, if you have it located in your documents folder,
    it would be `x = APIObject('~/Documents/auth.txt')`"""

    def get_instrument_candles(self, ins, gran, count=500, _from=None, to=None):
        """Returns a CandleCluster object containing candles with historical data. `ins` should be
        a string containing the currency pair you would like to retreive, in the form of BASE_QUOTE.
        (eg. USD_CAD). `gran` is the granularity of the candles, and should be a strong specifying
        any granularity that you would find in a typical market chart (eg. 'M1', 'M5', 'H1') etc...
        `count` is an optional variable that returns the specified number of candles. Should be an int.
        `_from` and `to` are for if you would prefer to retreive candles from a certain time range.
        These values should be an integer in the format of the UNIX epoch (seconds elapsed since 
        1 January 1970.)"""

        headers = {
            'Authorization': f'Bearer {self.auth}'
        }
        response = get(get_candle(ins, gran, count=count, _from=_from, to=to), headers=headers)
        return CandleCluster(response.text)

    def get_child_candles(self, candle, gran):
        """Returns the children candles of a specified candle at the specified granuarlity.
        For example, passing in an H1 candle from 00:00-01:00 on 1 January, using 'M1' as the
        desired child granularity, will yield a CandleCluster object containing 60 M1 candles, 
        ranging from the start of the parent candle to the end of the parent candle."""

        start = int(candle.time.timestamp()) - candlex[candle.gran]
        end = int(candle.time.timestamp())
        return self.get_instrument_candles(candle.instrument, gran, _from=start, to=end)

            

    def __init__(self, auth):
        self.auth = str(open(auth, 'r').read())
    
    @staticmethod
    def plot(x=None, y=None, style='scatter'):
        """Uses matplotlib to plot and visualize data. In order to plot
        data, x and y variables are required. To choose the format of
        the data being graphed (eg, line graph vs scatter plot), pass in
        the specified style of graphing to the keyworded argument, `style`.
        Defaults to `scatter`. `plot` is another valid and supported style.
        Horizontal and vertical lines can be graphed by passing in an x value
        for vertical lines, and using `vline` for `style`, and a y value for
        horizontal lines and using `hline` for `style`."""

        if style == 'vline':
            pyplot.axvline(x=x, color='r')
        if style == 'hline':
            pyplot.axhline(y=y, color='r')
        x = array(x)
        y = array(y)
        getattr(pyplot, style)(x, y)

    @staticmethod
    def visualize():
        """Visualizes plotted data."""
        
        pyplot.show()


                
        
        
        

