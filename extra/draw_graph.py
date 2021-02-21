import pandas as pd
import numpy as np
import plotly.graph_objects as go

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

from datetime import datetime
from mpl_finance import candlestick_ohlc

df = pd.read_csv('ETHUSDT-5m-data.csv').loc[340000:, ['open', 'high', 'low', 'close', 'volume', 'trades']]
print(df.describe())

## 그래프 그림
fig = plt.figure(figsize=(8, 5))
fig.set_facecolor('w')

gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])

axes = []
axes.append(plt.subplot(gs[0]))
axes.append(plt.subplot(gs[1], sharex=axes[0]))
axes[0].get_xaxis().set_visible(False)

x = np.arange(len(df.index))
ohlc = df[['open', 'high', 'low', 'close']].astype(int).values
dohlc = np.hstack((np.reshape(x, (-1, 1)), ohlc))

# 봉차트
candlestick_ohlc(axes[0], dohlc, width=0.5, colorup='r', colordown='b')

# 거래량 차트
axes[1].bar(x, df['volume'], color='k', width=0.6, align='center')

plt.tight_layout()
plt.show()