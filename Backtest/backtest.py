# 필요 패키지 호출
import numpy as np
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
        start_seed = 10000
        row_amount = len(ta_add_data.index)
        print('[INFO] Start Backtest')
        k = 1
        position = 'Empty'
        position_list = []
        amount_profit = [start_seed]

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
                
                amount_profit.append(amount_profit[-1])

            ### 매수예정(시가매수)
            elif position == 'PreBuy':
                # print('[INFO] Buy at Start')
                position = 'Buy'
                buy_price = row['Open']
                
                ### 시가에 매수했으므로 종가기준 수익률
                profit = amount_profit[-1] * row['Close'] / row['Open'] * (1+0.025/100)
                amount_profit.append(profit)

            ### 매수포지션 있음, 매도감시
            elif position == 'Buy':
                if self.strategy.make_sell_signal(row) == True:
                    # print('[INFO] Sell Next Start Time')
                    position = 'PreSell'
                
                else:
                    pass
                
                ### 전봉 종가 = 시가이므로 종가/시가
                profit = amount_profit[-1] * row['Close'] / row['Open']
                amount_profit.append(profit)


            ### 매도예정(시가매도)
            elif position == 'PreSell':
                # print('[INFO] Sell at Start')
                position = 'Empty'
                sell_price = row['Open']
                
                ### 전봉 시가에 팔았으므로 수익률 변동은 없음.
                ### 시장가에 팔았다 가정하고 수수료 차감
                amount_profit.append(amount_profit[-1] * (1-0.075/100))

            else:
                return False
            
            ### 현재 포지션 기록
            position_list.append(position)
            k += 1

        amount_profit = amount_profit[1:]
        ta_add_data['Trade'] = position_list
        ta_add_data['Profit'] = amount_profit
        
        result = ta_add_data.round(2)
        del ta_add_data
        
        return result

    ## MDD 계산
    ## 참고 : http://blog.quantylab.com/mdd.html
    def _get_mdd(self, profit_result):
        arr_v = np.array(profit_result)
        peak_lower = np.argmax(np.maximum.accumulate(arr_v) - arr_v)
        peak_upper = np.argmax(arr_v[:peak_lower])
        mdd = (arr_v[peak_lower] - arr_v[peak_upper]) / arr_v[peak_upper] * 100

        return mdd

    ## 백테스트 결과 생성
    def _make_backtest_result(self, result):
        total_trade_year = int(result.iat[-1, result.columns.get_loc('Date')]/10000) - int(result.iat[0, result.columns.get_loc('Date')]/10000)
        total_profit = round(result.iat[-1, result.columns.get_loc('Profit')] / result.iat[0, result.columns.get_loc('Profit')], 4)  # Total Profit
        cagr = total_profit ** (1/total_trade_year) - 1 * 100  
        mdd = self._get_mdd(result['Profit'])
               
        print('==================================================')
        print('< Backtest Result >')
        print('- Start Amount : %s' %result.iat[0, result.columns.get_loc('Profit')])
        print('- End Amount : %s' %result.iat[-1, result.columns.get_loc('Profit')])
        print('- Total Trade Year : %s Year' %total_trade_year)
        print('- Total_profit : %.2f %%' %(total_profit * 100))
        print('- CAGR : %.2f %%' %cagr)
        print('- MDD : %.2f %%' %mdd)
        print('==================================================')

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
        self._init_backtest() # 환경설정
        result = self._simulation() # 백테스트
        self._make_backtest_result(result) # 결과생성
        # 요약결과 DB에 저장
        # 상세 백테스트 결과 DB에 저장

        end = time.time()
        print('총 소요시간 : %.3f Sec.' %(end - start))

# 메인 실행 시
if __name__ == '__main__':
    sim = Backtest()
    sim.start()
    
    