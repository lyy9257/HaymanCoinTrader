# 필요 패키지 호출
import numpy as np
import pandas as pd
import pymysql
import os
import sys
import time

from datetime import datetime

# 타 폴더에 있는 패키지 사용을 위해 연결
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# 커스텀 패키지
import Collect.mysql_con

# 전략
# example 
from Strategy import example

# 백테스트 Class
# 현물 롱만 지원
class Backtest():
    def __init__(self):
        self.strategy = example.StrategyTemplate()
        self.backtest_store = Collect.mysql_con.BackTestResult(self.strategy.strategy_name)

    ## 백테스트 준비
    def _init_backtest(self):
        print('==================================================')
        print('< Backtest Option >')
        print('- Strategy name : %s' %self.strategy.strategy_name)
        print('- Broker : %s' %self.strategy.broker)
        print('- Buying Fee : %s %%' %self.strategy.buy_fee)
        print('- Selling Fee : %s %%' %self.strategy.sell_fee)
        print('- Time interval : %s' %self.strategy.time_interval)
        print('- Trade Target : %s' %self.strategy.trade_target)
        print('==================================================')

        return True

    ## 시뮬레이션
    def _simulation(self):
        raw_data = self.strategy.call_price_data()
        ta_add_data = self.strategy.make_ta_data(raw_data)
        ta_add_data['Buy'] = ta_add_data.apply(lambda x: self.strategy.make_buy_signal(x), axis=1)

        ### 최초 백테스트 환경설정
        start_seed = 100
        print('[INFO] Start Backtest')

        position = 'Empty'
        position_list = []
        amount_profit = [start_seed]

        for r in ta_add_data.iterrows():
            row = r[1]
            
            ### 제로 포지션 
            if position == 'Empty':
                if row['Buy'] == True:
                    position = 'PreBuy_Long'
                    buy_price = self.strategy.make_buy_price(row)

                else:
                    pass
                
                amount_profit.append(amount_profit[-1])

            ### 매수예정(시가매수)
            elif position == 'PreBuy_Long':
                position = 'Buy_Long' # 다음 봉에서 매수
                
                ### 종가기준 수익률 산출
                ### 종가 / 매수가
                profit = amount_profit[-1] * row['Close'] / buy_price * (1-self.strategy.buy_fee/100)
                amount_profit.append(profit)

                ### 사용자에게 안내
                print("[INFO] Entry Long Position")
                print("[INFO] Buy Price = %s" %buy_price)

            ### 매수포지션 있음, 매도감시
            elif position == 'Buy_Long':
                if self.strategy.make_sell_signal(row) == True:
                    position = 'PreSell_Long'
                    sell_price = self.strategy.make_buy_price(row)

                
                else:
                    pass
                
                ### 종가/시가 변화율로 수익률 산정
                profit = amount_profit[-1] * row['Close'] / row['Open']
                amount_profit.append(profit)

            ### 매도예정(시가매도)
            elif position == 'PreSell_Long':
                position = 'Empty'
                sell_price = self.strategy.make_sell_price(row)
                
                ### 시가대비 매도가 수익률로 봉 기준 숭기률 산출
                profit = amount_profit[-1] * row['Open'] / sell_price * (1-self.strategy.buy_fee/100)
                amount_profit.append(profit) 
                
                print("[INFO] Exit Long Position")
                print("[INFO] Exit Price = %s" %sell_price)

                total_profit = (sell_price / buy_price - 1) * 100

                print("[INFO] Total Profit(fee ignore) = %.2f %%" %total_profit)

            else:
                return False
            
            ### 백테스트 정상 작동여부 체크
            ### 매수준비, 매도준비 포지션은 연속하여 나올 수 없으므로 에러 처리
            if len(position_list) > 0:
                if position_list[-1] == position and position == 'PreBuy_Long':
                    raise ValueError

                if position_list[-1] == position and position == 'PreSell_Long':
                    raise ValueError

            ### 현재 포지션 기록
            position_list.append(position)

        amount_profit = amount_profit[1:]
        ta_add_data['Position'] = position_list
        ta_add_data['Profit'] = amount_profit
        
        result = ta_add_data.round(6) ##
        del ta_add_data
        
        return result

    ## MDD 계산
    ## 참고 : http://blog.quantylab.com/mdd.html
    def _get_mdd(self, profit_result):
        arr_v = np.array(profit_result)
        peak_lower = np.argmax(np.maximum.accumulate(arr_v) - arr_v)
        peak_upper = np.argmax(arr_v[:peak_lower])
        
        mdd = (arr_v[peak_lower] - arr_v[peak_upper]) / arr_v[peak_upper] * 100
        mdd = round(mdd, 4) ## 4자리수까지 반올림

        return mdd

    ## 백테스트 결과 생성
    def _make_backtest_result(self, result):
        start_amount = result.iat[0, result.columns.get_loc('Profit')]
        end_amount = result.iat[-1, result.columns.get_loc('Profit')]
        total_trade_year = int(result.iat[-1, result.columns.get_loc('Date')]/10000) - int(result.iat[0, result.columns.get_loc('Date')]/10000)
        total_profit = round(result.iat[-1, result.columns.get_loc('Profit')] / result.iat[0, result.columns.get_loc('Profit')], 4) - 1  # Total Profit
        ## cagr = (total_profit ** (1/total_trade_year) - 1) * 100  
        mdd = self._get_mdd(result['Profit'])
               
        print('==================================================')
        print('< Backtest Result >')
        print('- Start Amount : %s' %start_amount)
        print('- End Amount : %s' %end_amount)
        print('- Total Trade Year : %s Year' %total_trade_year)
        print('- Total_profit : %.2f %%' %(total_profit * 100))
        print('- MDD : %.2f %%' %mdd)
        print('==================================================')
        
        ### 백테스트 결과 저장
        now = datetime.now()
        date = now.strftime("%Y%m%d") # 시작시간 
        time = now.strftime("%H%M%S") # 시작 HHMMSS
        
        describe_result = [date, time, self.strategy.strategy_name, start_amount,
            end_amount, total_trade_year, total_profit, mdd
        ] # 요약 결과
        history_result = result[['Date', 'Time', 'Open', 'High',
            'Low', 'Close', 'Volume', 'Position', 'Profit']
        ] # 전체 히스토리

        self._save_describe_result(describe_result) # 요약결과
        self._save_history(history_result, date, time) #히스토리

        return True

    ## 요약 결과 저장
    def _save_describe_result(self, result):
        self.backtest_store.save(result, 'describe', 0, 0)

        return True

    ## 전체 트레이딩 히스토리 저장
    def _save_history(self, result, date, time):
        self.backtest_store.save(result, 'history', date, time)

        return True

    ## 전체 루틴
    def start(self):
        start = time.time()

        ### 시뮬레이션 시작
        self._init_backtest() # 환경설정
        result = self._simulation() # 백테스트
        self._make_backtest_result(result) # 결과생성
        
        end = time.time()
        print('총 소요시간 : %.3f Sec.' %(end - start))

# 메인 실행 시
if __name__ == '__main__':
    sim = Backtest()
    sim.start()
    
    