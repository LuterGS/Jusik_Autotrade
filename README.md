Jusik_Autotrade
=======================

파이썬과 키움증권 API를 연동해, 자동으로 주식시장을 파악하고 투자하는 알고리즘입니다.
----

# Requirements
* Linux (이 프로그램은 Ubuntu 20.04 desktop, x64에서 작동을 보장합니다.)
* Python (64bit, 3.8 이상 필)
* Python 라이브러리 : pika
    ```shell   
    pip install pika
  ```
  로 설치 가능
* RabbitMQ Server
    * 설치 후 MQ_VALUE.txt에서 값을 채워넣어야 합니다.
    * 큐는 두 개가 필요하며, 하나는 Ubuntu -> Windows 로 정보를 전달하는 큐, 하나는 그 반대의 큐입니다.
    * Ubuntu -> Windows로 가는 큐를 MQ_OUT_QUEUE에, 그 반대는 MQ_IN_QUEUE에 적어주시면 됩니다.
* [Jusik_Autotrade_Windows](https://github.com/LuterGS/Jusik_Autotrade_Windows) 가 설치된 Windows OS


# How to Use
* 아직 개발중이며, 현재 Windows와의 연동이 완료된 상태입니다.
    * 연동 테스트는 kiwoom_api.py를 실행시키면 가능합니다.


# Warning
* [Jusik_Autotrade_Windows](https://github.com/LuterGS/Jusik_Autotrade_Windows) 가 먼저 작동하고 있는 상태에서 이 프로그램을 실행시켜야 합니다.
    * 그 이외의 상황에서는 오류가 날 수 있습니다.
    
# Algorithm
1. 주식 종목을 선택한다
    * KOSPI 종목의 과거 데이터를 분석해서 종목을 선별하는 인공지능이 선택
    * 그날그날 주식의 거래량 및 가격을 보고 기계적으로 종목을 선별계
        1. 9시 30분에 개장부터 30분까지의 거래액이 가장 높은 주식 10개를 선별한다 (코스닥 기준)
        2. 10개를 구매 후, 일정 수익률 이상/이하가 되면 판매한다.
2. 주식을 구매한다.
    1. 주식을 구매하면, 정해진 익/손절 퍼센트에 도달하는지를 확인한다.
    2. 해당 퍼센트에 도달하면, 무조건 익/손절한다.
    

# Develop Process
* (2020.12.22) Windows Only 환경으로 개발하고 있었음
* (2020.12.24) 키움증권 API 요청 딜레이 (초당 최대 5회, 시간당 최대 1000회) 반영
* (2020.12.27) Windows, Linux 서버 분리 예정 (Windows환경에서 Signal Handling이 힘든 문제)
* (2020.12.28) Windows, Linux 서버 분리
* (2020.12.29) 단타기반 주식투자 알고리즘 기본 설