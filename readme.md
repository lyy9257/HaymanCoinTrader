# HAYMAN CRYPTO TRADER

## 개요 
코인 데이터 수집, 분석, 백테스팅, 실제트레이딩

## 사용방법

### 1. config 작성
* config_example.cfg 파일을 작성합니다.

        # API 설정(API 키, 바이낸스만 지원)
        [API]
        BINANCE_PUBLIC = (바이낸스 퍼블릭 api키)
        BINANCE_SECRET = (바이낸스 프라이빗 api 키)

        # Database 설정(저장할 DB)
        [DATABASE]
        DB_IP = (MySQL DB IP)
        DB_ID = (DB 접속아이디)
        DB_PW = (DB 접속비번)
        DB_PORT = (DB 접속포트)

* config.cfg 파일로 저장합니다.

### 2. 데이터 수집 
* coin_data 라는 이름을 가지는 database를 만들어줍니다.
* get_data.py 파일을 실행합니다.
    
        * 수집되는 티커 목록
        'BTCUSDT', 'ETHUSDT', 'ETHBTC', 'XRPUSDT',
        'BTCBUSD', 'ETHBUSD', 'XRPBUSD','XRPBTC'

        * 수집되는 타임 인터벌
        5분, 15분, 30분, 1시간

        * 저장 테이블 이름
        binance_(타임 인터벌) 

### 3. 백테스트
* coin_backtest 라는 이름을 가지는 database를 만들어줍니다.
* example.py 파일에 전략을 작성합니다.

        example.py 파일을 수정하여
        매수로직, 매도로직, 매수가, 매도가 설정을 합니다.

* backtest.py 파일을 실행합니다.
        
        백테스트가 수행이 되며,
        결과는 backtest_result table에 요약 결과가,
        history_전략명_날짜_시간 table에 전체 결과가 저장됩니다.

## 참고한 글
[바이낸스, 비트맥스 분봉 통째로 받기](https://medium.com/swlh/retrieving-full-historical-data-for-every-cryptocurrency-on-binance-bitmex-using-the-python-apis-27b47fd8137f)
