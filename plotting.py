from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
import pandas as pd
from etl import *

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
    fig,plotArea =  plt.subplots(nrows=2, ncols=1,squeeze=False)
    register_matplotlib_converters()
    newConfig = iniConfig()

    #buy-sell signal
    plotArea[0][0].plot(df_daily['5. adjusted close'], color = '#A9A9A9', label = 'daily')
    plotArea[0][0].plot(df_daily['ma10'], color = '#323296', label = 'ma' + str(newConfig.daily_short_ma_span()))
    plotArea[0][0].plot(df_daily['ma75'], color = '#329664', label = 'ma' + str(newConfig.daily_medium_ma_span()))
    plotArea[0][0].plot(df_daily['ma100'], color = '#C80032', label = 'ma' + str(newConfig.daily_long_ma_span()))
    
    #stops and exit prices + retracement
    plotArea[1][0].plot(df_daily['5. adjusted close'], color = '#A9A9A9', label = 'daily')
    plotArea[1][0].plot(df_daily['longStop'], color = '#3264C8', label = 'longStop')
    plotArea[1][0].plot(df_daily['shortStop'], color = '#DC143C', label = 'shortStop')

    #volume
    # plotArea[3][0].bar(x=df_daily['6. volume'].index, height=df_daily['6. volume'], width=5.0, color='#696969', label='volume')

    plt.grid(b=True, which='major', color='#A9A9A9', linestyle='-')
    plotArea[0][0].grid(b=True, which='major', color='#A9A9A9', linestyle='-')
    plotArea[1][0].grid(b=True, which='major', color='#A9A9A9', linestyle='-')
    # plotArea[2][0].grid(b=True, which='major', color='#A9A9A9', linestyle='-')
    plotArea[0][0].legend(loc="upper left")
    plotArea[1][0].legend(loc="upper left")
    # plotArea[2][0].legend(loc="upper left")
    # plotArea[3][0].legend(loc="upper left")
    fig.suptitle(name, fontsize=16)
    # plotArea[0][0].set_title(label='Buy/Sell', fontweight=10, pad='2.0')
    # plotArea[1][0].set_title(label='Stops/Exit', fontweight=10, pad='2.0')
    # plotArea[2][0].set_title(label='Retracement', fontweight=10, pad='2.0')
    # plotArea[4][0].set_title(label='Volume', fontweight=10, pad='2.0') 
    plt.show()