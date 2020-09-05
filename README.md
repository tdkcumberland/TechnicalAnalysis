# Technical Analysis - Trending following

Came across several books by Michael W. Covel, Andrew Abraham and Andreas Clenow on trending following and other various pure technical trading strategies so I decided to create a python script to mimic what the standard trading platform tools would provide for trending following strategy (i.e. EMA, MACD, ATR, etc...)

The idea of limitting the downside (predictable & managable risk) and letting profit runs (unlimited upside) really appeals to me. In a way, this is the real life implementation of an antifragile system/strategy described by Nassim Taleb in his Incerto series, especially "Antifragile".

Currently applying this to trade a practice account on CME as well as my real stock portfolio and as self examination to see if I have the disipline as well as the ability to remove emotion when trading which (imho) the most important aspect to technical trading.

### Data source
Stock price data are taken from Alpha Advantage throug the pandas.DataReader wrapper. You will need a API key (free). More details here: [AlphaVantage Documentation](https://www.alphavantage.co/documentation/)

###The strategy
EMA cross over with ATR stops and in the direction of MACD
| Steps | Description |
| ------ | ------ |
|Investment Universe| As many as you can to diversify lower risk|
| Screen Markets | High Volume (front future > 10000) + Strong trend (EMA100 + MACD)|
|Trading Rule|
| Entry | Long: MA10 > MA100 AND MACD > 0 AND MACD > SIGNAL AND UPWARD SLOPE  |
||Short: MA10 < MA100 AND MACD < 0 AND MACD < SIGNAL AND DOWNWARD SLOPE |
| Risk/Position Sizing | INITIAL HARD STOP: $1000|
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
```etl.py``` modulu handles all data clean and analysis while ```plotting.py``` handle the data output from ```etl.py``` in a streamline way to create the plots.

### Example output
![SPEM](https://github.com/tdkcumberland/TechnicalAnalysis/Example.png)
