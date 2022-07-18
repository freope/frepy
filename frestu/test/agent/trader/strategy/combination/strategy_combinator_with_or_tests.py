import os
import sys
import unittest

import pandas as pd

sys.path.append(os.path.join('..'))
from frestu.agent.trader.strategy.combination import StrategyCombinatorWithOr
from frestu.agent.trader.strategy.trend import StrategyMau
from frestu.agent.trader.strategy.trend import StrategyGcdc
from frestu.agent.trader import Trader
from frestu.agent.trader import Position


class StrategyCombinatorWithOrTests(unittest.TestCase):

    def setUp(self):
        strategy1 = StrategyGcdc(window_shorter=2, window_longer=3)
        strategy2 = StrategyMau(windows=[2, 3, 4])
        strategies = [strategy1, strategy2]
        self.strategy = StrategyCombinatorWithOr(strategies)
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
    
    def test_calculate_opening_times(self):
        opening_times = self.strategy.calculate_opening_times(self.df)
        # long
        otsl = opening_times[0]
        self.assertEqual(len(otsl), 2)
        otl = otsl[0]
        self.assertEqual(otl, '2020-01-01 17:02:00')
        otl = otsl[1]
        self.assertEqual(otl, '2020-01-01 17:08:00')
        # short
        otss = opening_times[1]
        self.assertEqual(len(otss), 1)
        ots = otss[0]
        self.assertEqual(ots, '2020-01-01 17:05:00')
    
    def test_calculate_closing_times(self):
        opening_times = self.strategy.calculate_opening_times(self.df)
        closing_times = \
            self.strategy.calculate_closing_times(self.df, opening_times)
        # long
        lcts = closing_times[0]
        self.assertEqual(len(lcts), 2)
        lct = lcts[0]
        self.assertEqual(lct, '2020-01-01 17:05:00')
        lct = lcts[1]
        self.assertIsNone(lct)
        # short
        scts = closing_times[1]
        self.assertEqual(len(scts), 1)
        sct = scts[0]
        self.assertEqual(sct, '2020-01-01 17:08:00')
    
    def test_create_positions(self):
        open_positions, closed_positions = \
            self.strategy.create_positions(self.df)
        # open
        self.assertEqual(len(open_positions), 1)
        open_time = open_positions[0]
        self.assertEqual(open_time['position_type'], 'long')
        self.assertEqual(open_time['opening_time'], '2020-01-01 17:08:00')
        self.assertIsNone(open_time['closing_time'])
        # closed
        self.assertEqual(len(closed_positions), 2)
        closed_time = closed_positions[0]
        self.assertEqual(closed_time['position_type'], 'long')
        self.assertEqual(closed_time['opening_time'], '2020-01-01 17:02:00')
        self.assertEqual(closed_time['closing_time'], '2020-01-01 17:05:00')
        closed_time = closed_positions[1]
        self.assertEqual(closed_time['position_type'], 'short')
        self.assertEqual(closed_time['opening_time'], '2020-01-01 17:05:00')
        self.assertEqual(closed_time['closing_time'], '2020-01-01 17:08:00')
    
    def test_calculate_indicators(self):
        open_indicators = self.strategy.calculate_open_indicators(self.df)
        self.assertFalse(open_indicators['long']['2020-01-01 17:01:00'])
        self.assertTrue(open_indicators['long']['2020-01-01 17:02:00'])
        self.assertFalse(open_indicators['long']['2020-01-01 17:07:00'])
        self.assertTrue(open_indicators['long']['2020-01-01 17:08:00'])
        self.assertFalse(open_indicators['short']['2020-01-01 17:04:00'])
        self.assertTrue(open_indicators['short']['2020-01-01 17:05:00'])


if __name__ == '__main__':
    unittest.main()