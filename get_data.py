
# IMPORTS
import pandas as pd
import math
import os.path
import time
from bitmex import bitmex
from binance.client import Client
from datetime import timedelta, datetime
from dateutil import parser
from tqdm import tqdm_notebook #(Optional, used for progress-bars)

class GetData():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.prev_path + '\config.cfg', encoding = 'utf-8')

        ### Read config about database
        self.db_ip = self.config.get('DATABASE', 'DB_IP')
        self.db_port = self.config.get('DATABASE', 'DB_PORT')
        self.db_id = self.config.get('DATABASE', 'DB_ID')
        self.db_pw = self.config.get('DATABASE', 'DB_PW')

        ### API
        self.binance_api_key = self.config.get('API', 'BINANCE_PUBLIC')    #Enter your own API-key here
        self.binance_api_secret = self.config.get('API', 'BINANCE_SECRET') #Enter your own API-secret here

        ### CONSTANTS
        self.binsizes = {"1m": 1, "5m": 5, "1h": 60, "1d": 1440}
        self.binance_client = Client(api_key = binance_api_key, api_secret = binance_api_secret)

    ### FUNCTIONS
    def minutes_of_new_data(self, symbol, kline_size, data, source):
        if len(data) > 0:
            old = parser.parse(data["timestamp"].iloc[-1])
        if source == "binance":
            old = datetime.strptime('1 Jan 2015', '%d %b %Y')
            new = pd.to_datetime(self.binance_client.get_klines(symbol=symbol, interval=kline_size)[-1][0], unit='ms')
        return old, new

    # 바이낸스 데이터
    def get_all_binance(symbol, kline_size, save = False):
        filename = '%s-%s-data.csv' % (symbol, kline_size)

        if os.path.isfile(filename):
            data_df = pd.read_csv(filename)
        else:
            data_df = pd.DataFrame()

        oldest_point, newest_point = self.minutes_of_new_data(symbol, kline_size, data_df, source = "binance")
        delta_min = (newest_point - oldest_point).total_seconds()/60
        available_data = math.ceil(delta_min/self.binsizes[kline_size])

        if oldest_point == datetime.strptime('1 Jan 2014', '%d %b %Y'):
            print('Downloading all available %s data for %s. Be patient..!' % (kline_size, symbol))
        else:
            print('Downloading %d minutes of new data available for %s, i.e. %d instances of %s data.' % (delta_min, symbol, available_data, kline_size))

        klines = self.binance_client.get_historical_klines(
            symbol, kline_size, oldest_point.strftime("%d %b %Y %H:%M:%S"), newest_point.strftime("%d %b %Y %H:%M:%S")
        )

        data = pd.DataFrame(
            klines, columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ]
            )
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')

        if len(data_df) > 0:
            temp_df = pd.DataFrame(data)
            data_df = data_df.append(temp_df)

        else:
            data_df = data

        data_df.set_index('timestamp', inplace=True)
        
        if save:
            data_df.to_csv(filename)
        
        print('All caught up..!')

        return data_df

if __name__ == '__main__':
    ticker_list = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'ADAUSDT']

    for t in ticker_list:
        data = get_all_binance(t, '5m', save = True)