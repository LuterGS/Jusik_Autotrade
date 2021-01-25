package src

import (
	kiwoom "./KiwoomInteractor"
	"sync"
)

type JusikGetter struct {
	kiwoom *kiwoom.QueueHandler
	db     *kiwoom.DBHandler

	lookupDay int
}

func NewJusikGetter() *JusikGetter {

	jusikGetter := JusikGetter{}

	jusikGetter.kiwoom = kiwoom.NewQueueHandler()
	jusikGetter.db = kiwoom.NewDBHandler()

	return &jusikGetter
}

func (j *JusikGetter) GetRecommendList(lookupDay int) {

	j.lookupDay = lookupDay
	today := kiwoom.GetCurTimeDaySting()
	Timelog("Complete Getting Day : ", today)

	// base - 조건식 종목을 가져온다.은 (코스피, 코스닥 따로)
	kospiJogunJongmoks := j.kiwoom.GetJogunSik(0)
	kosdaqJogunJongmoks := j.kiwoom.GetJogunSik(1)
	Timelog("Complete Getting Jogunsik")
	Timelog("KOSPI jogunsik : ", kospiJogunJongmoks)
	Timelog("KOSDAQ jogunsik : ", kosdaqJogunJongmoks)

	// filter 1. lookupDay 기준으로 각 시장 지수의 등락률보다 높으면서,
	// 	5일평균 >  10일평균 > 20일평균 > 60일평균 > 360일평균인 종목을 가져온다.
	kospiRawData := j.kiwoom.GetJisuDayData(kiwoom.JISU_KOSPI, today, 1)
	kosdaqRawData := j.kiwoom.GetJisuDayData(kiwoom.JISU_KOSDAQ, today, 1)
	kospiValue := float32(kospiRawData[0][1].(int)-kospiRawData[j.lookupDay][1].(int)) / float32(kospiRawData[j.lookupDay][1].(int))
	kosdaqValue := float32(kosdaqRawData[0][1].(int)-kosdaqRawData[j.lookupDay][1].(int)) / float32(kosdaqRawData[j.lookupDay][1].(int))
	Timelog("Complete Getting Jisu Value")

	rawKospiResult := make(chan string)
	rawKosdaqResult := make(chan string)
	var rawResult [2]chan string
	rawResult[0] = rawKospiResult
	rawResult[1] = rawKosdaqResult

	kospiResult := j.getRecommendResult(kospiJogunJongmoks, kospiValue, today)
	kosdaqResult := j.getRecommendResult(kosdaqJogunJongmoks, kosdaqValue, today)

	kiwoom.Timelog("KOSPI 결과 (개수 : ", len(kospiResult), ")")
	for _, data := range kospiResult {
		kiwoom.Timelog(data + "\t" + j.kiwoom.GetKoreanName(data))
	}

	kiwoom.Timelog("KOSDAQ 결과 (개수 : ", len(kosdaqResult), ")")
	for _, data := range kosdaqResult {
		kiwoom.Timelog(data + "\t" + j.kiwoom.GetKoreanName(data))
	}
}

func (j *JusikGetter) getRecommendResult(codeList []string, jisuValue float32, today string) []string {
	chanResult := make(chan string, len(codeList))
	var result []string
	var waiter sync.WaitGroup
	for index, data := range codeList {
		rawCodeData := j.kiwoom.GetJongmokDayData(data, today, 1)
		waiter.Add(1)
		data := data
		index := index
		go func() {
			codeData := make([]int, len(rawCodeData))
			for rIndex, _ := range rawCodeData {
				codeData[rIndex] = rawCodeData[rIndex][1].(int)
			}
			codeValue := (float32(codeData[0]) - float32(codeData[j.lookupDay])) / float32(codeData[j.lookupDay])
			past5 := sumSlice(codeData, 5)
			past10 := sumSlice(codeData, 10)
			past20 := sumSlice(codeData, 20)
			past60 := sumSlice(codeData, 60)
			past360 := sumSlice(codeData, 360)

			if codeValue > jisuValue &&
				past5 > past10 &&
				past10 > past20 &&
				past20 > past60 &&
				past60 >= past360 {
				chanResult <- data
			}
			waiter.Done()
			Timelog("Complete ", data, " all ", index, "/", len(codeList))

		}()
	}
	waiter.Wait()
	Timelog("Reached here")

	isBreak := false
	for {
		select {
		case data := <-chanResult:
			Timelog(data)
			result = append(result, data)

		default:
			isBreak = true
		}

		if isBreak {
			break
		}
	}
	return result
}
