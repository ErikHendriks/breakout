import pandas as pd
import unittest

from indicators import indicator
from pandas.io.json import json_normalize

class TestIndicator(unittest.TestCase):

    def setUp():

        print(prices())

    def testMovingAverage(self):
        result = Breakout.prepare()
        print(result)

TestIndicator.setUp()
