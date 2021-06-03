from utility import getDate, readPickle, convertNP_datetime_to_py_datetime, appendToDF, getOffSetFromToday
from etl import *
from plotting import *

_m = './dataStore/'
_t = 'JJA'
_d = 'daily'
_nd = _t + '-' + getDate() + '-' + _d
_nw = _t + '-' + getDate() + '-' + _d
_sd = '2020-01-01'
_ed = getDate()
etl = ETL()

# download & overwrite the data everyday
# etl.get_data_from_ticker_set(outSize='full')
etl.getData('SPY')

def run_all():
    # then load data, process and make positional decision
    for ticker in etl.everything:
        df= readPickle(_m + ticker, '2019-01-01', '2021-05-09')
        
        ema_application = etl.maDailyData(df)
        full_output, returns, tradeCount, startDate, endDate = etl.longOverlay(ema_application)
        # df_out = appendToDF(df_out, ticker, returns, tradeCount, startDate, endDate)
        print(ticker, returns[0], returns[1], returns[2], returns[3])
        # other rankinig indicator needed: MACD bar linear slope, last 20 days? MACD signal positive? by how much vs the other lines
        # with open('trading_position_' + getOffSetFromToday(), 'a') as output:
        #     output.write(ticker + ": " + full_output['Position'].iloc[-1] + ": " + returns + '\n')
        
        # plotFinalResult(full_output)
    # etl.strat_compare(df_out)

def run_one(ticker):
    df= readPickle(_m + ticker)
    ema_application = etl.maDailyData(df)
    full_output, returns, tradeCount, startDate, endDate = etl.longOverlay(ema_application)
    print(returns, tradeCount, startDate)
    plotFinalResult(full_output)

# column_names = ['ticker','my_ema_relative_return','buy_hold_relative_return' ,'naive_ema_crossover_relative_return', 
#         'number_of_trades', 'start_date', 'end_date', 'duration_in_month', 'duration_in_year']
# df_out = pd.DataFrame(columns = column_names)

run_one('SPY')
# run_all()
# for ticker in etl.everything:
#     df= readPickle(_m + ticker, '2019-01-01', '2021-05-09')
#     ema_application = etl.maDailyData(df)
#     full_output, returns, tradeCount, startDate, endDate = etl.newStrategy(ema_application)
#     print('==========================' + ticker + '==========================')
#     print(returns, tradeCount)
#     full_output, returns, tradeCount, startDate, endDate = etl.longOverlay(ema_application)
#     print(returns, tradeCount)
#     print('==========================' + ticker + '==========================')
#     # plotFinalResult(full_output)
