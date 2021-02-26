# 필요 패키지 호출
import pandas as pd
import pymysql
import os
import sys
import time

# 타 폴더에 있는 패키지 사용을 위해 연결
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# 커스텀 패키지
import Collect.mysql_con

# 전략
from Strategy import envelop

# 백테스트 Class
# 현물 롱만 지원
class Backtest():
    def __init__(self):
        self.strategy = envelop.StrategyTemplate()
        
    ## 백테스트 준비
    def _init_backtest(self):
        print('==================================================')
        print('< Backtest Option >')
        print('- Strategy name : %s' %self.strategy.strategy_name)
        print('- Broker : %s' %self.strategy.broker)
        print('- Time interval : %s' %self.strategy.time_interval)
        print('- Trade Target : %s' %self.strategy.trade_target)
        print('==================================================')
        print('< Basket Option >')
        print('- Start Amount : ')
        print('- Margin : ')
        print('- [Future] Max_Long_Ratio :')
        print('- [Future] Max_Short_Ratio  :')
        print('==================================================')

        return True

    ## 시뮬레이션
    def _simulation(self):
        raw_data = self.strategy.call_price_data()
        ta_add_data = self.strategy.make_ta_data(raw_data)
        ta_add_data['Buy'] = ta_add_data.apply(lambda x: self.strategy.make_buy_signal(x), axis=1)

        ### 최초 백테스트 환경설정
        start_seed = 100
        row_amount = len(ta_add_data.index)
        print('[INFO] Start Backtest')
        k = 1
        position = 'Empty'
        position_list = []

        for r in ta_add_data.iterrows():
            row = r[1]
            # print('[INFO] (%s-%s)' %(k, row_amount))
            # print('[INFO] Now Position is %s' %position)
            
            ### 제로 포지션 
            if position == 'Empty':
                if row['Buy'] == True:
                    position = 'PreBuy'
                else:
                    pass

            ### 매수예정(시가매수)
            elif position == 'PreBuy':
                # print('[INFO] Buy at Start')
                position = 'Buy'
                buy_price = row['Open']

            ### 매수포지션 있음, 매도감시
            elif position == 'Buy':
                if self.strategy.make_sell_signal(row) == True:
                    # print('[INFO] Sell Next Start Time')
                    position = 'PreSell'
                
                else:
                    pass
                
            ### 매도예정(시가매도)
            elif position == 'PreSell':
                # print('[INFO] Sell at Start')
                position = 'Empty'
                sell_price = row['Open']

            else:
                return False
            
            position_list.append(position)
            k += 1

        ta_add_data['Trade'] = position_list

        result = ta_add_data
        del ta_add_data

        return result

    ## 백테스트 결과 생성
    def _make_backtest_result(self):
        return True

    ## 요약 결과 저장
    def _save_describe_result(self):
        return True

    ## 전체 트레이딩 히스토리 저장
    def _save_history(self):
        return True

    ## 전체 루틴
    def start(self):
        start = time.time()

        ### 시뮬레이션 시작
        self._init_backtest()
        self._simulation()
        
        end = time.time()
        print('총 소요시간 : %2.f Sec.' %(end - start))

# 메인 실행 시
if __name__ == '__main__':
    sim = Backtest()
    sim.start()
    
    