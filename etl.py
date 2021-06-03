from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pandas.plotting import register_matplotlib_converters
from configIni import *
from utility import *
import time

class ETL():

    def __init__(self):
        super().__init__()
        self.newConfig = iniConfig()
        self.sector_equity = ['FSTA','SCHH','FDIS','FCOM','FUTY','FMAT','FHLC','FNCL','FIDU','FTEC','FENY','PBD']
        self.precious_metals = ['SBUG', 'GBUG', 'BAR', 'PALL', 'PGM', 'SIVR']
        self.fixed_income = ['TLT', 'IEI']
        self.commodity = ['GRN', 'JJA', 'XHB', 'DBC', 'MLPA', 'EBLU', 'COW', 'FAAR', 'JJE', 'MLPX', 'XTN', 'GNR', 'JJM']
        self.geographically = ['FLLA', 'CXSE', 'FLAX', 'FLCH', 'VWO', 'VPL', 'JPN']
        self.currency = ['FXC', 'DLR.TO']
        self.everything = []
        self.everything.extend(self.sector_equity)
        self.everything.extend(self.precious_metals)
        self.everything.extend(self.fixed_income)
        self.everything.extend(self.commodity)
        self.everything.extend(self.geographically)
        self.everything.extend(self.currency)

    def get_data_from_ticker_set(self, ticker_set='everything', outSize='compact'):
        for ticker in self.select_ticker_set(ticker_set):
            try:
                now = time.time()
                self.getData(ticker, outSize=outSize)
                print('Finish downloading ' + ticker)
                later = time.time()
                difference = int(later - now)
                if (difference < 12):
                    time.sleep(12 - difference)
                else:
                    continue
            except Exception:
                pass

    def select_ticker_set(self, ticker_set='everything'):
        return {
            'everything' : self.everything,
            'sector' : self.sector_equity,
            'precious_metals' : self.precious_metals,
            'fixed_income' : self.fixed_income,
            'commodity' : self.commodity,
            'geographically' : self.geographically
        } [ticker_set]

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
        fileName = ticker #+ "-" + getDate()+ "-" + duration
        dumpData(data, './' + self.newConfig.getPath() + '/' + fileName)
        return fileName

    def getDataframe(self,ticker,outSize='full',duration='daily'):
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
        return (data, meta_data)

    def calATR(self,dataframe, duration='daily'):
        '''
        Calculate average true range stop adjusted for stocksplit
        '''
        if duration == 'daily':
            dataframe['ATR1'] = abs(dataframe['2. high'] - dataframe['3. low'])
            dataframe['ATR2'] = abs(dataframe['2. high'] - dataframe['5. adjusted close'].shift())#/dataframe['8. split coefficient'])
            dataframe['ATR3'] = abs(dataframe['3. low'] - dataframe['5. adjusted close'].shift())#/dataframe['8. split coefficient'])
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
        # atr['ATRStops'] = atr.apply(self.calcATRStops, axis=1)

        atr['trading_position'] = atr['Position'].apply(self.trading_position)
        atr['trading_position'] = atr['trading_position'].shift()
        atr['asset_log_returns'] = np.log(atr['5. adjusted close']).diff()
        atr['strat_ret'] = atr['asset_log_returns'] * atr['trading_position']
        atr['cum_strategy_asset_log_returns'] = atr['strat_ret'].cumsum()
        atr['naive_ema_crossover_relative_return'] = np.exp(atr['cum_strategy_asset_log_returns']) - 1

        atr['ma12'] = atr.iloc[:,4].ewm(span=self.newConfig.weekly_short_ma_span(), adjust=False).mean()
        atr['ma26'] = atr.iloc[:,4].ewm(span=self.newConfig.weekly_long_ma_span(), adjust=False).mean()
        atr['macdLine'] = (atr['ma12'] - atr['ma26'])/atr['ma26']
        atr['ma9'] = atr['macdLine'].ewm(span=self.newConfig.weekly_macd_signal_span(), adjust=False).mean()
        atr['oscillator'] = atr['macdLine'] - atr['ma9']
        atr['oscillatorUp'] = atr['oscillator'].where(atr['oscillator'] >0)
        atr['oscillatorDown'] = atr['oscillator'].where(atr['oscillator']<=0)

        atr['macd_Position'] = atr.apply(self.applyMACDPosition, axis=1)
        atr['macd_trading_position'] = atr['macd_Position'].shift()
        atr['macd_asset_log_returns'] = np.log(atr['5. adjusted close']).diff()
        atr['macd_strat_ret'] = atr['macd_asset_log_returns'] * atr['macd_trading_position']
        atr['macd_cum_strategy_asset_log_returns'] = atr['macd_strat_ret'].cumsum()
        atr['naive_macd_crossover_relative_return'] = np.exp(atr['macd_cum_strategy_asset_log_returns']) - 1

        # return self.stopsCalc(atr)
        return atr

    def trading_position(self, x):
        return 0 if x == 'SHORT' else 1

    def applyMACDPosition(self, x):
        if x['ma9'] < x['macdLine']:
            return 0
        else:
            return 1

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

    def longOverlay(self, output):
        output['trading_position_before'] = output['trading_position']
        output['current_peak'] = output['trading_position']
        tradeCount = 0
        currentPosition = {"starting": True, "position" : "", "exit" : False}
        currentPeakTrough = output['5. adjusted close'][0]
        lookbackMax = currentPeakTrough
        for index, row in output.iterrows():
            a = output.index.get_loc(index)
            if currentPosition.get('starting'):
                currentPosition['position'] = row['Position']
                yesterdatPos = row['Position']
                currentPosition['starting'] = False
                currentPeakTrough = row['5. adjusted close']
            else:
                currentPosition['position'] = row['Position']

            dailyPrice = output.loc[index,'5. adjusted close']

            # lookback period for new local high for reentry
            # alternative approach version finding new all time high
            if a > 0:
                if a <= 15:
                    lookbackMax = output['5. adjusted close'][0:a].max()
                else:
                    lookbackMax = output['5. adjusted close'][a-16:a-1].max()

            if currentPosition['exit'] == True:
                if (yesterdatPos == 'SHORT') & (currentPosition['position'] == 'SHORT'):
                    output.loc[index,'trading_position_before'] = 0
                elif (yesterdatPos == 'SHORT') & (currentPosition['position'] == 'LONG'):
                    tradeCount +=1
                    currentPeakTrough = dailyPrice
                    currentPosition['exit'] = False
                    output.loc[index,'trading_position_before'] = 1
                elif (yesterdatPos == 'LONG') & (currentPosition['position'] == 'LONG'):
                    if dailyPrice > lookbackMax:
                        tradeCount +=1
                        currentPeakTrough = dailyPrice
                        currentPosition['exit'] = False
                        output.loc[index,'trading_position_before'] = 1
                    else:
                        output.loc[index,'trading_position_before'] = 0
                elif (yesterdatPos == 'LONG') & (currentPosition['position'] == 'SHORT'):
                    output.loc[index,'trading_position_before'] = 0
            else:
                if dailyPrice >= currentPeakTrough:
                    currentPeakTrough = dailyPrice
                    output.loc[index,'trading_position_before'] = 1
                #elif
                elif ((currentPeakTrough-dailyPrice)/currentPeakTrough)*100 > 5:
                    currentPosition['exit'] = True
                    tradeCount +=1
                    output.loc[index,'trading_position_before'] = 0
                else:
                    output.loc[index,'trading_position_before'] = 1


            output.loc[index,'current_peak'] = currentPeakTrough
            yesterdatPos = row['Position']

        # output.to_excel("SPY.xlsx")
        output['Nasset_log_returns'] = np.log(output['5. adjusted close']).diff()
        output['Nstrat_ret'] = output['Nasset_log_returns'] * output['trading_position_before']
        output['Ncum_strategy_asset_log_returns'] = output['Nstrat_ret'].cumsum()
        output['my_ema_relative_return'] = np.exp(output['Ncum_strategy_asset_log_returns']) - 1

        output['buy_hold'] = output['Nasset_log_returns'] * 1
        output['buy_hold_log_ret'] = output['buy_hold'].cumsum()
        output['buy_hold_relative_return'] = np.exp(output['buy_hold_log_ret']) - 1

        # print(tradeCount)
        _ = output[['my_ema_relative_return','buy_hold_relative_return' ,'naive_ema_crossover_relative_return', 'naive_macd_crossover_relative_return']].iloc[-1]
        # print(_)
        return output, _.values, tradeCount, output.index.values[0], _.name

    def newStrategy(self, output):
        output['trading_position_before'] = output['trading_position']
        tradeCount = 0
        currentPosition = {"yesterday_signal": 0, "today_signal" : 0, "entry_price" : -1, "in_or_out" : False, "current_profit": 0, "max_profit": 0}
        currentPeakTrough = output['5. adjusted close'][0]
        lookbackMax = currentPeakTrough
        lookbackperiod = 15
        for index, row in output.iterrows():
            a = output.index.get_loc(index)
            currentPosition['today_signal'] = 1 if row['ma10'] > row['ma100'] else 0
            dailyPrice = output.loc[index,'5. adjusted close']
            # lookback period for new local high for reentry alternative approach version finding new all time h
            #igh
            if a > 0:
                if a <= lookbackperiod:
                    lookbackMax = output['5. adjusted close'][0:a].max()
                else:
                    lookbackMax = output['5. adjusted close'][a-lookbackperiod+1:a-1].max()
            #OUT
            if currentPosition['in_or_out']==False:
                if currentPosition['today_signal'] == 0 and currentPosition['yesterday_signal'] == 0: #continue to stay out
                    currentPosition['entry_price'] = -1
                    output.loc[index,'trading_position_before'] = 0
                elif currentPosition['today_signal'] == 1 and currentPosition['yesterday_signal'] == 0: #buy, trend reverse
                    tradeCount+=1
                    currentPosition['entry_price'] = dailyPrice
                    currentPosition['in_or_out'] = True
                    currentPeakTrough = dailyPrice
                    output.loc[index,'trading_position_before'] = 1
                elif currentPosition['today_signal'] == 1 and currentPosition['yesterday_signal'] == 1: #on trend but exited before, reentry
                    if dailyPrice >= lookbackMax:
                        tradeCount +=1
                        currentPosition['entry_price'] = dailyPrice
                        currentPeakTrough = dailyPrice
                        currentPosition['in_or_out'] = True
                        output.loc[index,'trading_position_before'] = 1
                    else:
                        output.loc[index,'trading_position_before'] = 0
                elif currentPosition['today_signal'] == 0 and currentPosition['yesterday_signal'] == 1: #unlikely but possibly due to early exits from other criteria
                    currentPosition['entry_price'] = -1
                    output.loc[index,'trading_position_before'] = 0
            #IN
            else:
                currentPeakTrough = dailyPrice if dailyPrice > currentPeakTrough else currentPeakTrough
                currentPosition['max_profit'] = ((currentPeakTrough - currentPosition['entry_price'])/currentPosition['entry_price']) * 100
                currentPosition['current_profit'] = ((dailyPrice - currentPosition['entry_price'])/currentPosition['entry_price']) * 100
                if currentPosition['today_signal'] == 1 and currentPosition['yesterday_signal'] == 1: #continue to stay in
                    output.loc[index,'trading_position_before'] = 1

                # if ((currentPeakTrough-dailyPrice)/currentPeakTrough)*100 > 5:
                #     currentPosition['in_or_out'] = False
                #     currentPosition['entry_price'] = -1
                #     tradeCount +=1
                #     output.loc[index,'trading_position_before'] = 0
                # else:
                #     output.loc[index,'trading_position_before'] = 1
                else:
                    if currentPosition['max_profit'] < 7: #haven't made 7% yet, use entry price to check and wait it out
                        if ((dailyPrice - currentPosition['entry_price'])/currentPosition['entry_price']) * 100 <= -5: # lost more than 5% out
                            tradeCount +=1
                            currentPosition['entry_price'] = -1
                            currentPosition['in_or_out'] = False
                            output.loc[index,'trading_position_before'] = 0
                        else: #hang in there and wait it out, regardless of the signal
                            output.loc[index,'trading_position_before'] = 1
                    else: #made more than 7% in profit, use M2M for exit criteria
                        if (currentPosition['max_profit'] - currentPosition['current_profit']) >=5: #lose 7% M2M, exit
                            tradeCount +=1
                            currentPosition['entry_price'] = -1
                            currentPosition['in_or_out'] = False
                            output.loc[index,'trading_position_before'] = 0
                        else:#stay put
                            output.loc[index,'trading_position_before'] = 1 

            currentPosition['yesterday_signal'] = currentPosition['today_signal']

        output['Nasset_log_returns'] = np.log(output['5. adjusted close']).diff()
        output['Nstrat_ret'] = output['Nasset_log_returns'] * output['trading_position_before']
        output['Ncum_strategy_asset_log_returns'] = output['Nstrat_ret'].cumsum()
        output['my_ema_relative_return'] = np.exp(output['Ncum_strategy_asset_log_returns']) - 1

        output['buy_hold'] = output['Nasset_log_returns'] * 1
        output['buy_hold_log_ret'] = output['buy_hold'].cumsum()
        output['buy_hold_relative_return'] = np.exp(output['buy_hold_log_ret']) - 1

        # print(tradeCount)
        _ = output[['my_ema_relative_return','buy_hold_relative_return' ,'naive_ema_crossover_relative_return', 'naive_macd_crossover_relative_return']].iloc[-1]
        # print(_)
        return output, _.values, tradeCount, output.index.values[0], _.name

    def strat_compare(self, df_out):
        df_out['vs_hold'] = df_out['my_ema_relative_return'] - df_out['buy_hold_relative_return']
        df_out['vs_naive'] = df_out['my_ema_relative_return'] - df_out['naive_ema_crossover_relative_return']
        df_out['trade_per_month_volatility'] = df_out['number_of_trades']/df_out['duration_in_month']
        df_out['return_normalized_against_volatility'] = df_out['my_ema_relative_return'] / df_out['trade_per_month_volatility']
        df_out.to_excel('All.xlsx')