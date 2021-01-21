package KiwoomInteractor

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
	//Timelog(lines)
	for i := 0; i < len(lines)-1; i++ {
		singleLine := strings.Split(lines[i], "=")
		fileMap[singleLine[0]] = singleLine[1]
	}

	return fileMap
}

func timeSleep(timeVal chan int64, timeoutSec float32) {

	timeoutMiliSec := timeoutSec * 1000
	curTime := time.Now().UnixNano()
	savedTime := <-timeVal
	timeDiff := int(curTime - savedTime)
	//Timelog("curTime : ", curTime, "\tsavedTime : ", savedTime, "\ttimeDiff : ", timeDiff)

	if timeDiff < 0 {
		//Timelog("sleepTime1 : ", time.Duration(int(timeout*1000000000)))
		// TODO : 라즈베리 파이에서 시간이 다르게 Sleep되는 관계로, 확인이 필요함
		time.Sleep(time.Millisecond * time.Duration(timeoutMiliSec))
	} else if time.Duration(timeDiff) < time.Duration(timeoutMiliSec)*time.Millisecond {
		time.Sleep(time.Millisecond*time.Duration(timeoutMiliSec) - time.Duration(timeDiff))

		//sleepTime := time.Duration(int(timeout*1000000000) - timeDiff)
		//Timelog("sleepTime2 : ", sleepTime)
		//time.Sleep(sleepTime)
	}
	saveTime := time.Now().UnixNano()

	go func() { timeVal <- saveTime }()
}

func getCurTimeString() string {
	curTime := time.Now().Format(time.RFC3339Nano)
	replacer := strings.NewReplacer("-", "", "T", "", ":", "", ".", "")
	return replacer.Replace(curTime)[:len(curTime)-8]
}

func RawCodeToCode(code string) string {

	if code[0] == 'A' {
		return code[1:]
	} else {
		return code
	}
}

func IArraytoSArray(iArray []interface{}) []string {

	result := make([]string, len(iArray))
	for index, data := range iArray {
		result[index] = data.(string)
	}
	return result
}

func slice2dPrinter(value [][]string) {
	for d := range value {
		Timelog(value[d])
	}
}
