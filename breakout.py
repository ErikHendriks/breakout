#!/usr/bin/env python3

import datetime
import json
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
    filename='/var/log/breakout2.log',
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

ohlcd = {'count': 163,'granularity': 'H1'}

buyTrades = {}
sellTrades = {}
ma30 = {}
ma50 = {}
ma100 = {}
atr = {}
class Breakout():

    def prepare():
        for symbol in symbols:
            candle = InstrumentsCandles(instrument=symbol,params=ohlcd)
            api.request(candle)

            prices = pd.DataFrame.from_dict(json_normalize(candle.response['candles']))
            prices.time = pd.to_datetime(prices.time)
            prices = prices.set_index(prices.time)
#           print(prices)

            for column in 'mid.c','mid.h','mid.l','mid.o':
                prices[column] = prices[column].astype(float)

#           print(prices)

            atr[symbol] = indicator.atr(prices,[14])
            ma30[symbol] = indicator.movingAverage(prices,[30])
            ma50[symbol] = indicator.movingAverage(prices,[50])
            ma100[symbol] = indicator.movingAverage(prices,[100])
#           print(ma100[symbol])
#           print(ma30[symbol].iloc[-3])

            buyRule1 = [[i for i in ma30[symbol].iloc[range(-5,-1)]] > [i for i in ma50[symbol].iloc[range(-5,-1)]]]
            buyRule2 = [[i for i in ma50[symbol].iloc[range(-5,-1)]] > [i for i in ma100[symbol].iloc[range(-5,-1)]]]
#           print('1 ',buyRule1)
#           print('2 ',buyRule2)

            if buyRule1[0] is True\
            and buyRule2[0] is True:

                buyTrades[symbol] = []
                buyTrades[symbol].append(round(prices['mid.h'][-3:].max().item(),5))
                buyTrades[symbol].append(round(prices['mid.l'][-3:].min().item(),5))
                buyTrades[symbol].append(False)
                buyTrades[symbol].append(False)
#               print('buy')
#               print(buyTrades)

            sellRule1 = [[i for i in ma30[symbol].iloc[range(-5,-1)]] < [i for i in ma50[symbol].iloc[range(-5,-1)]]]
            sellRule2 = [[i for i in ma50[symbol].iloc[range(-5,-1)]] < [i for i in ma100[symbol].iloc[range(-5,-1)]]]
#           print('1 ',sellRule1)
#           print('2 ',sellRule2)

            if sellRule1[0] is True\
            and sellRule2[0] is True:

                sellTrades[symbol] = []
                sellTrades[symbol].append(round(prices['mid.h'][-3:].max().item(),5))
                sellTrades[symbol].append(round(prices['mid.l'][-3:].min().item(),5))
                sellTrades[symbol].append(False)
                sellTrades[symbol].append(False)
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
        sendEmail(text,subject)

#       print(buyTrades,sellTrades,atr)
        return buyTrades, sellTrades, atr, ma30, ma50

Breakout.prepare()
timeout = 7200
timeout_start = time.time()
n1 = (len(buyTrades)+len(sellTrades))
n2 = 0
while True:

    if n2 == n1:
        subject = 'Final rapport n at '+str(datetime.datetime.now())
        textList.append('Break n at '+str(datetime.datetime.now()))
        break
    elif time.time() > (timeout_start + timeout):
        subject = 'Final rapport t at '+str(datetime.datetime.now())
        textList.append('Break time at '+str(datetime.datetime.now()))
        break

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
#               print('buy',ma30[p['instrument']].iloc[-1])
#               print('buy',ma30)
                if buy < ma30[p['instrument']].iloc[-1]\
                and buy > ma50[p['instrument']].iloc[-1]\
                and buyTrades[p['instrument']][2] == False:

                    buyTrades[p['instrument']][2] = True
                    buyTrades[p['instrument']][3] = False
