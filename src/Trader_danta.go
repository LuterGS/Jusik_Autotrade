package src

import "strconv"

type DantaTrader struct {
	kiwoom *QueueHandler
	db     *DBHandler
	//file	*FileHandler

}

func NewDantaTrader() *DantaTrader {

	dantaTrader := DantaTrader{}

	dantaTrader.kiwoom = NewQueueHandler()
	dantaTrader.db = NewDBHandler()
	//dantaTrader.file = NewFileHandler()

	return &dantaTrader
}

func (d *DantaTrader) getRecommended(notBuyList []string, rawCurJusikProfitList [][]string) [][]string {

	buyPrice := int(ONE_JONGMOK_PRICE * 0.97)

	curJusikProfitList := rawCurJusikProfitList
	if rawCurJusikProfitList == nil {
		curJusikProfitList = d.kiwoom.GetProfitPercent()
	}
	curJusikList := make([]string, len(curJusikProfitList))
	for index, data := range curJusikProfitList {
		curJusikList[index] = data[1]
	}

	buyListNum := TOTAL_JONGMOK_NUM - len(curJusikList)
	Timelog("buyListNum : ", buyListNum)
	if buyListNum == 0 {
		return nil
	}

	buyList := make([][]string, buyListNum)
	rawBuyList := d.kiwoom.GetHighestTrade(CUR_TRADE_MARKET, true, true)
	counter := 0
	for _, buyData := range rawBuyList {
		jusikPrice, _ := strconv.Atoi(buyData[2])
		amount := int(buyPrice / jusikPrice)
		if d.isContained(buyData[1], notBuyList) == false && d.isContained(buyData[1], curJusikList) == false && amount > 0 {
			buyList[counter] = []string{buyData[0], buyData[1], strconv.Itoa(amount), buyData[2]}
			// 각각 종목코드, 종목이롬, 구매개수, 구매가격을 뜻한다.
			counter++
		}

		if counter == buyListNum {
			break
		}
	}
	Timelog(buyList)
	return buyList
}

func (d *DantaTrader) isContained(checkData string, checkList []string) bool {
	//Timelog(checkData, checkList)
	isContained := false
	for d := range checkList {
		if checkList[d] == checkData {
			isContained = true
		}
	}
	return isContained
}

func (d *DantaTrader) trade() {

	notBuyList := d.db.getNotBuyList()
	Timelog(notBuyList)
	for {
		curProfitJusiks := d.kiwoom.GetProfitPercent()

		if len(curProfitJusiks) < TOTAL_JONGMOK_NUM {
			//
		}

	}

}
