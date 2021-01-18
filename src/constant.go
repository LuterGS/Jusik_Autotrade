package src

const (
	MQ_SETTING_FILE string = "MQ_VALUE.txt"
	DB_SETTING_FILE string = "DB_VALUE.txt"

	MARKET_LOOKUP_MIN = 15

	SIG_A_HOUR, SIG_A_MIN = 3, 55                // 점검을 시작하는 시간
	SIG_B_HOUR, SIG_B_MIN = 5, 30                // 점검을 끝내는 시간
	SIG_C_HOUR, SIG_C_MIN = 9, MARKET_LOOKUP_MIN // 단타 트레이더를 시작하는 시간
	SIG_D_HOUR, SIG_D_MIN = 14, 30               // 단타 트레이더 종료 및 AI 트레이더 시작하는 시간
	SIG_E_HOUR, SIG_E_MIN = 15, 19               // 장마감 시간

	ONE_JONGMOK_PRICE = 500000 // 한 종목에 투자할 금액수
	TOTAL_JONGMOK_NUM = 6      // 구매할 종목 수

	CUR_TRADE_MARKET = MARKET_KOSDAQ // 현재 거래할 주식시

	MAX_PROFIT_PERCENT = 3
	MAX_LOSS_PERCENT   = 1

	END_DANTA_SELL_ALL = true //true시 단타 종료하면 모든 주식 팔음, false시 놔둠

	//=================== 아래는 건드리지 말 것 ==========================
	MARKET_KOSDAQ = "101" //코스닥 시장을 의미
	MARKET_KOSPI  = "001" //코스피 시장을 의미
	MARKET_ALL    = "000" //코스닥 + 코스피 시장을 의미
)
