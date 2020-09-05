import pandas as pd
from utility import getDate, readPickle
from etl import *
from plotting import *
from alpha_vantage.foreignexchange import ForeignExchange
from pprint import pprint

_m = './dataStore/'
_t =  'SPEM'
_d = 'daily'
_nd = _t + '-' + getDate() + '-' + _d
_nw = _t + '-' + getDate() + '-' + _d
_sd = '2019-09-01'
_ed = getDate()
etl = ETL()

# cc = ForeignExchange(key='QSMUWQIPLV31UH4Y', output_format='pandas')
# data, _ = cc.get_currency_exchange_daily(from_symbol='USD',to_symbol='JPY',outputsize='full')
# print(data.tail())

# download data
# _name = etl.getData(ticker=_t, duration=_d)

#load data
# df= readPickle(_m + _nd, _sd,_ed)
# df= readPickle(_m + _n)

# get plots

plotMACD(etl.macdWeekly(readPickle(_m + _nw)))
# plotDailyMA(etl.maDailyData(df), _nd)
# etl.maDailyData(readPickle(_m + _nd)).to_excel('VTI_OUT.xlsx')

# print(etl.maDailyData(df).tail())

# macdWeekly(df).to_excel('weeklyOut.xlsx')

#TODO: return calculation -> retracement


