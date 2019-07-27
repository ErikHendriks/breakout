#!/usr/bin/env python3

import datetime
import gnupg
import json
import logging
import oandapyV20
import oandapyV20.endpoints.orders as orders
import requests
import smtplib
import time
import urllib3

from oandapyV20 import API
from oandapyV20.contrib.requests import *
from oandapyV20.endpoints.instruments import InstrumentsCandles
from oandapyV20.endpoints.pricing import PricingStream
from oandapyV20.exceptions import V20Error, StreamTerminated
from requests.exceptions import ConnectionError

logging.basicConfig(
    filename='/var/log/breakout.log',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s : %(message)s',)

#requests.packages.urllib3.disable_warnings()
#requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'

def sendEmail(text,subject):
    '''
        Sending relevant information about initial buy/sell target prices as well as
        stop loss and take profit prices, executed buy/sell orders, when all trades are
        executed or allotted time has passed.
        You need a sender email address with password, receiver email address
        with fingerprint of public key.
    '''
    try:
        fingerprint = conf[3]
        password = conf[4]
        sender = conf[6]
        reciever = conf[5]
#       subject = 'Oanda v20 breakout test rapport at '+str(datetime.datetime.now())
        gpg = gnupg.GPG(gnupghome='/etc/breakout/.gnupg')
        text = str(gpg.encrypt(text,fingerprint))
        mail = '''From: %s\nTo: %s\nSubject: %s\n\n%s
               ''' % (sender,reciever,subject,text)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender,password)
#       server.set_debuglevel(1)
        server.sendmail(sender, reciever, mail)
        server.quit()
    except Exception as e:
#       print(e)
        with open('/var/log/breakout.log', 'a') as LOG:
            LOG.write(str(datetime.datetime.now()) + ' sendEmail: {}\n'.format(e))
        pass

buy = {}
buyTP = {}
buySL = {}
sell = {}
sellTP = {}
sellSL = {}
risk = {}
textList = []
textList.append('Oanda v20 breakout rapport at '+str(datetime.datetime.now()))
textList.append(' ')

conf = [line.strip('\n') for line in open('/etc/breakout/conf.v20')]
accountID = conf[0]
api = API(access_token = conf[1],\
          environment = conf[2])

symbols = ['GBP_USD','GBP_AUD','EUR_USD','GBP_NZD','EUR_AUD','NZD_USD','EUR_NZD',\
           'AUD_USD','GBP_CAD','EUR_CAD','AUD_NZD','EUR_GBP','AUD_CAD','GBP_CHF',\
           'USD_CAD','EUR_CHF','AUD_CHF','USD_CHF']

#symbols = ['AUD_CAD','AUD_CHF','AUD_JPY','AUD_NZD','AUD_USD',\
#          'CAD_CHF','CAD_JPY',\
#          'CHF_JPY',\
#          'EUR_AUD','EUR_CAD','EUR_CHF','EUR_GBP','EUR_JPY','EUR_NZD','EUR_USD',\
#          'GBP_AUD','GBP_CAD','GBP_CHF','GBP_JPY','GBP_NZD','GBP_USD',\
#          'NZD_CAD','NZD_CHF','NZD_JPY','NZD_USD','NZD_USD',\
#          'USD_CAD','USD_CHF','USD_JPY']

n = 0
ohlc4h = {'count': 1,'granularity': 'H4'}
for symbol in symbols:
    candle = InstrumentsCandles(instrument=symbol,params=ohlc4h)
    api.request(candle)

    textList.append(symbol)
    textList.append('#######')
    risk[symbol] = float(candle.response['candles'][0]['mid']['h']) - float(candle.response['candles'][0]['mid']['l'])
    if risk[symbol] < 0.0025:
        risk[symbol] = 0.0050
#       buy[symbol] = None
#       sell[symbol] = None
#       textList.append('No Trade')
#       textList.append(' ')
#       n+=1

    elif risk[symbol] > 0.0065:
        risk[symbol] = 0.0050
#       buy[symbol] = None
#       sell[symbol] = None
#       textList.append('No Trade')
#       textList.append(' ')
#       n+=1

