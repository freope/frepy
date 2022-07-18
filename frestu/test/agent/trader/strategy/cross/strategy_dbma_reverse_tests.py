import os
import sys
import unittest

import numpy as np
import pandas as pd

sys.path.append(os.path.join('..'))
from frestu.agent.trader.strategy.cross import StrategyDbmaReverse


class StrategyDbmaReverseTests(unittest.TestCase):

    def setUp(self):
        self.strategy_dbsma = StrategyDbmaReverse('sma', 2, 'sma', 3)
        self.strategy_dbema = StrategyDbmaReverse('ema', 2, 'ema', 3)
        self.df = pd.DataFrame(
            [
                ['2020-01-01 17:00:00', 0],
                ['2020-01-01 17:01:00', 10],
                ['2020-01-01 17:02:00', 20],
                ['2020-01-01 17:03:00', 30],
                ['2020-01-01 17:04:00', 25],
                ['2020-01-01 17:05:00', 15],
                ['2020-01-01 17:06:00', 5],
                ['2020-01-01 17:07:00', 10],
                ['2020-01-01 17:08:00', 30],
                ['2020-01-01 17:09:00', 60],
                ['2020-01-01 17:10:00', 70],
            ],
            columns=['time', 'val'],
        ).set_index('time')
    
    def tearDown(self):
        pass
    
    def test_calculate_open_indicators(self):
        # dbsma
        indicator = self.strategy_dbsma.calculate_open_indicators(self.df)
        self.assertTrue(np.isnan(indicator.loc['2020-01-01 17:00:00']))
        self.assertEqual(indicator.loc['2020-01-01 17:02:00'], 5.0)
        self.assertGreater(indicator.loc['2020-01-01 17:09:00'], 11.0)
        self.assertLess(indicator.loc['2020-01-01 17:09:00'], 12.0)
        
        # dbema
        indicator = self.strategy_dbema.calculate_open_indicators(self.df)
        self.assertEqual(indicator.loc['2020-01-01 17:00:00'], 0.0)
        self.assertGreater(indicator.loc['2020-01-01 17:01:00'], 1.6)
        self.assertLess(indicator.loc['2020-01-01 17:01:00'], 1.7)
        self.assertGreater(indicator.loc['2020-01-01 17:09:00'], 7.5)
        self.assertLess(indicator.loc['2020-01-01 17:09:00'], 7.6)
    
    def test_convert_open_indicators(self):
        # dbsma
        indicator = self.strategy_dbsma.calculate_open_indicators(self.df)
        can_open_long = self.strategy_dbsma.convert_open_indicators(
            indicator, 'long')
        can_open_short = self.strategy_dbsma.convert_open_indicators(
            indicator, 'short')
        # long
        self.assertFalse(can_open_long['2020-01-01 17:04:00'])
        self.assertTrue(can_open_long['2020-01-01 17:05:00'])
        # short
        self.assertFalse(can_open_short['2020-01-01 17:01:00'])
        self.assertTrue(can_open_short['2020-01-01 17:02:00'])

        # dbema
        indicator = self.strategy_dbema.calculate_open_indicators(self.df)
        can_open_long = self.strategy_dbema.convert_open_indicators(
            indicator, 'long')
        can_open_short = self.strategy_dbema.convert_open_indicators(
            indicator, 'short')
        # long
        self.assertFalse(can_open_long['2020-01-01 17:04:00'])
        self.assertTrue(can_open_long['2020-01-01 17:05:00'])
        # short
        self.assertFalse(can_open_short['2020-01-01 17:00:00'])
        self.assertTrue(can_open_short['2020-01-01 17:01:00'])


if __name__ == '__main__':
    unittest.main()