#!/usr/bin/env python3

import datetime
import numpy as np
import numpy as np
import logging
import oandapyV20
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.orders as orders
import pandas as pd
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

params = {'instruments':'AUD_CAD,AUD_CHF,AUD_JPY,AUD_NZD,AUD_USD,CAD_CHF,CAD_JPY,CHF_JPY,EUR_AUD,EUR_CAD,EUR_CHF,EUR_GBP,EUR_JPY,EUR_NZD,EUR_USD,GBP_AUD,GBP_CAD,GBP_CHF,GBP_JPY,GBP_NZD,GBP_USD,NZD_CAD,NZD_CHF,NZD_JPY,NZD_USD,NZD_USD,USD_CAD,USD_CHF,USD_JPY'}
#params = {'instruments':'AUD_NZD,AUD_USD,EUR_AUD,EUR_GBP,EUR_USD,GBP_USD,NZD_USD,USD_CAD,USD_CHF'}
price = PricingStream(accountID=accountID,params=params)

ohlcd = {'count': 103,'granularity': 'H1'}

n1 = 0
buyTrades = {}
sellTrades = {}
ma30 = {}
ma50 = {}
ma100 = {}
atr = {}
class Breakout():

    def prepare(n1):
        for symbol in symbols:
            candle = InstrumentsCandles(instrument=symbol,params=ohlcd)
            api.request(candle)

#           pprint.pprint(candle.response['candles'])
            prices = pd.DataFrame.from_dict(json_normalize(candle.response['candles']))
            prices.time = pd.to_datetime(prices.time)
            prices = prices.set_index(prices.time)
#           print(prices)
#           prices.columns = [['complete','volume','time','open','high','low','close']]

#           print(prices)
            for column in 'mid.c','mid.h','mid.l','mid.o':
                prices[column] = prices[column].astype(float)

#           print(prices)

            atr[symbol] = indicator.atr(prices,14)
            ma30[symbol] = indicator.movingAverage(prices,[30])
            ma50[symbol] = indicator.movingAverage(prices,[50])
            ma100[symbol] = indicator.movingAverage(prices,[100])
#           print(ma100[symbol])
#           print(ma30[symbol].iloc[-3])
            if ma30[symbol].iloc[-1] > ma50[symbol].iloc[-1]\
            and ma50[symbol].iloc[-1] > ma100[symbol].iloc[-1]\
            and ma30[symbol].iloc[-2] > ma50[symbol].iloc[-2]\
            and ma50[symbol].iloc[-2] > ma100[symbol].iloc[-2]\
            and ma30[symbol].iloc[-3] > ma50[symbol].iloc[-3]\
            and ma50[symbol].iloc[-3] > ma100[symbol].iloc[-3]\
            and prices['mid.l'][-1] > ma30[symbol].iloc[-1]:

                buyTrades[symbol] = []
                buyTrades[symbol].append(round(prices['mid.h'][-3:].max().item(),5))
                buyTrades[symbol].append(round(prices['mid.l'][-3:].min().item(),5))
                buyTrades[symbol].append(False)
                buyTrades[symbol].append(False)
                n1+=1
#               print('buy')
#               print(buyTrades)

            if ma30[symbol].iloc[-1] < ma50[symbol].iloc[-1]\
            and ma50[symbol].iloc[-1] < ma100[symbol].iloc[-1]\
            and ma30[symbol].iloc[-2] < ma50[symbol].iloc[-2]\
            and ma50[symbol].iloc[-2] < ma100[symbol].iloc[-2]\
            and ma30[symbol].iloc[-3] < ma50[symbol].iloc[-3]\
            and ma50[symbol].iloc[-3] < ma100[symbol].iloc[-3]\
            and prices['mid.h'][-1] < ma30[symbol].iloc[-1]:

                sellTrades[symbol] = []
                sellTrades[symbol].append(round(prices['mid.h'][-3:].max().item(),5))
                sellTrades[symbol].append(round(prices['mid.l'][-3:].min().item(),5))
                sellTrades[symbol].append(False)
                sellTrades[symbol].append(False)
                n1+=1
