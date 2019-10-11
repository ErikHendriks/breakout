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
from breakout import Breakout
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

Breakout.prepare()
#ohlcd = {'count': 100,'granularity': 'H1'}
#symbols = ['EUR_GBP','EUR_USD','GBP_USD']
##symbols = ['AUD_NZD','AUD_USD',\
##         'EUR_AUD','EUR_GBP','EUR_USD',\
##         'GBP_USD',\
##         'NZD_USD',\
##         'USD_CAD','USD_CHF']
##symbols = ['AUD_CAD','AUD_CHF','AUD_JPY','AUD_NZD','AUD_USD',\
##         'CAD_CHF','CAD_JPY',\
##         'CHF_JPY',\
##         'EUR_AUD','EUR_CAD','EUR_CHF','EUR_GBP','EUR_JPY','EUR_NZD','EUR_USD',\
##         'GBP_AUD','GBP_CAD','GBP_CHF','GBP_JPY','GBP_NZD','GBP_USD',\
##         'NZD_CAD','NZD_CHF','NZD_JPY','NZD_USD',\
##         'USD_CAD','USD_CHF','USD_JPY']
#
##params = {'instruments':'GBP_USD,GBP_AUD,EUR_USD,GBP_NZD,EUR_AUD,NZD_USD,EUR_NZD,AUD_USD,GBP_CAD,EUR_CAD,AUD_NZD,EUR_GBP,AUD_CAD,GBP_CHF,USD_CAD,EUR_CHF,AUD_CHF,USD_CHF'}
params = {'instruments':'AUD_CAD,AUD_CHF,AUD_JPY,AUD_NZD,AUD_USD,CAD_CHF,CAD_JPY,CHF_JPY,EUR_AUD,EUR_CAD,EUR_CHF,EUR_GBP,EUR_JPY,EUR_NZD,EUR_USD,GBP_AUD,GBP_CAD,GBP_CHF,GBP_JPY,GBP_NZD,GBP_USD,NZD_CAD,NZD_CHF,NZD_JPY,NZD_USD,NZD_USD,USD_CAD,USD_CHF,USD_JPY'}
#params = {'instruments':'EUR_GBP,EUR_USD,GBP_USD'}
##params = {'instruments':'AUD_NZD,AUD_USD,EUR_AUD,EUR_GBP,EUR_USD,GBP_USD,NZD_USD,USD_CAD,USD_CHF'}
price = PricingStream(accountID=accountID,params=params)
#
#"""
### Create lists of each period required by the functions
#"""
#bollingerKey = [15]
#cciKey = [15]
#macdKey = [15,30]
#momentumKey = [3,4,5,8,9,10]
#movingAverageKey = [30]
#paverageKey = [2]
#procKey = [12,13,14,15]
#williamsKey = [6,7,8,9,10]
#
#price = {}
#trades = {}
#buyTrades = {}
#sellTrades = {}
#bands = {}
#cci = {}
#macd = {}
#momentum = {}
#ma30 = {}
#ma50 = {}
#ma100 = {}
#paverage = {}
#proc = {}
#williams = {}

#class Brkout():


#   print(trades[symbol][2])
#   print(trades[symbol][3])
#   print(prices.high[-3:].max())
#   print(prices.low[-3:].min().item())
#   print(prices)
#   price[symbol] = prices
#   bands[symbol] = indicator.bollinger(price[symbol],bollingerKey,2)
#   cci[symbol] = indicator.cci(prices,cciKey)
#   macd[symbol] = indicator.macd(prices,macdKey)
#   momentum[symbol] = indicator.momentum(prices,momentumKey)
#   ma30[symbol] = indicator.movingAverage(price[symbol],[30])
#   ma50[symbol] = indicator.movingAverage(price[symbol],[50])
#   ma100[symbol] = indicator.movingAverage(price[symbol],[100])
#   paverage[symbol] = indicator.paverage(prices,paverageKey)
#   proc[symbol] = indicator.proc(prices,procKey)
#   williams[symbol] = indicator.williams(prices,williamsKey)

#   def strategy():

textList = []
textList.append('Oanda v20 breakout rapport at '+str(datetime.datetime.now()))
textList.append(' ')

