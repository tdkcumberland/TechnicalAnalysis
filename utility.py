from datetime import datetime
from datetime import timedelta
import pandas as pd
import numpy as np

def getDate():
    '''
    Get today's date to name the downloaded data
    '''
    return datetime.today().strftime('%Y-%m-%d')

def getOffSetFromToday(days=1):
    _ = datetime.today() + timedelta(days=days)
    return _.strftime('%Y-%m-%d')

def readPickle(pickleName, startDate="", endDate=""):
    _tmp = pd.read_pickle(pickleName)
    _tmp.sort_index(inplace=True)
    if startDate =="" or endDate == "":
        return _tmp
    elif startDate !="" and endDate != "":
        return _tmp.loc[startDate : endDate]
    else:
        print('PARAMETERS...')
        return

def dumpData(df, name):
    """
    Dump data to a pickle file
    df : pandas dataframe
    name : str
        pickle file name
    """
    df.to_pickle(name)

def convertNP_datetime_to_py_datetime(datetime64):
    unix_epoch = np.datetime64(0, 's')
    one_second = np.timedelta64(1, 's')
    seconds_since_epoch = (datetime64 - unix_epoch) / one_second
    return datetime.utcfromtimestamp(seconds_since_epoch)

def appendToDF(df_out, ticker, returns,tradeCount, startDate, endDate):
    startDate = convertNP_datetime_to_py_datetime(startDate)
    endDate = endDate.to_pydatetime()
    duration_month = (endDate.year - startDate.year) * 12 + (endDate.month - startDate.month)
    duration_year = (endDate.year - startDate.year)
    df_out = df_out.append(dict(zip(df_out.columns, [ticker,*returns,tradeCount, startDate, endDate, duration_month, duration_year])), ignore_index=True)
    return df_out