#               print('sell')
#               print(sellTrades)


        textList.append('Buy Orders')
        textList.append(buyTrades)
        textList.append(' ')
        textList.append('Sell Orders')
        textList.append(sellTrades)
        textList.append(' ')
        text = '\n'.join(map(str,textList))
        subject = 'Start rapport breakout at '+str(datetime.datetime.now())
#       sendEmail(text,subject)

        print(text)
        print(n1)
        return n1,buyTrades,sellTrades

Breakout.prepare(n1)
#timeout = 10800
timeout_start = time.time()
n2 = 0
print(n2)
while True:

    if n2 == 9:
#   if n == 18:
        subject = 'Final rapport n at '+str(datetime.datetime.now())
        textList.append('Break n at '+str(datetime.datetime.now()))
        break
#   elif time.time() > (timeout_start + timeout):
#       subject = 'Final rapport t at '+str(datetime.datetime.now())
#       textList.append('Break time at '+str(datetime.datetime.now()))
#       break

    try:
#       print('ola')
        for p in api.request(price):
#           print(p['instrument'])
            if p['instrument'] in buyTrades:
#               print(buyTrades[p['instrument']])
#               print(buyTrades[p['instrument']][0])
#               print(buyTrades[p['instrument']][1])
#               print(buyTrades[p['instrument']][2])
#               print(buyTrades[p['instrument']][3])
                buy = float(p['asks'][0]['price'])
#               print('buy',buy)
                if buy > buyTrades[p['instrument']][0]:
                    print('hello')
                    if buyTrades[p['instrument']][2] == False:
                        print('privet')
#
                        buyTrades[p['instrument']][2] = True
                        buyTrades[p['instrument']][3] = False
                        time.sleep(0.01)
                        print('buy check 1')
                        print(p['instrument'])
                        print(buyTrades[p['instrument']])

                    elif buyTrades[p['instrument']][2] == True\
                    and buyTrades[p['instrument']][3] == False:

                        buyTrades[p['instrument']][3] = True
                        time.sleep(0.01)
                        print('buy check 2')
                        print(p['instrument'])
                        print(buyTrades[p['instrument']])

                    elif buyTrades[p['instrument']][3] == True\
                    and buyTrades[p['instrument']][2] == True:

                        r = accounts.AccountSummary(accountID)
                        api.request(r)

                        stopLoss = buyTrades[p['instrument']][1] - atr[p['instrument']]
                        takeProfit = buyTrades[p['instrument']][0] + (atr[p['instrument']] * 2)

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
                        del buyTrades[p['instrument']]
                        n2+=1
                        print('buy ')
                        print(p['instrument'])
                        print(buyTrades[p['instrument']])

            elif p['instrument'] in sellTrades:
#               print(sellTrades[p['instrument']])
#               print(sellTrades[p['instrument']][0])
#               print(sellTrades[p['instrument']][1])
#               print(sellTrades[p['instrument']][2])
#               print(sellTrades[p['instrument']][3])
                sell = float(p['bids'][0]['price'])

                if sell < sellTrades[p['instrument']][1]:
                    if sellTrades[p['instrument']][3] == False:

                        sellTrades[p['instrument']][3] = True
                        sellTrades[p['instrument']][2] = False
                        time.sleep(0.01)
                        print('sell check 1')
                        print(p['instrument'])
                        print(sellTrades[p['instrument']])

                    elif sellTrades[p['instrument']][3] == True\
                    and sellTrades[p['instrument']][2] == False:

                        sellTrades[p['instrument']][2] = True
                        time.sleep(0.01)
                        print('sell check 2')
                        print(p['instrument'])
                        print(sellTrades[p['instrument']])

                    elif sellTrades[p['instrument']][2] == True\
                    and sellTrades[p['instrument']][3] == True:

                        stopLoss = buyTrades[p['instrument']][1] + atr[p['instrument']]
                        takeProfit = buyTrades[p['instrument']][0] - (atr[p['instrument']] * 2)

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
                        del sellTrades[p['instrument']]
                        n2+=1
                        print('sell')
                        print(p['instrument'])
                        print(sellTrades[p['instrument']])
            else:
                pass
#               print('nothing')

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


