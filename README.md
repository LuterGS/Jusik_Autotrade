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
* 기본적인 설정은 constant.py에서 할 수 있습니다.
* 아직 개발중이며, 현재 Windows와의 연동이 완료된 상태입니다.
    * 연동 테스트는 kiwoom_api.py를 실행시키면 가능합니다.


# Warning
* [Jusik_Autotrade_Windows](https://github.com/LuterGS/Jusik_Autotrade_Windows) 가 먼저 작동하고 있는 상태에서 이 프로그램을 실행시켜야 합니다.
    * 그 이외의 상황에서는 오류가 날 수 있습니다.
    
# Algorithm
1. 9시 ~ 지정한 시각까지는 단타 알고리즘이 거래합니다.
2. 지정한 시각 ~ 장마감까지는 AI 알고리즘이 거래합니다.

* 단타 알고리즘
    1. 9시 xx분에 개장부터 현재 시각까지의 거래량 급등량이 많은 종목을 선출해서 가져옵니다.
    2. 해당 주식들을 총 n개씩 (사용자 지정 가능) 분할해 구매합니다.
    3. 구매한 주식은 일정 손/익절 분기점을 지나면 매도합니다.
    4. 보유 주식 종류가 n개가 될 때까지 거래량이 높은 주식을 매수합니다.
    5. 단타 알고리즘 종료 시기가 오면, 설정에 따라 모두 팔거나, 가지고 있습니다.
* AI 알고리즘
    1. 현재 개발중입니다.
    

# Develop Process
* (2020.12.22) Windows Only 환경으로 개발하고 있었음
* (2020.12.24) 키움증권 API 요청 딜레이 (초당 최대 5회, 시간당 최대 1000회) 반영
* (2020.12.27) Windows, Linux 서버 분리 예정 (Windows환경에서 Signal Handling이 힘든 문제)
* (2020.12.28) Windows, Linux 서버 분리
* (2020.12.29) 단타기반 주식투자 알고리즘 기본 설계
* (2020.12.30) 알고리즘 세분화, 시그널 핸들러를 이용한 코드 최적화 및 사용자 설정 반영 (constant.py)