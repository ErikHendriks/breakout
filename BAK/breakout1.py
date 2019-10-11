#!/usr/bin/env python3

import datetime
import numpy as np
import pandas as pd
import time

from indicators import indicator
from oandapyV20 import API
from oandapyV20.endpoints.instruments import InstrumentsCandles
from oandapyV20.endpoints.pricing import PricingStream
from oandapyV20.exceptions import V20Error, StreamTerminated
from pandas.io.json import json_normalize
from sendInfo import sendEmail

conf = [line.strip('\n') for line in open('/etc/breakout/conf.v20')]
accountID = conf[0]
api = API(access_token = conf[1],\
          environment = conf[2])

textList = []
textList.append('Oanda v20 test rapport at '+str(datetime.datetime.now()))
textList.append(' ')

symbols = ['EUR_GBP','EUR_USD','GBP_USD']
ohlcd = {'count': 50,'granularity': 'H1'}

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

n = 3
for symbol in symbols:
    trades[symbol] = []
    candle = InstrumentsCandles(instrument=symbol,params=ohlcd)
    api.request(candle)

    prices = pd.DataFrame.from_dict(json_normalize(candle.response['candles']))
    prices.time = pd.to_datetime(prices.time)
    prices = prices.set_index(prices.time)
    prices.columns = [['complete','close','high','low','open','time','volume']]

    for column in ['close','high','low','open']:
        prices[column] = prices[column].astype(float)

    trades[symbol].append(prices.high[-3:].max().item() + 0.0005)
    trades[symbol].append(prices.low[-3:].min().item() - 0.0005)
    trades[symbol].append(False)
    trades[symbol].append(False)
    n-=1
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


#params = {'instruments':'GBP_USD,GBP_AUD,EUR_USD,GBP_NZD,EUR_AUD,NZD_USD,EUR_NZD,AUD_USD,GBP_CAD,EUR_CAD,AUD_NZD,EUR_GBP,AUD_CAD,GBP_CHF,USD_CAD,EUR_CHF,AUD_CHF,USD_CHF'}
#params = {'instruments':'AUD_CAD,AUD_CHF,AUD_JPY,AUD_NZD,AUD_USD,CAD_CHF,CAD_JPY,CHF_JPY,EUR_AUD,EUR_CAD,EUR_CHF,EUR_GBP,EUR_JPY,EUR_NZD,EUR_USD,GBP_AUD,GBP_CAD,GBP_CHF,GBP_JPY,GBP_NZD,GBP_USD,NZD_CAD,NZD_CHF,NZD_JPY,NZD_USD,NZD_USD,USD_CAD,USD_CHF,USD_JPY'}
params = {'instruments':'EUR_GBP,EUR_USD,GBP_USD'}
prices = PricingStream(accountID=accountID,params=params)


textList = []
textList.append('Oanda v20 breakout rapport at '+str(datetime.datetime.now()))
textList.append(' ')

timeout = 7200
timeout_start = time.time()
while True:

    if n == 3:
        subject = 'Final rapport n at '+str(datetime.datetime.now())
        textList.append('Break n at '+str(datetime.datetime.now()))
        break
    elif time.time() > (timeout_start + timeout):
        subject = 'Final rapport t at '+str(datetime.datetime.now())
        textList.append('Break time at '+str(datetime.datetime.now()))
        break

    try:
        for p in api.request(prices):

            if not trades[p['instrument']]:
                pass
            else:
                buy = float(p['asks'][0]['price'])
                sell = float(p['bids'][0]['price'])
                if buy > trades[p['instrument']][0]:
                    if trades[p['instrument']][2] == False:

                        trades[p['instrument']].remove(2)
                        trades[p['instrument']].insert(2,True)
                        trades[p['instrument']].remove(3)
                        trades[p['instrument']].insert(3,False)
                        time.sleep(.100)

                    elif trades[p['instrument']][2] == True\
                    and trades[p['instrument']][3] == False:
                        trades[p['instrument']].remove(3)
                        trades[p['instrument']].insert(3,True)
                        time.sleep(.100)

                    elif trades[p['instrument']][3] == True\
                    and trades[p['instrument']][2] == True:

                        stopLoss = p['asks'][0]['price'] - 0.0025
                        takeProfit = p['asks'][0]['price'] + 0.005

                        buyOrder = MarketOrderRequest(instrument=p['instrument'],\
                                      units=2000,\
                                      takeProfitOnFill=TakeProfitDetails(price=float(takeProfit)).data,\
                                      stopLossOnFill=StopLossDetails(price=float(stopLoss)).data)
                        r = orders.OrderCreate(accountID, data=buyOrder.data)
                        rv = api.request(r)
                        textList.append('Buy Order')
                        textList.append(buyOrder)
                        textList.append(' ')
                        textList.append(rv)
                        textList.append(' ')
                        subject = 'buy '+p['instrument']+' at '+str(datetime.datetime.now())
                        sendEmail(str(buyOrder),subject)
                        sendEmail(str(rv),subject)
                        del trades[p['instrument']]
                        n+=1

                    else:
                        trades[p['instrument']].remove(2)
                        trades[p['instrument']].insert(2,False)
                        trades[p['instrument']].remove(3)
                        trades[p['instrument']].insert(3,False)
                        time.sleep(.100)

                elif sell < trades[p['instrument']][1]:
                    if trades[p['instrument']][3] == False:

                        trades[p['instrument']].remove(3)
                        trades[p['instrument']].insert(3,True)
                        trades[p['instrument']].remove(2)
                        trades[p['instrument']].insert(2,False)
                        time.sleep(.100)

                    elif trades[p['instrument']][3] == True\
                    and trades[p['instrument']][2] == False:
                        trades[p['instrument']].remove(2)
                        trades[p['instrument']].insert(2,True)
                        time.sleep(.100)

                    elif trades[p['instrument']][2] == True\
                    and trades[p['instrument']][3] == True:

                        stopLoss = p['bids'][0]['price'] + 0.0025
                        takeProfit = p['bids'][0]['price'] - 0.005

                        sellOrder = MarketOrderRequest(instrument=p['instrument'],\
                                      units=-2000,\
                                      takeProfitOnFill=TakeProfitDetails(price=float(takeProfit)).data,\
                                      stopLossOnFill=StopLossDetails(price=float(stopLoss)).data)
                        r = orders.OrderCreate(accountID, data=sellOrder.data)
                        rv = api.request(r)
                        textList.append('Sell Order')
                        textList.append(sellOrder)
                        textList.append(' ')
                        textList.append(rv)
                        textList.append(' ')
                        subject = 'sell '+p['instrument']+' at '+str(datetime.datetime.now())
                        sendEmail(str(sellOrder),subject)
                        sendEmail(str(rv),subject)
                        del trades[p['instrument']]
                        n+=1

                    else:
                        trades[p['instrument']].remove(2)
                        trades[p['instrument']].insert(2,False)
                        trades[p['instrument']].remove(3)
                        trades[p['instrument']].insert(3,False)
                        time.sleep(.100)

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

text = '\n'.join(map(str,textList))
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

