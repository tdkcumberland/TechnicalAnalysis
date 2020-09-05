from datetime import datetime
import pandas as pd

def getDate():
    '''
    Get today's date to name the downloaded data
    '''
    return datetime.today().strftime('%Y-%m-%d')

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