timeout = 10800
timeout_start = time.time()
n = 0
while True:

    if n == 18:
        subject = 'Final rapport n at '+str(datetime.datetime.now())
        textList.append('Break n at '+str(datetime.datetime.now()))
        break
    elif time.time() > (timeout_start + timeout):
        subject = 'Final rapport t at '+str(datetime.datetime.now())
        textList.append('Break time at '+str(datetime.datetime.now()))
        break
#   n=18
    try:
        for p in api.request(price):
            print(p)
            if buy[p['instrument']] is None or\
               sell[p['instrument']] is None:
#               print('2 ',buy[p['instrument']])
                pass
            else:
#               print('3 ',buy[p['instrument']])
                for symbol in symbols:
##H1
                    sma30h1[symbol] = 0.0
                    candles = InstrumentsCandles(instrument=symbol,params=smaData30h1)
                    api.request(candles)
                    for close in candles.response['candles']:
                        sma30h1[symbol] += float(close['mid']['c'])
                    sma30h1[symbol] = sma30h1[symbol] / 30
#                   print('30h1  ',sma30h1[symbol])

#               for symbol in symbols:
                    sma50h1[symbol] = 0.0
                    candles = InstrumentsCandles(instrument=symbol,params=smaData50h1)
                    api.request(candles)
                    for close in candles.response['candles']:
                        sma50h1[symbol] += float(close['mid']['c'])
                    sma50h1[symbol] = sma50h1[symbol] / 50
#                   print('50h1  ',sma50h1[symbol])

#               for symbol in symbols:
                    sma100h1[symbol] = 0.0
                    candles = InstrumentsCandles(instrument=symbol,params=smaData100h1)
                    api.request(candles)
                    for close in candles.response['candles']:
                        sma100h1[symbol] += float(close['mid']['c'])
                    sma100h1[symbol] = sma100h1[symbol] / 100
#                   print('100h1    ',sma100h1[symbol])
##H2
                    sma30h2[symbol] = 0.0
                    candles = InstrumentsCandles(instrument=symbol,params=smaData30h2)
                    api.request(candles)
                    for close in candles.response['candles']:
                        sma30h2[symbol] += float(close['mid']['c'])
                    sma30h2[symbol] = sma30h2[symbol] / 30
#                   print('30h1  ',sma30h2[symbol])

#               for symbol in symbols:
                    sma50h2[symbol] = 0.0
                    candles = InstrumentsCandles(instrument=symbol,params=smaData50h2)
                    api.request(candles)
                    for close in candles.response['candles']:
                        sma50h2[symbol] += float(close['mid']['c'])
                    sma50h2[symbol] = sma50h2[symbol] / 50
#                   print('50h2  ',sma50h2[symbol])

#               for symbol in symbols:
                    sma100h2[symbol] = 0.0
                    candles = InstrumentsCandles(instrument=symbol,params=smaData100h2)
                    api.request(candles)
                    for close in candles.response['candles']:
                        sma100h2[symbol] += float(close['mid']['c'])
                    sma100h2[symbol] = sma100h2[symbol] / 100
#                   print('100h2    ',sma100h2[symbol])
##H3
                    sma30h3[symbol] = 0.0
                    candles = InstrumentsCandles(instrument=symbol,params=smaData30h3)
                    api.request(candles)
                    for close in candles.response['candles']:
                        sma30h3[symbol] += float(close['mid']['c'])
                    sma30h3[symbol] = sma30h3[symbol] / 30
#                   print('30h3  ',sma30h3[symbol])

#               for symbol in symbols:
                    sma50h3[symbol] = 0.0
                    candles = InstrumentsCandles(instrument=symbol,params=smaData50h3)
                    api.request(candles)
                    for close in candles.response['candles']:
                        sma50h3[symbol] += float(close['mid']['c'])
                    sma50h3[symbol] = sma50h3[symbol] / 50
#                   print('50h3  ',sma50h3[symbol])

#               for symbol in symbols:
                    sma100h3[symbol] = 0.0
                    candles = InstrumentsCandles(instrument=symbol,params=smaData100h3)
                    api.request(candles)
                    for close in candles.response['candles']:
                        sma100h3[symbol] += float(close['mid']['c'])
                    sma100h3[symbol] = sma100h3[symbol] / 100
