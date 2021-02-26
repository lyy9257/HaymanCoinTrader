import pandas as pd
import talib
import time

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import Collect.mysql_con

# 전략 템플릿
class StrategyTemplate():
    
    ## 초기화
    def __init__(self):
        self.strategy_name = 'Envelop'
        self.price_db = Collect.mysql_con.SearchPriceLog('Binance', '15m')
        self.trade_target = 'BTCUSDT'
    
    ## 주가데이터 호출
    def call_price_data(self):
        price_data = self.price_db.price_data(self.trade_target)[::-1].reset_index(drop=True)
        
        return price_data

    ## 적삼병, 흑삼병 체크용
    def _check_three_candle(self, price_data):
        loop_range = len(price_data.index) - 2
        
        price_data['Candle'] = price_data[['Open', 'Close']].apply(
            lambda x : x['Open'] < x['Close'] and 1 or -1 , axis=1
        ) 
        
        price_data['Candle_3'] = price_data['Candle'].rolling(3).sum().fillna(0)

    ## 지표 데이터 추가
    def make_ta_data(self, price_data):       
        open = price_data['Open']
        high = price_data['High']
        low = price_data['Low']
        close = price_data['Close']
        volume = price_data['Volume']

        self._check_three_candle(price_data)

        price_data['RSI_2'] = talib.RSI(close, timeperiod=2)
        price_data['MA_100'] = talib.MA(low, timeperiod=100, matype=0)

        upperband, middleband, lowerband = talib.BBANDS(
            close, timeperiod=15, nbdevup=2, nbdevdn=2, matype=0
        )
        price_data['BB_Upper'] = upperband
        price_data['BB_Middle'] = middleband
        price_data['BB_Lower'] = lowerband

        price_data['MA_5'] = talib.MA(close, timeperiod=5, matype=0)
        price_data['Env_5_1_Down'] = (price_data['MA_5'] * 0.99)
        price_data['Env_5_1_Down'] = (price_data['MA_5'] * 1.01)
        price_data['Vol_max_3'] = price_data['Volume'].rolling(3).max()

        price_data = price_data.fillna(0).round(2)
        
        return price_data

    ## 매수타점 추가
    def _make_buy_signal(self, row):
        cnt = 0
        if row['RSI_2'] < 10:
            cnt += 1
        
        if row['Candle_3'] == -3:
            cnt += 1

        if row['Volume'] == row['Vol_max_3']:
            cnt +=1

        if row['Low'] < row['Env_5_1_Down']:
            cnt +=1 

        if cnt == 4:
            return True
        
        else:
            return False
        
    ## 매도타점 추가
    def _make_sell_signal(self, row):
        cnt = 0

        ## 익절
        if row['Close'] > row['MA_5']:
            cnt += 1
        
        ## 손절
        if row['Close'] < row['MA_100']:
            cnt += 1
        
        if cnt > 0:
            return True

        else:
            return False

        return True
        
    ## 시뮬레이션
    def simulation(self):
        raw_data = self.call_price_data()
        ta_add_data = self.make_ta_data(raw_data)
        ta_add_data['Buy'] = ta_add_data.apply(lambda x: self._make_buy_signal(x), axis=1)

        ### 최초 백테스트 환경설정
        start_seed = 100
        row_amount = len(ta_add_data.index)
        print('[INFO] Start Backtest')
        k = 1
        position = 'Empty'
        position_list = []

        for r in ta_add_data.iterrows():
            row = r[1]
            print('[INFO] (%s-%s)' %(k, row_amount))
            print('[INFO] Now Position is %s' %position)
            
            ### 제로 포지션 
            if position == 'Empty':
                if row['Buy'] == True:
                    position = 'PreBuy'
                else:
                    pass

            ### 매수예정(시가매수)
            elif position == 'PreBuy':
                print('[INFO] Buy at Start')
                position = 'Buy'
                buy_price = row['Open']

            ### 매수포지션 있음, 매도감시
            elif position == 'Buy':
                if self._make_sell_signal(row) == True:
                    print('[INFO] Sell Next Start Time')
                    position = 'PreSell'
                
                else:
                    pass
            
            elif position == 'PreSell':
                print('[INFO] Sell at Start')
                position = 'Empty'
                sell_price = row['Open']

            else:
                return False
            
            position_list.append(position)
            k += 1

        ta_add_data['Trade'] = position_list
        print(ta_add_data[ta_add_data['Trade'] != 'Empty'])

        return True
    

if __name__ == '__main__':
    start = time.time()
    
    envelop = StrategyTemplate()
    envelop.simulation()
    
    end = time.time()
    print('총 소요시간 : %2.f Sec.' %(end - start))
    