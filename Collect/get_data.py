
# IMPORTS
import configparser
import datetime
import pandas as pd
import math
import os.path
import time

from binance.client import Client
from datetime import timedelta, datetime
from dateutil import parser
from tqdm import tqdm_notebook #(Optional, used for progress-bars)

from mysql_con import CoinPriceLog

## 데이터 호출
class Binance():
    def __init__(self, kline_size):        

        ### input data
        self.kline_size = kline_size

        ### get prev path 
        self.prev_path = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))

        self.config = configparser.ConfigParser()
        self.config.read(self.prev_path + '\config.cfg', encoding = 'utf-8')

        ### API
        self.binance_api_key = self.config.get('API', 'BINANCE_PUBLIC')    #Enter your own API-key here
        self.binance_api_secret = self.config.get('API', 'BINANCE_SECRET') #Enter your own API-secret here

        ### CONSTANTS
        self.binsizes = {"1m": 1, "5m": 5, "15m": 15,  "30m": 30, "1h": 60, "1d": 1440}
        self.binance_client = Client(
            api_key = self.binance_api_key, api_secret = self.binance_api_secret
        )

        ### Database
        self.coin_db = CoinPriceLog('binance', self.kline_size)
        
    ## FUNCTIONS
    def _minutes_of_new_data(self, symbol, data):

        if len(data) > 0:
            last_time = str(data["Date"].iloc[-1] * 1000000 + data["Time"].iloc[-1])
            old = datetime.strptime(last_time,'%Y%m%d%H%M%S')
        else:
            old = datetime.strptime('1 Jan 2015', '%d %b %Y')
            
        new = pd.to_datetime(
            self.binance_client.get_klines(symbol=symbol, interval=self.kline_size)[-1][0], unit='ms'
        )
        
        return old, new

    ### 티커 리스트 호출
    def get_ticker_list(self, filter_opt):
        all_list = pd.DataFrame(self.binance_client.get_ticker())['symbol']
        ticker_list = all_list[all_list.str.slice(start=-4) == filter_opt].reset_index(drop=True)
        
        return ticker_list
    
    ### 바이낸스 주가 데이터 호출
    def price_data(self, symbol, save = False):

        ### 기존 존재 데이터 확인                           
        try:
            data_df = self.coin_db.search_last_update_data(symbol)
        except:
            data_df = pd.DataFrame()

        oldest_point, newest_point = self._minutes_of_new_data(symbol, data_df)
        delta_min = (newest_point - oldest_point).total_seconds()/60
        available_data = math.ceil(delta_min/self.binsizes[kline_size])

        if oldest_point == datetime.strptime('1 Jan 2014', '%d %b %Y'):
            print('[INFO] Downloading all available %s data for %s. Be patient..!'
            % (self.kline_size, symbol)
            )

        else:
            print('[INFO] Downloading %d minutes of new data available for %s, i.e. %d instances of %s data.'
            % (delta_min, symbol, available_data, self.kline_size)
            )

        klines = self.binance_client.get_historical_klines(
            symbol, self.kline_size, oldest_point.strftime("%d %b %Y %H:%M:%S"), newest_point.strftime("%d %b %Y %H:%M:%S")
        )

        data = pd.DataFrame(
            klines, columns = [
                'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time',
                'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'
                ]
            )

        data['DateTime'] = pd.to_datetime(data['Time'], unit='ms')
        data['Date'] = data['DateTime'].apply(lambda x: x.strftime('%Y%m%d')).astype(int)
        data['Time'] = data['DateTime'].apply(lambda x: x.strftime('%H%M%S')).astype(int)
        data['Ticker'] = [symbol for x in range(len(data.index))]
        
        data = data.drop(columns=['DateTime', 'Close_time', 'ignore'])
        data = data[['Ticker', 'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume',
            'quote_av', 'trades', 'tb_base_av', 'tb_quote_av']]
       
        print("[INFO] Received Data length is %s." %len(data.index))

        return data

    ## DB에 저장
    def save_to_database(self, data):
        self.coin_db.save(data)
  
if __name__ == '__main__':
    ticker_list = ['BTCUSDT', 'ETHUSDT', 'ETHBTC' , 'XRPUSDT',
        'BTCBUSD', 'ETHBUSD', 'XRPBUSD', 'XRPBTC']

    kline_size = '15m'    

    bi = Binance(kline_size)
    
    # ticker_list = get.get_ticker_list('USDT')

    for ti in ticker_list:
        data = bi.price_data(ti)
        bi.save_to_database(data)

   