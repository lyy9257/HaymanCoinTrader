import pandas as pd

def RSI(series, period=2):
    delta = series.diff().dropna()
    u = delta * 0
    d = u.copy()
    u[delta > 0] = delta[delta > 0]
    d[delta < 0] = -delta[delta < 0]
    u[u.index[period-1]] = np.mean( u[:period] ) #first value is sum of avg gains
    u = u.drop(u.index[:(period-1)])
    d[d.index[period-1]] = np.mean( d[:period] ) #first value is sum of avg losses
    d = d.drop(d.index[:(period-1)])
    rs = u.ewm(com=period-1, adjust=False).mean() / \
         d.ewm(com=period-1, adjust=False).mean()
    rsi = 100 - 100 / (1 + rs)
    return rsi[-1]


class BackTest():
    def __init__(self):
        self.ticker = 'ETHUSDT'
        self.test_data = pd.read_csv('%s-5m-data.csv' %self.ticker)
        self.filtered_data = self.test_data['open', 'high', 'low', 'close', 'volume', 'trades']
    