#   else:
    buy[symbol] = float(candle.response['candles'][0]['mid']['h'])
    buyTP[symbol] = float(candle.response['candles'][0]['mid']['h']) + float(risk[symbol])
    buySL[symbol] = float(candle.response['candles'][0]['mid']['l'])
    sell[symbol] = float(candle.response['candles'][0]['mid']['l'])
    sellTP[symbol] = float(candle.response['candles'][0]['mid']['l']) - float(risk[symbol])
    sellSL[symbol] = float(candle.response['candles'][0]['mid']['h'])
#   print(buy[symbol])
#   print(sell[symbol])
    textList.append('Buy')
    textList.append(buy[symbol])
    textList.append(' ')
    textList.append('Buy Take Profit')
    textList.append(buyTP[symbol])
    textList.append(' ')
    textList.append('Buy Stop Loss')
    textList.append(buySL[symbol])
    textList.append(' ')
    textList.append('Sell')
    textList.append(sell[symbol])
    textList.append(' ')
    textList.append('Sell Take Pofit')
    textList.append(sellTP[symbol])
    textList.append(' ')
    textList.append('Sell Stop Loss')
    textList.append(sellSL[symbol])
    textList.append(' ')

#textList.append('n')
#textList.append(n)
#textList.append(' ')

text = '\n'.join(map(str,textList))
subject = 'Start rapport at '+str(datetime.datetime.now())
sendEmail(text,subject)

params = {'instruments':'GBP_USD,GBP_AUD,EUR_USD,GBP_NZD,EUR_AUD,NZD_USD,EUR_NZD,AUD_USD,GBP_CAD,EUR_CAD,AUD_NZD,EUR_GBP,AUD_CAD,GBP_CHF,USD_CAD,EUR_CHF,AUD_CHF,USD_CHF'}
#params = {'instruments':'AUD_CAD,AUD_CHF,AUD_JPY,AUD_NZD,AUD_USD,CAD_CHF,CAD_JPY,CHF_JPY,EUR_AUD,EUR_CAD,EUR_CHF,EUR_GBP,EUR_JPY,EUR_NZD,EUR_USD,GBP_AUD,GBP_CAD,GBP_CHF,GBP_JPY,GBP_NZD,GBP_USD,NZD_CAD,NZD_CHF,NZD_JPY,NZD_USD,NZD_USD,USD_CAD,USD_CHF,USD_JPY'}
price = PricingStream(accountID=accountID,params=params)
date = datetime.datetime.now()

smaData30h1 = {'count': 30,'granularity': 'H1'}
smaData50h1 = {'count': 50,'granularity': 'H1'}
smaData100h1 = {'count': 100,'granularity': 'H1'}
sma30h1 = {}
sma50h1 = {}
sma100h1 = {}

smaData30h2 = {'count': 30,'granularity': 'H2'}
smaData50h2 = {'count': 50,'granularity': 'H2'}
smaData100h2 = {'count': 100,'granularity': 'H2'}
sma30h2 = {}
sma50h2 = {}
sma100h2 = {}

smaData30h3 = {'count': 30,'granularity': 'H6'}
smaData50h3 = {'count': 50,'granularity': 'H6'}
smaData100h3 = {'count': 100,'granularity': 'H6'}
sma30h3 = {}
sma50h3 = {}
sma100h3 = {}

smaData30h4 = {'count': 30,'granularity': 'H4'}
smaData50h4 = {'count': 50,'granularity': 'H4'}
smaData100h4 = {'count': 100,'granularity': 'H4'}
sma30h4 = {}
sma50h4 = {}
sma100h4 = {}

textList = []
textList.append('Oanda v20 breakout rapport at '+str(datetime.datetime.now()))
textList.append(' ')

timeout = 14400
timeout_start = time.time()
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
#           print('1',buy[p['instrument']],sell[p['instrument']])
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
                    stopLoss = float(p['asks'][0]['price']) - risk[p['instrument']]
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
                    stopLoss = float(p['asks'][0]['price']) + risk[p['instrument']]
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

textList.append('n')
textList.append(n)
text = '\n'.join(map(str,textList))
sendEmail(text,subject)
