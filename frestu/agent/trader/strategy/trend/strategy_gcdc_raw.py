from frestu.agent.trader.strategy.cross import StrategyDbmaRaw


class StrategyGcdcRaw(StrategyDbmaRaw):

    def __init__(self, window_shorter, window_longer):
        super().__init__('sma', window_shorter, 'sma', window_longer)