from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pandas.plotting import register_matplotlib_converters
from configIni import *
from utility import *

class ETL():

    def __init__(self):
        super().__init__()
        self.newConfig = iniConfig()

    def getData(self,ticker,outSize='full',duration='daily'):
        '''
        Find and download data from AlphaVantage by ticker \r\n
        Default duration frequency is 'daily', can be changed to 'weekly'
        '''
        ts = TimeSeries(key=self.newConfig.getAPIKey(), output_format='pandas')
        if duration == 'daily':
            data, meta_data = ts.get_daily_adjusted(symbol=ticker,outputsize=outSize)
        elif duration == 'weekly':
            data, meta_data = ts.get_weekly_adjusted(symbol=ticker)
        else:
            print('Duration is not defined...')
            return
        fileName = ticker + "-" + getDate()+ "-" + duration
        dumpData(data, './' + self.newConfig.getPath() + '/' + fileName)
        return fileName

    def calATR(self,dataframe, duration='daily'):
        '''
        Calculate average true range stop adjusted for stocksplit
        '''
        if duration == 'daily':
            dataframe['ATR1'] = abs(dataframe['2. high'] - dataframe['3. low'])
            dataframe['ATR2'] = abs(dataframe['2. high'] - dataframe['4. close'].shift()/dataframe['8. split coefficient'])
            dataframe['ATR3'] = abs(dataframe['3. low'] - dataframe['4. close'].shift()/dataframe['8. split coefficient'])
            dataframe['TrueRange'] = dataframe[['ATR1', 'ATR2', 'ATR3']].max(axis=1).ewm(span=self.newConfig.daily_atr_span(),adjust=False).mean()
        elif duration == 'weekly':
            dataframe['ATR1'] = abs(dataframe['2. high'] - dataframe['3. low'])
            dataframe['ATR2'] = abs(dataframe['2. high'] - dataframe['4. close'].shift())
            dataframe['ATR3'] = abs(dataframe['3. low'] - dataframe['4. close'].shift())
            dataframe['TrueRange'] = dataframe[['ATR1', 'ATR2', 'ATR3']].max(axis=1).ewm(span=self.newConfig.weekly_atr_span(),adjust=False).mean()
        return dataframe

    def maDailyData(self,df):
        '''
        Calculate exponential moving averages as well as the calATR then return the entire dataframe
        '''
        newConfig = iniConfig()
        df['ma10'] = df.iloc[:, 4].ewm(span=self.newConfig.daily_short_ma_span(), adjust=False).mean()
        df['ma75'] = df.iloc[:, 4].ewm(span=self.newConfig.daily_medium_ma_span(),adjust=False).mean()
        df['ma100'] = df.iloc[:, 4].ewm(span=self.newConfig.daily_long_ma_span(),adjust=False).mean()
        atr = self.calATR(df)
        atr['Position'] = atr.apply(self.applyPostion, axis=1)
        atr['ATRStops'] = atr.apply(self.calcATRStops, axis=1)
        return self.stopsCalc(atr)

    def macdWeekly(self,df_weekly):
        '''
        Calculate MACD based on the weekly data \r\n
        ema12 and ema26 is used to construct MACD line with an ema9 for the signal line \r\n
        oscillator is also calcualted
        '''
        df_weekly = self.calATR(df_weekly, 'weekly')
        df_weekly['ma12'] = df_weekly.iloc[:,4].ewm(span=self.newConfig.weekly_short_ma_span(), adjust=False).mean()
        df_weekly['ma26'] = df_weekly.iloc[:,4].ewm(span=self.newConfig.weekly_long_ma_span(), adjust=False).mean()
        df_weekly['macdLine'] = df_weekly['ma12'] - df_weekly['ma26']
        df_weekly['ma9'] = df_weekly['macdLine'].ewm(span=self.newConfig.weekly_macd_signal_span(), adjust=False).mean()
        df_weekly['oscillator'] = df_weekly['macdLine'] - df_weekly['ma9']
        df_weekly['oscillatorUp'] = df_weekly['oscillator'].where(df_weekly['oscillator'] >0)
        df_weekly['oscillatorDown'] = df_weekly['oscillator'].where(df_weekly['oscillator']<=0)
        df_weekly = self.calATR(df_weekly, duration='weekly')
        df_weekly['Position'] = df_weekly.apply(self.applyWeeklyPosition, axis=1)
        df_weekly['ATRStops'] = df_weekly.apply(self.calcATRWeeklyStops, axis=1)
        return self.stopsCalc(df_weekly, 'weekly')

    def applyPostion(self,x):
        '''
        Custom dataframe function to be determine position based on ema
        '''
        if x['ma10'] <= x['ma100']:
            return 'SHORT'
        else:
            return "LONG"

    def applyWeeklyPosition(self,x):
        '''
        Custom dataframe function to be determine position based on ema
        '''
        if x['ma12'] <= x['ma26']:
            return 'SHORT'
        else:
            return "LONG"

    def calcATRStops(self,x):
        '''
        Custom dataframe function to calculate the stops based on the calcualted LONG/SHORT position
        '''
        if (x['Position'] == 'SHORT'):
            return x['5. adjusted close'] + self.newConfig.daily_atr_multi() * x['TrueRange']
        elif (x['Position'] == 'LONG'):
            return x['5. adjusted close'] - self.newConfig.daily_atr_multi() * x['TrueRange']

    def calcATRWeeklyStops(self,x):
        '''
        Custom dataframe function to calculate the stops based on the calcualted LONG/SHORT position
        '''
        if (x['Position'] == 'SHORT'):
            return x['5. adjusted close'] + self.newConfig.weekly_atr_multi() * x['TrueRange']
        elif (x['Position'] == 'LONG'):
            return x['5. adjusted close'] - self.newConfig.weekly_atr_multi() * x['TrueRange']

    def stopsCalc(self,dailyProcessed, duration='daily'):
        '''
        Determine postion, calculate stops 
        '''
        # dailyProcessed['Position'] = maDailyData(dailyProcessed).apply(applyPostion, axis=1)
        # dailyProcessed['ATRStops'] = dailyProcessed.apply(calcATRStops, axis=1)
        currentPosition = {"starting": True, "position" : "", "ATRMultiplier" : self.newConfig.daily_atr_trend_change_multi() if duration == 'daily' else self.newConfig.weekly_atr_trend_change_multi()}
        dailyProcessed['trueStop'] = dailyProcessed['ATRStops'][0]
        dailyProcessed['longStop'] = dailyProcessed['ATRStops'][0]
        dailyProcessed['shortStop'] = dailyProcessed['ATRStops'][0]

        for index, row in dailyProcessed.iterrows():
            a = dailyProcessed.index.get_loc(index)
            if currentPosition.get('starting'):
                currentPosition['position'] = dailyProcessed['Position'][0]
                currentPosition['starting'] = False
                if currentPosition['position'] == "SHORT":
                    dailyProcessed.loc[index,'longStop'] = np.NaN
                    dailyProcessed.loc[index,'shortStop'] = dailyProcessed.loc[index,'trueStop']
                else:
                    dailyProcessed.loc[index,'longStop'] = dailyProcessed.loc[index,'trueStop']
                    dailyProcessed.loc[index,'shortStop'] = np.NaN
            else:
                currentPosition['position'] = row['Position']

            yesterdatPos = dailyProcessed.iloc[a - 1]['Position']
            yesterdayStop = dailyProcessed.iloc[a - 1]['trueStop']
            todayNewStop = dailyProcessed.loc[index,'ATRStops']
            dailyPrice = dailyProcessed.loc[index,'5. adjusted close']
            atr = dailyProcessed.loc[index,'TrueRange']

            #changes in position informed by the signal, nan out the non position and fill in ATRStops for the other
            if (yesterdatPos != currentPosition['position']):
                if yesterdatPos == "SHORT":
                    dailyProcessed.loc[index,'trueStop'] = dailyPrice - (currentPosition['ATRMultiplier'] * atr)
                    dailyProcessed.loc[index,'longStop'] = dailyPrice - (currentPosition['ATRMultiplier'] * atr)
                    dailyProcessed.loc[index,'shortStop'] = np.NaN
                else:
                    dailyProcessed.loc[index,'trueStop'] = dailyPrice + (currentPosition['ATRMultiplier'] * atr)
                    dailyProcessed.loc[index,'longStop'] = np.NaN
                    dailyProcessed.loc[index,'shortStop'] = dailyPrice + (currentPosition['ATRMultiplier'] * atr)

            #if trend is continuing, adjust stops as the prices changes, implemented a rachet mechanism so that during long/short stops doesn't go down/up
            if (yesterdatPos == currentPosition['position']) & (currentPosition['position'] == 'SHORT'):
                if dailyProcessed.loc[index,'ATRStops'] >= yesterdayStop:
                    dailyProcessed.loc[index,'trueStop'] = yesterdayStop
                    dailyProcessed.loc[index,'shortStop'] = yesterdayStop
                    dailyProcessed.loc[index,'longStop'] = np.NaN
                else:
                    dailyProcessed.loc[index,'trueStop'] = todayNewStop
                    dailyProcessed.loc[index,'shortStop'] = todayNewStop
                    dailyProcessed.loc[index,'longStop'] = np.NaN

            elif (yesterdatPos == currentPosition['position']) & (currentPosition['position'] == 'LONG'):
                if dailyProcessed.loc[index,'ATRStops'] <= yesterdayStop:
                    dailyProcessed.loc[index,'trueStop'] = yesterdayStop
                    dailyProcessed.loc[index,'longStop'] = yesterdayStop
                    dailyProcessed.loc[index,'shortStop'] = np.NaN
                else:
                    dailyProcessed.loc[index,'trueStop'] = todayNewStop
                    dailyProcessed.loc[index,'longStop'] = todayNewStop
                    dailyProcessed.loc[index,'shortStop'] = np.NaN
        return dailyProcessed