#                   print('100h3    ',sma100h3[symbol])
##H4
                    sma30h4[symbol] = 0.0
                    candles = InstrumentsCandles(instrument=symbol,params=smaData30h4)
                    api.request(candles)
                    for close in candles.response['candles']:
                        sma30h4[symbol] += float(close['mid']['c'])
                    sma30h4[symbol] = sma30h4[symbol] / 30
#                   print('30h4  ',sma30h4[symbol])

#               for symbol in symbols:
                    sma50h4[symbol] = 0.0
                    candles = InstrumentsCandles(instrument=symbol,params=smaData50h4)
                    api.request(candles)
                    for close in candles.response['candles']:
                        sma50h4[symbol] += float(close['mid']['c'])
                    sma50h4[symbol] = sma50h4[symbol] / 50
#                   print('50h4  ',sma50h4[symbol])

#               for symbol in symbols:
                    sma100h4[symbol] = 0.0
                    candles = InstrumentsCandles(instrument=symbol,params=smaData100h4)
                    api.request(candles)
                    for close in candles.response['candles']:
                        sma100h4[symbol] += float(close['mid']['c'])
                    sma100h4[symbol] = sma100h4[symbol] / 100
#                   print('100h4    ',sma100h4[symbol])


                if buy[p['instrument']] is not None and\
                   sma50h1[p['instrument']] > sma100h1[p['instrument']] and\
                   sma30h1[p['instrument']] > sma50h1[p['instrument']] and\
                   sma50h2[p['instrument']] > sma100h2[p['instrument']] and\
                   sma30h2[p['instrument']] > sma50h2[p['instrument']] and\
                   float(p['asks'][0]['price']) > sma30h1[p['instrument']] and\
                   float(p['asks'][0]['price']) > float(buy[p['instrument']]):

#                   print('buy')
                    buy[p['instrument']] = None
                    sell[p['instrument']] = None
                    n+=1
                    stopLoss = float(p['asks'][0]['price']) - (risk[p['instrument']] / 2)
                    takeProfit = float(p['asks'][0]['price']) + risk[p['instrument']]

                    buyOrder = MarketOrderRequest(instrument=p['instrument'],\
                                  units=2000,\
                                  takeProfitOnFill=TakeProfitDetails(price=float(takeProfit)).data,\
                                  stopLossOnFill=StopLossDetails(price=float(stopLoss)).data)
                    r = orders.OrderCreate(accountID, data=buyOrder.data)
                    rv = api.request(r)
                    textList.append('Buy Order')
                    textList.append(buyOrder)
                    textList.append(' ')
                    subject = 'buy '+p['instrument']+' at '+str(datetime.datetime.now())
                    sendEmail(str(buyOrder),subject)

                elif sell[p['instrument']] is not None and\
                     sma50h1[p['instrument']] < sma100h1[p['instrument']] and\
                     sma30h1[p['instrument']] < sma50h1[p['instrument']] and\
                     sma50h2[p['instrument']] < sma100h2[p['instrument']] and\
                     sma30h2[p['instrument']] < sma50h2[p['instrument']] and\
                     float(p['bids'][0]['price']) < sma30h1[p['instrument']] and\
                     float(p['bids'][0]['price']) < float(sell[p['instrument']]):

#                   print('sell')
                    sell[p['instrument']] = None
                    buy[p['instrument']] = None
                    n+=1
                    stopLoss = float(p['asks'][0]['price']) + (risk[p['instrument']] / 2)
                    takeProfit = float(p['asks'][0]['price']) - risk[p['instrument']]

                    sellOrder = MarketOrderRequest(instrument=p['instrument'],\
                                  units=-2000,\
                                  takeProfitOnFill=TakeProfitDetails(price=float(takeProfit)).data,\
                                  stopLossOnFill=StopLossDetails(price=float(stopLoss)).data)
                    r = orders.OrderCreate(accountID, data=sellOrder.data)
                    rv = api.request(r)
                    textList.append('Sell Order')
                    textList.append(sellOrder)
                    textList.append(' ')
                    subject = 'sell '+p['instrument']+' at '+str(datetime.datetime.now())
                    sendEmail(str(sellOrder),subject)

                else:
#                   print(p['asks'][0]['price'],' ',n)
                    time.sleep(.100)
