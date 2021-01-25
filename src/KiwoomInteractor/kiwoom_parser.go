package KiwoomInteractor

import (
	"strconv"
	"strings"
)

type tradeBuyType string
type parser func(string) [][]interface{}

const (
	qrBalance         string = "0"
	qrGetPastMinData  string = "1"
	qrGetHighestRaise string = "2"
	qrBuyJusik        string = "3"
	qrSellJusik       string = "4"
	qrGetProfit       string = "5"
	qrGetJogunsik     string = "6"
	qrProgramRestart  string = "7"
	qrGetPastDayData  string = "8"
	qrGetJisuDayData  string = "9"
	qrGetKoreanName   string = "10"

	qrJijungGaTrade tradeBuyType = "00"
	qrSijangGaTrade tradeBuyType = "03"
)

func parseFunc() []parser {
	return []parser{
		_parseOneData,        //0
		_parsePastData,       //1
		_parseHighestRaise,   //2
		_parseOneData,        //3
		_parseOneData,        //4
		_parseProfit,         //5
		_parseJogunsik,       //6
		_parseProgramRestart, //7
		_parsePastData,       //8
		_parsePastData,       //9
		_parseOneData,        //10
	}
}

func parseKoreanNameInput(code string) string {
	return qrGetKoreanName + "," + code
}

func parseTradeJusikInput(tradeType string, code string, amount string, price string, howToTrade tradeBuyType) string {
	if tradeType == qrBuyJusik {
		return tradeType + ",1," + code + "," + amount + "," + price + "," + string(howToTrade)
	} else {
		return tradeType + ",2," + code + "," + amount + "," + price + "," + string(howToTrade)
	}
}

func parseJogunSik(jogunsikNum int) string {
	jogunsikStr := strconv.Itoa(jogunsikNum)
	return qrGetJogunsik + "," + jogunsikStr
}

func parseMinData(code string, iter bool) string {
	if !iter {
		return qrGetPastMinData + "," + code + ",0"
	} else {
		return qrGetPastMinData + "," + code + ",2"
	}
}

func parseDayData(reqNum string, code string, day string, iter bool) string {
	if !iter {
		return reqNum + "," + code + "," + day + ",0"
	} else {
		return reqNum + "," + code + "," + day + ",2"
	}
}

//market은 constant에 있는 MARKET_* 를 참고할 것
//isPercent는 급증률로 조회할 것인지를, isMin은 몇 분별로 조회할 것인지를 (아닐시 전일 조회) 표기함
//거래량급증요청시 입력값을 parsing해주는 함수
func parseHighestRaiseInput(market string, isPercent bool, isMin bool) string {

	var isPercentString string
	var isMinString string
	lastMinString := strconv.Itoa(MARKET_LOOKUP_MIN)
	if isPercent {
		isPercentString = "2"
	} else {
		isPercentString = "1"
	}
	if isMin {
		isMinString = "1"
	} else {
		isMinString = "2"
		lastMinString = ""
	}

	inputValue := qrGetHighestRaise + "," + lastMinString + "," + market + "," + isPercentString + "," + isMinString
	return inputValue
}

// Queue에서 받은 데이터의 종류와 값에 따라 올바른 값을 parse해서 넘겨준다.
func queueOutputToData(rawFuncNum string, inputValue string) [][]interface{} {

	//error check
	if inputValue == "FAIL" {
		Timelog("키움증권 요청이 실패했습니다. 재시도합니다.")
		return _parseOneData("ERROR")
	} else if inputValue == "" {
		Timelog("Windows Queue 요청이 실패했습니다. 재시도합니다.")
		return _parseOneData("ERROR")
	}

	funcNumInt, err := strconv.Atoi(strings.Split(rawFuncNum, ",")[0])
	if err != nil {
		Timelog("숫자 변환시 에러가 발생했습니다.")
		panic("숫자 변환시 에러가 발생했습니다.")
	}

	parseFunc := parseFunc()
	return parseFunc[funcNumInt](inputValue)
}

func _parseOneData(inputValue string) [][]interface{} {
	returner := make([][]interface{}, 1)
	returner[0] = make([]interface{}, 1)
	returner[0][0] = inputValue
	return returner
}

// Sliced된 길이가 4인 배열에서, 각각의 값은 다음을 의미한다.
// 종목코드, 종목이름, 현재주식금액, 총거래액
func _parseHighestRaise(inputValue string) [][]interface{} {

	outputRawSeperated := strings.Split(inputValue, "/")
	outputSlice := make([][]interface{}, len(outputRawSeperated)-1)
	for i := range outputSlice {
		outputSlice[i] = make([]interface{}, 4)
		splitted := strings.Split(outputRawSeperated[i], ",")
		for index, data := range splitted {
			outputSlice[i][index] = data
		}
	}
	//Timelog(outputSlice)
	return outputSlice
}

// Sliced된 길이가 6인 배열에서, 각각의 값은 다음을 의미한다.
// 체결시간, 현재가, 거래량, 시가, 고가, 저가
func _parsePastData(inputValue string) [][]interface{} {

	outputRawSeperated := strings.Split(inputValue, "/")
	outputSlice := make([][]interface{}, len(outputRawSeperated)-1)
	for i := range outputSlice {
		outputSlice[i] = make([]interface{}, 6)
		splitted := strings.Split(outputRawSeperated[i], ",")
		outputSlice[i][0] = splitted[0]
		for index, data := range splitted[1:] {
			intData, _ := strconv.Atoi(data)
			outputSlice[i][index+1] = intData
		}
	}
	return outputSlice
}

// Sliced된 길이가 8인 배열에서, 각각의 값은 다음을 의미한다.
// 종목코드, 종목이름, 주식보유수, 주식총구매금액, 현재주식평가금액, 손익금액, 손익퍼센트, 현재주식가격
// 각각 string, string, int, int, int, int, float32, int임
func _parseProfit(inputValue string) [][]interface{} {

	outputRawSeperated := strings.Split(inputValue, "/")
	jusikNum, _ := strconv.Atoi(outputRawSeperated[0])
	outputSlice := make([][]interface{}, jusikNum)

	for i := range outputSlice {
		outputSlice[i] = make([]interface{}, 8)
		splitted := strings.Split(outputRawSeperated[i+1], ",")
		outputSlice[i][0] = splitted[0]
		outputSlice[i][1] = splitted[1]
		outputSlice[i][2], _ = strconv.Atoi(splitted[2])
		outputSlice[i][3], _ = strconv.Atoi(splitted[3])
		outputSlice[i][4], _ = strconv.Atoi(splitted[4])
		outputSlice[i][5], _ = strconv.Atoi(splitted[5])
		temp, _ := strconv.ParseFloat(splitted[6], 32)
		outputSlice[i][6] = float32(temp)
		outputSlice[i][7], _ = strconv.Atoi(splitted[7])

		for index, data := range splitted {
			outputSlice[i][index] = data
		}
	}
	//Timelog(outputSlice)
	return outputSlice
}

// 2차배열이지만, [0][n] 크기의 배열이다.
func _parseJogunsik(inputValue string) [][]interface{} {

	outputSeperated := strings.Split(inputValue, ",")
	outputSlice := make([][]interface{}, 1)
	outputSlice[0] = make([]interface{}, len(outputSeperated))
	for index, data := range outputSeperated {
		outputSlice[0][index] = data
	}
	return outputSlice
}

// !1234 같이, 느낌표 뒤에 숫자가 있는 것을 걸러낸다.
func _parseProgramRestart(inputValue string) [][]interface{} {
	return _parseOneData(inputValue[1:])
}
