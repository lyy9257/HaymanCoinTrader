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
        
        self.strategy_name = 'Envelop' ### 로직 이름
        self.price_db = Collect.mysql_con.SearchPriceLog('Binance', '15m') ### 데이터 커넥션
        self.trade_target = 'BTCUSDT' ### 트레이딩 타겟
    
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
        
        return ta_added_data

    ## 매수타점 추가
    def _make_buy_signal(self, row):

        ''' 
        * 작성방법 *
        입력을 DataFrame Index를 받습니다.
        인덱스 데이터를 기반으로
        체크한 결과가 True or False가 출력되게 작성합니다.
        '''

        if x == True: 
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
    