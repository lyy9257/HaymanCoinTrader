import pandas as pd
import talib
import time

### 타 폴더에 있는 패키지 사용을 위해 연결
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import Collect.mysql_con

# 전략 템플릿
class StrategyTemplate():
    
    ## 초기화
    def __init__(self):

        ### Backtest Parameter 설정
        self.strategy_name = ' '
        self.broker = ' '
        self.time_interval = ' '
        self.trade_target = ' '

        self.price_db = Collect.mysql_con.SearchPriceLog(
            self.broker,  self.time_interval
            )
        
    ## 가격 데이터 호출
    ## input : x (초기화 때 설정한 타임 인터벌, 티커, 브로커 기반으로 호출)
    ## output : price_data
    def call_price_data(self):
        price_data = self.price_db.price_data(self.trade_target)[::-1]
        price_data = price_data.drop_duplicates().reset_index(drop=True) ## 중복데이터 삭제
        
        return price_data

    ## 지표 데이터 추가
    ## input : price data
    ## output : ta_added_data (기술적 분석 데이터가 추가된 데이터)
    def make_ta_data(self, price_data):       
        
        ### 지표 제작용 데이터 연결
        _open = price_data['Open']
        _high = price_data['High']
        _low = price_data['Low']
        _close = price_data['Close']
        _volume = price_data['Volume']

        ### 지표추가
        ### 여기서 부터 사용자가 원하는 대로 수식 작성
        
        return price_data

    
    ## 매수타점 추가
    ## 특정 조건에 대해서 True, False로 반환될 수 있게
    ## 수식을 작성하면 됩니다.
    ## input : Dataframe each row
    ## output : bool(True, False)
    def make_buy_signal(self, row):
        
        ### 매수타점 산출식 작성
        something = True
        
        ### 산출식 결과가 True면 집행
        if something == True:
            return True
        
        else:
            return False
        
    ## 매도타점 추가
    ## 특정 조건에 대해서 True, False로 반환될 수 있게
    ## 수식을 작성하면 됩니다.
    ## input : Dataframe each row
    ## output : bool(True, False)
    def make_sell_signal(self, row):
        
        ### 매도타점 산출식 작성
        something = True
        
        ### 산출식 결과가 True면 집행
        if something == True:
            return True
        
        else:
            return False
    
    ## 매수가 설정
    def make_buy_price(self):

        return True
        
    ## 매도가 설정
    def make_sell_price(self):
        return True