#                   pass

    except V20Error as e:
        # catch API related errors that may occur
        with open('/var/log/breakout.log', 'a') as LOG:
            LOG.write(str(datetime.datetime.now()) + ' V20Error: {}\n'.format(e))
        pass

    except ConnectionError as e:
        with open('/var/log/breakout.log', 'a') as LOG:
            LOG.write(str(datetime.datetime.now()) + ' Connection Error: {}\n'.format(e))
        pass

    except StreamTerminated as e:
        with open('/var/log/breakout.log', 'a') as LOG:
            LOG.write(str(datetime.datetime.now()) + ' Stopping: {}\n'.format(e))
        pass

    except Exception as e:
        with open('/var/log/breakout.log', 'a') as LOG:
            LOG.write(str(datetime.datetime.now()) + ' Exception: {}\n'.format(e))
        pass


#textList = []
#textList.append('Oanda v20 breakout rapport at '+str(datetime.datetime.now()))
#textList.append(' ')
#
#timeout = 7200
#timeout_start = time.time()
#n = 0
#while True:
#
#   if n == 9:
#       subject = 'Final rapport n at '+str(datetime.datetime.now())
#       textList.append('Break n at '+str(datetime.datetime.now()))
#       text = '\n'.join(map(str,textList))
#       sendEmail(text,subject)
#       break
#   elif time.time() > (timeout_start + timeout):
#       subject = 'Final rapport t at '+str(datetime.datetime.now())
#       textList.append('Break time at '+str(datetime.datetime.now()))
#       text = '\n'.join(map(str,textList))
#       sendEmail(text,subject)
#       break
#
#   try:
#       print(curPrice)
#       for p in api.request(curPrice):
#
#           print(p)
#           if buyTrades[p['instrument']]:
#               print(buyTrades[p['instrument']])
#               print(buyTrades[p['instrument']][0])
#               print(buyTrades[p['instrument']][1])
#               print(buyTrades[p['instrument']][2])
#               print(buyTrades[p['instrument']][3])
#               buy = float(p['bids'][0]['price'])
#               print('buy',buy)
#               if buy > buyTrades[p['instrument']][0]:
#                   if buyTrades[p['instrument']][2] == False:
#
#                       buyTrades[p['instrument']][2] = True
#                       buyTrades[p['instrument']][3] = False
#                       time.sleep(0.01)
#                       print('buy check 1')
#                       print(p['instrument'])
#                       print(buyTrades[p['instrument']])
#
#                   elif buyTrades[p['instrument']][2] == True\
#                   and buyTrades[p['instrument']][3] == False:
#
#                       buyTrades[p['instrument']][3] = True
#                       time.sleep(0.01)
#                       print('buy check 2')
#                       print(p['instrument'])
#                       print(buyTrades[p['instrument']])
#
#                   elif buyTrades[p['instrument']][3] == True\
#                   and buyTrades[p['instrument']][2] == True:
#
#                       stopLoss = float(p['asks'][0]['price']) - 0.002
#                       takeProfit = float(p['asks'][0]['price']) + 0.004
#
#                       buyOrder = MarketOrderRequest(instrument=p['instrument'],\
#                                     units=2000,\
#                                     takeProfitOnFill=TakeProfitDetails(price=float(takeProfit)).data,\
#                                     stopLossOnFill=StopLossDetails(price=float(stopLoss)).data)
#                       r = orders.OrderCreate(accountID, data=buyOrder.data)
#                       rv = api.request(r)
#                       textList.append('Buy Order')
#                       textList.append(buyOrder)
#                       textList.append(' ')
#                       textList.append(rv)
#                       textList.append(' ')
#                       subject = 'buy '+p['instrument']+' at '+str(datetime.datetime.now())
#                       sendEmail(str(buyOrder),subject)
#                       sendEmail(str(rv),subject)
#                       del buyTrades[p['instrument']]
#                       n+=1
#                       print('buy ')
#                       print(p['instrument'])
#                       print(buyTrades[p['instrument']])
#
#           elif sellTrade['symbol']:
#               print(sellTrades[p['instrument']])
#               print(sellTrades[p['instrument']][0])
#               print(sellTrades[p['instrument']][1])
#               print(sellTrades[p['instrument']][2])
#               print(sellTrades[p['instrument']][3])
#               sell = float(p['asks'][0]['price'])
#
#               if sell < sellTrades[p['instrument']][1]:
#                   if sellTrades[p['instrument']][3] == False:
#
#                       sellTrades[p['instrument']][3] = True
#                       sellTrades[p['instrument']][2] = False
#                       time.sleep(0.01)
#                       print('sell check 1')
#                       print(p['instrument'])
#                       print(sellTrades[p['instrument']])
#
#                   elif sellTrades[p['instrument']][3] == True\
#                   and sellTrades[p['instrument']][2] == False:
#
#                       sellTrades[p['instrument']][2] = True
#                       time.sleep(0.01)
#                       print('sell check 2')
#                       print(p['instrument'])
#                       print(sellTrades[p['instrument']])
#
#                   elif sellTrades[p['instrument']][2] == True\
#                   and sellTrades[p['instrument']][3] == True:
#
#                       stopLoss = float(p['bids'][0]['price']) + 0.002
#                       takeProfit = float(p['bids'][0]['price']) - 0.004
#
#                       sellOrder = MarketOrderRequest(instrument=p['instrument'],\
#                                     units=-2000,\
#                                     takeProfitOnFill=TakeProfitDetails(price=float(takeProfit)).data,\
#                                     stopLossOnFill=StopLossDetails(price=float(stopLoss)).data)
#                       r = orders.OrderCreate(accountID, data=sellOrder.data)
#                       rv = api.request(r)
#                       textList.append('Sell Order')
#                       textList.append(sellOrder)
#                       textList.append(' ')
#                       textList.append(rv)
#                       textList.append(' ')
#                       subject = 'sell '+p['instrument']+' at '+str(datetime.datetime.now())
#                       sendEmail(str(sellOrder),subject)
#                       sendEmail(str(rv),subject)
#                       del sellTrades[p['instrument']]
#                       n+=1
#                       print('sell')
#                       print(p['instrument'])
#                       print(sellTrades[p['instrument']])
#               else:
#                   print('nothing')
#
#
#   except V20Error as e:
#       # catch API related errors that may occur
#       with open('/var/log/breakout.log', 'a') as LOG:
#           LOG.write(str(datetime.datetime.now()) + ' V20Error: {}\n'.format(e))
#       print(e)
#       pass
#
#   except ConnectionError as e:
#       with open('/var/log/breakout.log', 'a') as LOG:
#           LOG.write(str(datetime.datetime.now()) + ' Connection Error: {}\n'.format(e))
#       print(e)
#       pass
#
#   except StreamTerminated as e:
#       with open('/var/log/breakout.log', 'a') as LOG:
#           LOG.write(str(datetime.datetime.now()) + ' Stopping: {}\n'.format(e))
#       print(e)
#       pass
#
#   except Exception as e:
#       with open('/var/log/breakout.log', 'a') as LOG:
#           LOG.write(str(datetime.datetime.now()) + ' Exception: {}\n'.format(e))
##              print(e)
#       pass
#
#
##Brkout.strategy()

