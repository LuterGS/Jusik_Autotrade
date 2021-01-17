package src

import "time"

func mainer() {

	for {
		curTime, curTimer := setCurTimer()
		if curTime == 0 { // 현재 시간이 점검전, 장마감 이후일 때
			Timelog("현재 점검전, 장마감 이후입니다.")

			<-curTimer.C //Timer 울릴 때까지 대기
			curTimer.Stop()
		} else if curTime == 1 { // 현재 시간이 점검 시간일 때
			Timelog("현재 점검중입니다. 프로그램도 잠시 쉽니다.")

			<-curTimer.C
			curTimer.Stop()
		} else if curTime == 2 { // 현재 시간이 점검 직후, 단타 이전 시간일 때
			Timelog("현재 점검 직후, 단타 이전입니다.")

			<-curTimer.C
			curTimer.Stop()
		} else if curTime == 3 { // 현재 시간이 단타알고리즘 시간일 때
			Timelog("현재 단타알고리즘 시간입니다.")

			<-curTimer.C
			curTimer.Stop()
		} else if curTime == 4 { // 현재 시간이 AI 트레이더 시간일 때
			Timelog("현재 AI 트레이더 시간입니다.")

			<-curTimer.C
			curTimer.Stop()
		}
	}
}

func setCurTimer() (int, *time.Timer) {

	curTime := time.Now()
	sigHour := [5]int{SIG_A_HOUR, SIG_B_HOUR, SIG_C_HOUR, SIG_D_HOUR, SIG_E_HOUR}
	sigMin := [5]int{SIG_A_MIN, SIG_B_MIN, SIG_C_MIN, SIG_D_MIN, SIG_E_MIN}

	for i := 0; i < len(sigHour); i++ {
		if (curTime.Hour() < sigHour[i]) || (curTime.Hour() == sigHour[i] && curTime.Minute() <= sigMin[i]) {
			estimateTime := time.Date(curTime.Year(), curTime.Month(), curTime.Day(), sigHour[i], sigMin[i], 0, 0, curTime.Location())
			timeDiff := estimateTime.Sub(curTime)
			timer := time.NewTimer(timeDiff)
			return i, timer
		}
	}
	//만약 지금이 장마감 이후 시간일 때
	estimateTime := time.Date(curTime.Year(), curTime.Month(), curTime.Day()+1, sigHour[0], sigMin[0], 0, 0, curTime.Location())
	timeDiff := estimateTime.Sub(curTime)
	timer := time.NewTimer(timeDiff)
	return 0, timer
}
