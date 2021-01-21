package KiwoomInteractor

type Jisu string

const (
	MQ_SETTING_FILE string = "MQ_VALUE.txt"
	DB_SETTING_FILE string = "DB_VALUE.txt"

	MARKET_LOOKUP_MIN = 15

	MARKET_KOSDAQ = "101" //코스닥 시장을 의미
	MARKET_KOSPI  = "001" //코스피 시장을 의미
	MARKET_ALL    = "000" //코스닥 + 코스피 시장을 의미

	JISU_KOSDAQ Jisu = MARKET_KOSDAQ
	JISU_KOSPI  Jisu = MARKET_KOSPI
)
