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
	dbData, err := ioutil.ReadFile(curLoc + "/setting/" + DB_SETTING_FILE)
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

func addValueToChannel(channel chan int, value int) {
	channel <- value
}