#                   print('buy0')

                elif buy < ma30[p['instrument']].iloc[-1]\
                and buy > ma50[p['instrument']].iloc[-1]\
                and buyTrades[p['instrument']][2] == True:

                    buyTrades[p['instrument']][2] = False
                    buyTrades[p['instrument']][3] = False
#                   print('buy1')

                elif buy > buyTrades[p['instrument']][0]\
                and buyTrades[p['instrument']][2] == True\
                and buyTrades[p['instrument']][3] == False:
#                   print('privet')

                    buyTrades[p['instrument']][3] = True
#                   time.sleep(0.01)
#                   print('buy2')
#                   print(p['instrument'])
#                   print(buyTrades[p['instrument']])

                elif buy > buyTrades[p['instrument']][0]\
                and buyTrades[p['instrument']][3] == True\
                and buyTrades[p['instrument']][2] == True:

#                   r = accounts.AccountSummary(accountID)
#                   api.request(r)

#                   print('buy ')
#                   print(p['instrument'])
#                   print(buyTrades[p['instrument']])
                    if 'JPY' in p['instrument']:
                        stopLoss = round(buyTrades[p['instrument']][0] - atr[p['instrument']],3)
                        takeProfit = round(buyTrades[p['instrument']][0] + atr[p['instrument']],3)# * 2),3)
                    else:
                        stopLoss = round(buyTrades[p['instrument']][0] - atr[p['instrument']],5)
                        takeProfit = round(buyTrades[p['instrument']][0] + atr[p['instrument']],5)# * 2),5)
#                       print('buy ')
#                       print(p['instrument'])
#                       print(stopLoss)
#                       print('buy ')
#                       print(p['instrument'])
#                       print(takeProfit)

                    buyOrder = MarketOrderRequest(instrument=p['instrument'],\
                                  units=2000,\
                                  takeProfitOnFill=TakeProfitDetails(price=float(takeProfit)).data,\
                                  stopLossOnFill=StopLossDetails(price=float(stopLoss)).data)
                    r = orders.OrderCreate(accountID, data=buyOrder.data)
                    rv = api.request(r)
                    textList.append('Buy Order')
                    textList.append(buyOrder)
                    textList.append(' ')
#                   textList.append(rv)
#                   textList.append(' ')
                    subject = 'buy '+p['instrument']+' at '+str(datetime.datetime.now())
#                   sendEmail(str(buyOrder),subject)
                    sendEmail(str(json.dumps(rv)),subject)
#                   print(str(json.dumps(rv)))
                    del buyTrades[p['instrument']]
                    n2+=1
#                   print('buy ',rv)
#                   print(p['instrument'])
#                   print(buyTrades[p['instrument']])

            elif p['instrument'] in sellTrades:
#               print(sellTrades[p['instrument']])
#               print(sellTrades[p['instrument']][0])
#               print(sellTrades[p['instrument']][1])
#               print(sellTrades[p['instrument']][2])
#               print(sellTrades[p['instrument']][3])
                sell = float(p['bids'][0]['price'])
                if sell > ma30[p['instrument']].iloc[-1]\
                and sell < ma50[p['instrument']].iloc[-1]\
                and sellTrades[p['instrument']][2] == False:

                    sellTrades[p['instrument']][2] = True
                    sellTrades[p['instrument']][3] = False
#                   print('sell0')

                elif sell > ma30[p['instrument']].iloc[-1]\
                and sell < ma50[p['instrument']].iloc[-1]\
                and sellTrades[p['instrument']][2] == True:

                    sellTrades[p['instrument']][2] = False
                    sellTrades[p['instrument']][3] = False
#                   print('sell1')


                elif sell < sellTrades[p['instrument']][1]\
                and sellTrades[p['instrument']][2] == True\
                and sellTrades[p['instrument']][3] == False:

                    sellTrades[p['instrument']][3] = True
