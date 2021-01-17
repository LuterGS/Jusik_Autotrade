package src

import (
	"fmt"
	"io/ioutil"
	"os"
	"strings"
	"time"
)

func Timelog(a ...interface{}) {
	fmt.Print(time.Now().Format(time.StampMilli) + "\t")
	fmt.Println(a...)
}

func readFromFile(fileName string) map[string]string {

	curLoc, _ := os.Getwd()
	Timelog(curLoc + fileName)
	dbData, err := ioutil.ReadFile(curLoc + fileName)
	if err != nil {
		Timelog("파일을 불러오는 데 실패했습니다. 프로그램을 종료합니다.")
		panic("파일 Read 실패")
	}

	var fileMap map[string]string
	fileMap = make(map[string]string)
	lines := strings.Split(string(dbData), "\n")
	for i := 0; i < len(lines); i++ {
		singleLine := strings.Split(lines[i], "=")
		fileMap[singleLine[0]] = singleLine[1]
	}

	return fileMap
}

func timeSleep(timeVal chan int64, timeout float32) {

	curTime := time.Now().UnixNano()
	savedTime := <-timeVal
	timeDiff := int(curTime - savedTime)
	Timelog("curTime : ", curTime, "\tsavedTime : ", savedTime, "\ttimeDiff : ", timeDiff)

	if timeDiff < 0 {
		Timelog("sleepTime1 : ", time.Duration(int(timeout*1000000000)))
		time.Sleep(time.Duration(int(timeout * 1000000000)))
	} else if timeDiff < int(timeout*1000000000) {
		sleepTime := time.Duration(int(timeout*1000000000) - timeDiff)
		Timelog("sleepTime2 : ", sleepTime)
		time.Sleep(sleepTime)
	}
	saveTime := time.Now().UnixNano()
	Timelog("will save time : ", saveTime/1000000000, saveTime)

	go func() { timeVal <- saveTime }()
}

func getCurTimeString() string {
	curTime := time.Now().Format(time.RFC3339Nano)
	replacer := strings.NewReplacer("-", "", "T", "", ":", "", ".", "")
	return replacer.Replace(curTime)[:len(curTime)-8]
}

func SrcTest() {

	test2 := NewDBHandler()
	//Timelog(test.ProgramRestart(10))
	//Timelog(test.GetHighestTrade(MARKET_KOSPI, true, true))
	//Timelog(test.GetProfitPercent())
	//Timelog(getCurTimeString())

	test3 := NewDantaTrader()
	test3.getRecommended(test2.getNotBuyList(), nil)
}
