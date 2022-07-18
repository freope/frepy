from frestu.agent.trader.strategy.cross import StrategyCrossIndicatorsAbstract
from frestu.feature_extraction.time_series import ExtractorDeviationRate


class StrategyDeviationRate(StrategyCrossIndicatorsAbstract):

    def __init__(self, window, threshold_long, threshold_short):
        super().__init__(threshold_long, threshold_short)
        self.__extractor = ExtractorDeviationRate(window)

    def calculate_open_indicators(self, df):
        return self.__extractor.extract(df).iloc[:, 0]