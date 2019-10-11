import unittest

from breakout import Breakout

class TestBreakout(unittest.TestCase):

    def testPrepare():
        result = Breakout.prepare()
        print(result)

