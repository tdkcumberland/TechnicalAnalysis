from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
import pandas as pd
from etl import *
import matplotlib.dates as mdates

def plotMACD(df_weekly):
    fig,plotArea =  plt.subplots(nrows=3, ncols=1,squeeze=False)
    register_matplotlib_converters()
    newConfig = iniConfig()
    plotArea[0][0].plot(df_weekly['5. adjusted close'], label = 'daily',color='#646464')
    plotArea[0][0].plot(df_weekly['ma26'], label = 'ma' + str(newConfig.weekly_long_ma_span()),color='#3296FA')
    plotArea[0][0].plot(df_weekly['ma12'], label = 'ma' + str(newConfig.weekly_short_ma_span()),color='#C83232')

    plotArea[1][0].bar(x=df_weekly['oscillatorUp'].index, height=df_weekly['oscillatorUp'], width=5.0, color='g')
    plotArea[1][0].bar(x=df_weekly['oscillatorDown'].index, height=df_weekly['oscillatorDown'], width=5.0, color='r')
    plotArea[1][0].axhline(y=0, color='k', linestyle='--')
    plotArea[1][0].plot(df_weekly['macdLine'], label= 'MACD',color='#3296FA')
    plotArea[1][0].plot(df_weekly['ma9'], label= 'signal line',color='#FA6400')

    plotArea[2][0].plot(df_weekly['5. adjusted close'], color = '#A9A9A9', label = 'daily')
    plotArea[2][0].plot(df_weekly['longStop'], color = '#3264C8', label = 'longStop')
    plotArea[2][0].plot(df_weekly['shortStop'], color = '#DC143C', label = 'shortStop')

    plotArea[0][0].grid(b=True, which='major', color='#A9A9A9', linestyle='-')
    plotArea[1][0].grid(b=True, which='major', color='#A9A9A9', linestyle='-')
    plotArea[1][0].legend(loc="lower center")
    plotArea[0][0].legend(loc="upper center")
    plt.show()

def plotDailyMA(df_daily, name):
    fig,plotArea =  plt.subplots(nrows=4, ncols=1,squeeze=False)
    register_matplotlib_converters()
    newConfig = iniConfig()
    my_year_month_fmt = mdates.DateFormatter('%m/%y')

    #buy-sell signal
    plotArea[0][0].plot(df_daily['5. adjusted close'], color = '#A9A9A9', label = 'daily')
    plotArea[0][0].plot(df_daily['ma10'], color = '#323296', label = 'ma' + str(newConfig.daily_short_ma_span()))
    plotArea[0][0].plot(df_daily['ma75'], color = '#329664', label = 'ma' + str(newConfig.daily_medium_ma_span()))
    plotArea[0][0].plot(df_daily['ma100'], color = '#C80032', label = 'ma' + str(newConfig.daily_long_ma_span()))
    
    #stops and exit prices + retracement
    plotArea[1][0].plot(df_daily['5. adjusted close'], color = '#A9A9A9', label = 'daily')
    # plotArea[1][0].plot(df_daily['longStop'], color = '#3264C8', label = 'longStop')
    # plotArea[1][0].plot(df_daily['shortStop'], color = '#DC143C', label = 'shortStop')

    #volume
    # plotArea[3][0].bar(x=df_daily['6. volume'].index, height=df_daily['6. volume'], width=5.0, color='#696969', label='volume')

    # cummulative returns
    plotArea[2][0].plot(df_daily.index,df_daily['my_ema_relative_return'],label='Cummulative Returns')

    #MACD
    plotArea[3][0].plot(df_daily.index,df_daily['macdLine'],label='MACD')
    plotArea[3][0].plot(df_daily.index,df_daily['ma9'],label='Signal')
    plotArea[3][0].bar(x=df_daily.index,height=df_daily['oscillatorUp'],color='#42f557',width=5.0)
    plotArea[3][0].bar(x=df_daily.index,height=df_daily['oscillatorDown'],color='#42f557',width=5.0)

    #formatting
    plt.grid(b=True, which='major', color='#A9A9A9', linestyle='-')
    plotArea[0][0].grid(b=True, which='major', color='#A9A9A9', linestyle='-')
    plotArea[1][0].grid(b=True, which='major', color='#A9A9A9', linestyle='-')
    plotArea[2][0].xaxis.set_major_formatter(my_year_month_fmt)
    # plotArea[2][0].grid(b=True, which='major', color='#A9A9A9', linestyle='-')
    plotArea[0][0].legend(loc='best')
    plotArea[1][0].legend(loc='best')
    plotArea[2][0].legend(loc='best')
    plotArea[3][0].legend(loc='best')
    fig.suptitle(name, fontsize=16)
    # plotArea[0][0].set_title(label='Buy/Sell', fontweight=10, pad='2.0')
    # plotArea[1][0].set_title(label='Stops/Exit', fontweight=10, pad='2.0')
    plotArea[2][0].set_title(label='Cummulative Returns', fontweight=10, pad='2.0')
    plotArea[3][0].set_title(label='Percentage Price Oscillators' + str(newConfig.weekly_short_ma_span()) + '-' + str(newConfig.weekly_long_ma_span()) + '-' + str(newConfig.weekly_macd_signal_span()), fontweight=10, pad='2.0')
    # plotArea[4][0].set_title(label='Volume', fontweight=10, pad='2.0') 
    plt.show()

def plotFinalResult(output):
    register_matplotlib_converters()
    fig,plotArea =  plt.subplots(nrows=3, ncols=1,squeeze=False)

    #buy-sell signal
    plotArea[0][0].plot(output['5. adjusted close'], color = '#A9A9A9', label = 'daily')
    plotArea[0][0].plot(output['ma10'], color = '#323296', label = 'ma' + 'short')
    plotArea[0][0].plot(output['ma75'], color = '#329664', label = 'ma' + 'medium')
    plotArea[0][0].plot(output['ma100'], color = '#C80032', label = 'ma' + 'long')

    # stops and exit prices + retracement
    # plotArea[1][0].plot(output['5. adjusted close'], color = '#A9A9A9', label = 'daily')
    # plotArea[1][0].plot(output.index,output['trading_position_before'], color = '#3264C8', label = 'trading_position')
    plotArea[1][0].plot(output.index,output['trading_position_before'], color = '#C80032', label = 'trading_position')
    # plotArea[1][0].plot(output['shortStop'], color = '#DC143C', label = 'shortStop')

    plotArea[2][0].plot(output.index,output['my_ema_relative_return'],label='EMAX w/ 5% M2MStp, 15dh-re', color = '#0033cc')
    plotArea[2][0].plot(output.index,output['buy_hold_relative_return'],label='Buy and hold' , color = '#ff0000')
    plotArea[2][0].plot(output.index,output['naive_ema_crossover_relative_return'],label='Naive EMAX', color = '#00cc00')
    plotArea[2][0].plot(output.index,output['naive_macd_crossover_relative_return'],label='Naive MACDX', color = '#fcba03')
    # plotArea[3][0].plot(output.index,output['buy_hold_rel_ret'],label='Buy and Hold Relative Return')
    plotArea[0][0].legend()
    plotArea[1][0].legend()
    plotArea[2][0].legend()
    plt.show()