Jusik_Autotrade
=======================

Go를 사용해 [Jusik_Autotrade_Windows](https://github.com/LuterGS/Jusik_Autotrade_Windows) 와 통신하면서 자동으로 주식시장을 파악하고 투자하는 알고리즘입니다.
----

# Requirements
* __Linux__ (이 프로그램은 Ubuntu 20.04 desktop, x64에서 작동을 보장합니다.)
* __Go__ (1.15.6 버전 이상)
* __Go Redis, AMQP Module__
    ```shell   
    go get github.com/streadway/amqp
  go get github.com/go-redis/redis
  ```
  로 설치 가능
* __RabbitMQ Server__ : 설치 후 /setting/SAMPLE_MQ_VALUE.txt 를 참고해 MQ_VALUE.txt를 같은 위치에 만들어야 합니다.
* __Redis Server__ : 설치 후 /setting/SAMPLE_DB_VALUE.txt 를 참고해 DB_VALUE.txt를 같은 위치에 만들어야 합니다.  
* __[Jusik_Autotrade_Windows](https://github.com/LuterGS/Jusik_Autotrade_Windows)__ 가 설치된 __Windows OS__


# How to Use
* 기본적인 설정은 src/CONSTANT.go 에서 할 수 있습니다.
* 현재 단타 알고리즘만 동작하는 상태입니다.


# Warning
* __[Jusik_Autotrade_Windows](https://github.com/LuterGS/Jusik_Autotrade_Windows) 가 먼저 작동하고 있는 상태에서 이 프로그램을 실행시켜야 합니다.__
    * 그 이외의 상황에서는 오류가 날 수 있습니다.
* OS 및 커널, CPU 버전 등등의 차이에 따라 프로그램이 오작동할 가능성이 있습니다. 현재 x64 Ubuntu 20.04에서 작동을 보장합니다.  

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
* (2021.01.21) go버전으로 포팅 완료