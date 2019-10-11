#!/usr/bin/env python3

import datetime
import numpy as np
import logging
import oandapyV20
import oandapyV20.endpoints.orders as orders
import pandas as pd
import pprint
import requests
import time
import urllib3

from indicators import indicator
from oandapyV20 import API
from oandapyV20.contrib.requests import *
from oandapyV20.endpoints.instruments import InstrumentsCandles
from oandapyV20.endpoints.pricing import PricingStream
from oandapyV20.exceptions import V20Error, StreamTerminated
from pandas.io.json import json_normalize
from requests.exceptions import ConnectionError
from sendInfo import sendEmail

logging.basicConfig(
    filename='/var/log/breakout.log',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s : %(message)s',)

conf = [line.strip('\n') for line in open('/etc/breakout/conf.v20')]
accountID = conf[0]
api = API(access_token = conf[1],\
          environment = conf[2])

textList = []
textList.append('Oanda v20 test rapport at '+str(datetime.datetime.now()))
textList.append(' ')

ohlcd = {'count': 100,'granularity': 'H1'}
#symbols = ['EUR_GBP','EUR_USD','GBP_USD']
#symbols = ['AUD_NZD','AUD_USD',\
#          'EUR_AUD','EUR_GBP','EUR_USD',\
#          'GBP_USD',\
#          'NZD_USD',\
#          'USD_CAD','USD_CHF']
symbols = ['AUD_CAD','AUD_CHF','AUD_JPY','AUD_NZD','AUD_USD',\
           'CAD_CHF','CAD_JPY',\
           'CHF_JPY',\
           'EUR_AUD','EUR_CAD','EUR_CHF','EUR_GBP','EUR_JPY','EUR_NZD','EUR_USD',\
           'GBP_AUD','GBP_CAD','GBP_CHF','GBP_JPY','GBP_NZD','GBP_USD',\
           'NZD_CAD','NZD_CHF','NZD_JPY','NZD_USD',\
           'USD_CAD','USD_CHF','USD_JPY']

#params = {'instruments':'GBP_USD,GBP_AUD,EUR_USD,GBP_NZD,EUR_AUD,NZD_USD,EUR_NZD,AUD_USD,GBP_CAD,EUR_CAD,AUD_NZD,EUR_GBP,AUD_CAD,GBP_CHF,USD_CAD,EUR_CHF,AUD_CHF,USD_CHF'}
#params = {'instruments':'AUD_CAD,AUD_CHF,AUD_JPY,AUD_NZD,AUD_USD,CAD_CHF,CAD_JPY,CHF_JPY,EUR_AUD,EUR_CAD,EUR_CHF,EUR_GBP,EUR_JPY,EUR_NZD,EUR_USD,GBP_AUD,GBP_CAD,GBP_CHF,GBP_JPY,GBP_NZD,GBP_USD,NZD_CAD,NZD_CHF,NZD_JPY,NZD_USD,NZD_USD,USD_CAD,USD_CHF,USD_JPY'}
params = {'instruments':'EUR_GBP,EUR_USD,GBP_USD'}
#params = {'instruments':'AUD_NZD,AUD_USD,EUR_AUD,EUR_GBP,EUR_USD,GBP_USD,NZD_USD,USD_CAD,USD_CHF'}
curPrice = PricingStream(accountID=accountID,params=params)

"""
## Create lists of each period required by the functions
"""
bollingerKey = [15]
cciKey = [15]
macdKey = [15,30]
momentumKey = [3,4,5,8,9,10]
movingAverageKey = [30]
paverageKey = [2]
procKey = [12,13,14,15]
williamsKey = [6,7,8,9,10]

price = {}
trades = {}
buyTrades = {}
sellTrades = {}
bands = {}
cci = {}
macd = {}
momentum = {}
ma30 = {}
ma50 = {}
ma100 = {}
paverage = {}
proc = {}
williams = {}

class Breakout():

    def prepare():
        for symbol in symbols:
            trades[symbol] = []
            candle = InstrumentsCandles(instrument=symbol,params=ohlcd)
            print(candle)
            api.request(candle)

#           pprint.pprint(candle.response['candles'])
            prices = pd.DataFrame.from_dict(json_normalize(candle.response['candles']))
            prices.time = pd.to_datetime(prices.time)
            prices = prices.set_index(prices.time)
            prices.columns = [['complete','close','high','low','open','time','volume']]

            for column in ['close','high','low','open']:
                prices[column] = prices[column].astype(float)

            print(prices)

            ma30[symbol] = indicator.movingAverage(prices,[30])
            ma50[symbol] = indicator.movingAverage(prices,[50])
            ma100[symbol] = indicator.movingAverage(prices,[100])
            print(ma100[symbol])
            print(ma30[symbol].ix[-3:].values[0][0])
            if ma30[symbol].ix[-1:].values[0][0] > ma50[symbol].ix[-1:].values[0][0]\
            and ma50[symbol].ix[-1:].values[0][0] > ma100[symbol].ix[-1:].values[0][0]\
            and ma30[symbol].ix[-2:].values[0][0] > ma50[symbol].ix[-2:].values[0][0]\
            and ma50[symbol].ix[-2:].values[0][0] > ma100[symbol].ix[-2:].values[0][0]\
            and ma30[symbol].ix[-3:].values[0][0] > ma50[symbol].ix[-3:].values[0][0]\
            and ma50[symbol].ix[-3:].values[0][0] > ma100[symbol].ix[-3:].values[0][0]:

                buyTrades[symbol] = []
                buyTrades[symbol].append(prices.high[-3:].max().item() + 0.00005)
                buyTrades[symbol].append(prices.low[-3:].min().item() - 0.00005)
                buyTrades[symbol].append(False)
                buyTrades[symbol].append(False)

            if ma30[symbol].ix[-1:].values[0][0] < ma50[symbol].ix[-1:].values[0][0]\
            and ma50[symbol].ix[-1:].values[0][0] < ma100[symbol].ix[-1:].values[0][0]\
            and ma30[symbol].ix[-2:].values[0][0] < ma50[symbol].ix[-2:].values[0][0]\
            and ma50[symbol].ix[-2:].values[0][0] < ma100[symbol].ix[-2:].values[0][0]\
            and ma30[symbol].ix[-3:].values[0][0] < ma50[symbol].ix[-3:].values[0][0]\
            and ma50[symbol].ix[-3:].values[0][0] < ma100[symbol].ix[-3:].values[0][0]:

                sellTrades[symbol] = []
                sellTrades[symbol].append(prices.high[-3:].max().item() + 0.00005)
                sellTrades[symbol].append(prices.low[-3:].min().item() - 0.00005)
                sellTrades[symbol].append(False)
                sellTrades[symbol].append(False)

        textList.append('Buy Orders')
        textList.append(buyTrades)
        textList.append(' ')
        textList.append('Sell Orders')
        textList.append(sellTrades)
        textList.append(' ')
        text = '\n'.join(map(str,textList))
        subject = 'Start rapport breakout at '+str(datetime.datetime.now())
        sendEmail(text,subject)

        pprint.pprint(buyTrades, depth=4)
        return buyTrades,sellTrades

Breakout.prepare()