#                   time.sleep(0.01)
#                   print('sell2')
#                   print(p['instrument'])
#                   print(sellTrades[p['instrument']])

                elif sell < sellTrades[p['instrument']][1]\
                and sellTrades[p['instrument']][2] == True\
                and sellTrades[p['instrument']][3] == True:

#                   print('0sell')
#                   print(p['instrument'])
#                   print(sellTrades[p['instrument']])
                    if 'JPY' in p['instrument']:
                        stopLoss = round(sellTrades[p['instrument']][1] + atr[p['instrument']],3)
                        takeProfit = round(sellTrades[p['instrument']][1] - atr[p['instrument']],3)# * 2),3)
                    else:
                        stopLoss = round(sellTrades[p['instrument']][1] + atr[p['instrument']],5)
                        takeProfit = round(sellTrades[p['instrument']][1] - atr[p['instrument']],5)# * 2),5)
#                       print('1sell')
#                       print(p['instrument'])
#                       print(stopLoss)
#                       print('2sell')
#                       print(p['instrument'])
#                       print(takeProfit)

                    sellOrder = MarketOrderRequest(instrument=p['instrument'],\
                                  units=-2000,\
                                  takeProfitOnFill=TakeProfitDetails(price=float(takeProfit)).data,\
                                  stopLossOnFill=StopLossDetails(price=float(stopLoss)).data)
                    r = orders.OrderCreate(accountID, data=sellOrder.data)
                    rv = api.request(r)
                    textList.append('Sell Order')
                    textList.append(sellOrder)
                    textList.append(' ')
#                   textList.append(rv)
#                   textList.append(' ')
                    subject = 'sell '+p['instrument']+' at '+str(datetime.datetime.now())
#                   sendEmail(str(sellOrder),subject)
                    sendEmail(str(json.dumps(rv)),subject)
#                   print(str(json.dumps(rv)))
                    del sellTrades[p['instrument']]
                    n2+=1
#                   print('sell ',rv)
#                   print(p['instrument'])
#                   print(sellTrades[p['instrument']])
            else:
                pass
#               print('nothing')

    except V20Error as e:
        # for the repr
#       print('v20 repr ',repr(e))
        # for just the message, or str(e), since print calls str under the hood
#       print('v20 e ',e)
        # the arguments that the exception has been called with.
        # the first one is usually the message. (OSError is different, though)
#       print('v20 args ',e.args)
        # catch API related errors that may occur
        with open('/var/log/breakout2.log', 'a') as LOG:
            LOG.write(str(datetime.datetime.now()) + ' V20Error: {}\n'.format(e))
        pass

    except ConnectionError as e:
        # for the repr
#       print('cond repr ',repr(e))
        # for just the message, or str(e), since print calls str under the hood
#       print('cond e ',e)
        # the arguments that the exception has been called with.
        # the first one is usually the message. (OSError is different, though)
#       print('cond args ',e.args)
        with open('/var/log/breakout2.log', 'a') as LOG:
            LOG.write(str(datetime.datetime.now()) + ' Connection Error: {}\n'.format(e))
        pass

    except StreamTerminated as e:
        # for the repr
#       print('str repr ',repr(e))
        # for just the message, or str(e), since print calls str under the hood
#       print('str e ',e)
        # the arguments that the exception has been called with.
        # the first one is usually the message. (OSError is different, though)
#       print('str srg ',e.args)
        with open('/var/log/breakout2.log', 'a') as LOG:
            LOG.write(str(datetime.datetime.now()) + ' Stopping: {}\n'.format(e))
        pass

    except Exception as e:
        # for the repr
#       print('exc repr ',repr(e))
        # for just the message, or str(e), since print calls str under the hood
#       print('exc e ',e)
        # the arguments that the exception has been called with.
        # the first one is usually the message. (OSError is different, though)
#       print('exc args ',e.args)
        with open('/var/log/breakout2.log', 'a') as LOG:
            LOG.write(str(datetime.datetime.now()) + ' Exception: {}\n'.format(e))
        pass