text = '\n'.join(map(str,textList))
#subject = 'subject'
sendEmail(text,subject)

#print('price ',price)
#print('banda ',bands)
#print('cci ',cci)
#print('macd ',macd)
#print('momentum ',momentum)
#print('ma30 ',ma30)
#print('ma50 ',ma50)
#print('ma100 ',ma100)
#print('paverage ',paverage)
#print('proc ',proc)
#print('williams ',williams)

#print(ma50['EUR_USD']['close'].values[-1])

#print(bands)
#bollingerDict = indicator.bollinger(prices,bollingerKey,2)
#cciDict = indicator.cci(prices,cciKey)
#macdDict = indicator.macd(prices,macdKey)
#momentumDict = indicator.momentum(prices,momentumKey)
#movingAverageDict = indicator.movingAverage(prices,movingAverageKey)
#paverageDict = indicator.paverage(prices,paverageKey)
#procDict = indicator.proc(prices,procKey)
#williamsDict = indicator.williams(prices,williamsKey)

#macd = indicator.macd(prices,macdKey)
#bands = indicator.bollinger(prices,bollingerKey,2)
#cci = indicator.cci(prices,cciKey)
#print(indicator.movingAverage(prices,movingAverageKey))

#for symbol in symbols:
#   print(indicator.bollinger(price[symbol],bollingerKey,2))

#print(bands[15]['upper'].values[-2])

