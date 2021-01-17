package src

import (
	"strconv"
	"strings"
)

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

	inputValue := "거래량급증요청," + lastMinString + "," + market + "," + isPercentString + "," + isMinString
	return inputValue
}

// Queue에서 받은 데이터의 종류와 값에 따라 올바른 값을 parse해서 넘겨준다.
func queueOutputToData(dataType string, inputValue string) [][]string {

	//error check
	if inputValue == "FAIL" {
		Timelog("키움증권 요청이 실패했습니다. 재시도합니다.")
		return nil
	} else if inputValue == "" {
		Timelog("Windows Queue 요청이 실패했습니다. 재시도합니다.")
		return nil
	}

	if dataType == "거래량급증요청" {
		return _highestRaiseParse(inputValue)
	} else if dataType == "잔액요청" {
		return _oneDataParse(inputValue)
	} else if dataType == "수익률요청" {
		return _profitParse(inputValue)
	} else if dataType == "프로그램재시작" {
		return _oneDataParse(inputValue)
	}
	return _highestRaiseParse(inputValue)
}

func _oneDataParse(inputValue string) [][]string {
	returner := make([][]string, 1)
	returner[0] = make([]string, 1)
	returner[0][0] = inputValue
	return returner
}

// Sliced된 길이가 4인 배열에서, 각각의 값은 다음을 의미한다.
// 종목코드, 종목이름, 현재주식금액, 총거래액
func _highestRaiseParse(inputValue string) [][]string {

	outputRawSeperated := strings.Split(inputValue, "/")
	outputSlice := make([][]string, len(outputRawSeperated)-1)
	for i := range outputSlice {
		outputSlice[i] = make([]string, 4)
		outputSlice[i] = strings.Split(outputRawSeperated[i], ",")
	}
	//Timelog(outputSlice)
	return outputSlice
}

// Sliced된 길이가 8인 배열에서, 각각의 값은 다음을 의미한다.
// 종목코드, 종목이름, 주식보유수, 주식총구매금약, 현재주식평가금약, 손익금액, 손익퍼센트, 현재주식가격
func _profitParse(inputValue string) [][]string {

	outputRawSeperated := strings.Split(inputValue, "/")
	jusikNum, _ := strconv.Atoi(outputRawSeperated[0])
	outputSlice := make([][]string, jusikNum)
	for i := range outputSlice {
		outputSlice[i] = make([]string, 8)
		outputSlice[i] = strings.Split(outputRawSeperated[i+1], ",")
	}
	//Timelog(outputSlice)
	return outputSlice
}
