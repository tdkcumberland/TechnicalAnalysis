# Technical Analysis - Trending following

Came across several books by Michael W. Covel, Andrew Abraham and Andreas Clenow on trending following and other various pure technical trading strategies so I decided to create a python script to mimic what the standard trading platform tools would provide for trending following strategy (i.e. EMA, MACD, ATR, etc...)

The idea of limitting the downside (predictable & managable risk) and letting profit runs (unlimited upside) really appeals to me. In a way, this is the real life implementation of an antifragile system/strategy described by Nassim Taleb in his Incerto series, especially "Antifragile".

Currently applying this to trade a practice account on CME as well as my real stock portfolio and as self examination to see if I have the disipline as well as the ability to remove emotion when trading which (imho) the most important aspect to technical trading.

### Data source
Stock price data are taken from Alpha Advantage throug the pandas.DataReader wrapper. You will need a API key (free). More details here: [AlphaVantage Documentation](https://www.alphavantage.co/documentation/)

### The strategy
EMA cross over with ATR stops and in the direction of MACD
| Steps | Description |
| ------ | ------ |
|Investment Universe| As many as you can to diversify lower risk|
| Screen Markets | High Volume (front future > 10000) + Strong trend (EMA100 + MACD)|
|Trading Rule|
| Entry | Long: MA10 > MA100 AND MACD > 0 AND MACD > SIGNAL AND UPWARD SLOPE  |
||Short: MA10 < MA100 AND MACD < 0 AND MACD < SIGNAL AND DOWNWARD SLOPE |
| Risk/Position Sizing | INITIAL HARD STOP: $1000 (or 1% of your trading account equity)|
||Once price move beyond HARD STOP, starting moving the ATR with spot price with rachet (only UP/DOWN when LONG/SHORT)|
| Re-entry | New HIGH/LOW on LONG/SHORT current trend |

### Configuration
One can modify the model's key parameters (short, medium, long term EMA period, daily or weekly timeframe; ATR period) through ```config.ini``` along with the API key for Alpha Vantage.

```ini
[DEFAULT]
apiKey=[APIKEY]
path=dataStore

[weekly_param]
weekly_atr_span=1
weekly_atr_multi=3
weekly_atr_trend_change_multi=0.5
weekly_short_ma_span=12
weekly_long_ma_span=26
weekly_macd_signal_span=9

[daily_param]
#default: 21
daily_atr_span=21
#default: 3
daily_atr_multi=3
#default: 0.5
daily_atr_trend_change_multi=0.5
#default: 10
daily_short_ma_span=10
#default: 55
daily_medium_ma_span=55
#default: 100
daily_long_ma_span=100
```

### Modules
Starting with ```TrendFollowing.py```, one can defines the ticker of interest:

```python
#data destination folder
_m = './dataStore/' 
#ticker
_t =  'SPEM' 
#daily or weekly timeframe
_d = 'daily' 
#create name of the downloaded datafile by concating ticker + today's date + timeframe
_nd = _t + '-' + getDate() + '-' + _d 
_nw = _t + '-' + getDate() + '-' + _d
#the start date for the analysis
_sd = '2019-09-01'
#the end date for the analysis
_ed = getDate()
#initialize ETL module
etl = ETL()
```

To start downloading the data:

```python
# download data
_name = etl.getData(ticker=_t, duration=_d)
```

To load data and process through the ETL pipeline and plotting

```python
#load data
df= readPickle(_m + _nd, _sd,_ed)

#this will analyze all the of the available data 
#rather than a limited window defined by _sd and _ed
# df= readPickle(_m + _n)

# get plots
plotDailyMA(etl.maDailyData(df), _nd)
```

```etl.py``` modulu handles all data clean and analysis while ```plotting.py``` handle the data output from ```etl.py``` in a streamline way to create the plots.

### Example output

Below is an example output of SPEM ticker from September 2019 to September 2020, showing all three EMA lines in the top subplot. These features are very standard for every single trading platform tool out there. However, the position logic, the stops and rachet mechanism for the stops are not something I see often. The bottom subplot is showing the stops for long and short position determine by the trading rule. A rachet mechanism is also implemented so that the stop doesn't move in the opposite direction to the current position.

![SPEM](https://github.com/tdkcumberland/TechnicalAnalysis/blob/master/Example.png)

If interested, one can also plot the MACD and ATR to inspect how the stops come about.


### Back test:

Below is back test of VTI (total market ETF) going back to 2020-01-01. From this it is clear that this strategy is defensive one. I will only outperform the market if there's a large drop of at least the defined stop loss. Else due to the delay nature of the moving average signal, I will under perform the market.

This is strategy would be good as an active volatility segment of a portfolio to guard against negative market volatility. In a long secular bull market, this strategy will under perform buy and hold.

![VTI](https://github.com/tdkcumberland/TechnicalAnalysis/blob/master/VTI_strategies_return.png)

