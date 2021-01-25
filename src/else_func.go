package src

import (
	kiwoom "./KiwoomInteractor"
)

func sumSlice(inputSlice []int, num int) float32 {

	if num > len(inputSlice) {
		num = len(inputSlice)
	}

	sum := 0
	for i := 0; i < num; i++ {
		sum += inputSlice[i]
	}
	return float32(sum) / float32(num)
}

func Timelog(a ...interface{}) {
	kiwoom.Timelog(a...)
}
