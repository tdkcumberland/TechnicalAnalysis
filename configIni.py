import configparser

class iniConfig():

    def __init__(self):
        super().__init__()
        self.config = configparser.ConfigParser()
        self.config.read('./config.ini')

    def getAPIKey(self):
        return self.config['DEFAULT']['apiKey']

    def getPath(self):
        return self.config['DEFAULT']['path']

    def weekly_atr_span(self):
        return int(self.config['weekly_param']['weekly_atr_span'])
    def weekly_atr_multi(self):
        return float(self.config['weekly_param']['weekly_atr_multi'])
    def weekly_atr_trend_change_multi(self):
        return float(self.config['weekly_param']['weekly_atr_trend_change_multi'])
    def weekly_short_ma_span(self):
        return int(self.config['weekly_param']['weekly_short_ma_span'])
    def weekly_long_ma_span(self):
        return int(self.config['weekly_param']['weekly_long_ma_span'])
    def weekly_macd_signal_span(self):
        return int(self.config['weekly_param']['weekly_macd_signal_span'])
    def daily_atr_span(self):
        return int(self.config['daily_param']['daily_atr_span'])
    def daily_atr_multi(self):
        return float(self.config['daily_param']['daily_atr_multi'])
    def daily_atr_trend_change_multi(self):
        return float(self.config['daily_param']['daily_atr_trend_change_multi'])
    def daily_short_ma_span(self):
        return int(self.config['daily_param']['daily_short_ma_span'])
    def daily_medium_ma_span(self):
        return int(self.config['daily_param']['daily_medium_ma_span'])
    def daily_long_ma_span(self):
        return int(self.config['daily_param']['daily_long_ma_span'])
