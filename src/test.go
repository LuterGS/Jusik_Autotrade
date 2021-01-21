package src

import (
	kiwoom "./KiwoomInteractor"
	"os"
)

//db := NewDBHandler()
//db.editCurProfit("1234")
func Test() {

	test := kiwoom.NewQueueHandler()
	kiwoom.Timelog(test.GetBalance())
	kiwoom.Timelog(test.GetProfitPercent())
	kiwoom.Timelog(test.GetJogunSik(0))
	kiwoom.Timelog(test.GetHighestTrade(kiwoom.MARKET_KOSPI, true, true))
	kiwoom.Timelog(test.GetJisuDayData(kiwoom.JISU_KOSPI, "20210121", 2))
	kiwoom.Timelog(test.GetJongmokDayData("001000", "20210121", 2))
	kiwoom.Timelog(test.GetJongmokMinData("001000", 2))

	os.Exit(1)
}
