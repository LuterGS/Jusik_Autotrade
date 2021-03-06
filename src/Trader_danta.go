package src

import (
	"strconv"
	"time"
)

type DantaTrader struct {
	kiwoom *QueueHandler
	db     *DBHandler
	//file	*FileHandler

	checkEnd *time.Timer //trade는 이 timer가 울릴 때까지 동작한다.

	profitPrice int
}

func NewDantaTrader(checkEnd *time.Timer) *DantaTrader {

	dantaTrader := DantaTrader{}

	dantaTrader.kiwoom = NewQueueHandler()
	dantaTrader.db = NewDBHandler()
	//dantaTrader.file = NewFileHandler()

	dantaTrader.checkEnd = checkEnd

	dantaTrader.profitPrice = 0

	return &dantaTrader
}

func (d *DantaTrader) SellJusik(jusikData []string) {

	go d.db.addSellData(jusikData[0], jusikData[1], jusikData[2], jusikData[7], jusikData[4], jusikData[6], jusikData[5])
	d.kiwoom.SellJusik(jusikData[0], jusikData[2], jusikData[7])
	//개인적으로 찍는 log도 포함되어야함
	Timelog(jusikData)
}

func (d *DantaTrader) BuyJusik(jusikData []string) {
	amount, _ := strconv.Atoi(jusikData[2])
	price, _ := strconv.Atoi(jusikData[3])

	go d.db.addBuyData(jusikData[0], jusikData[1], jusikData[2], jusikData[3], strconv.Itoa(amount*price))
	d.kiwoom.BuyJusik(jusikData[0], jusikData[2], jusikData[3])

	Timelog(jusikData)
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

	// 로그 찍기
	Timelog(notBuyList, curJusikList)

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

func (d *DantaTrader) isEnd() bool {

	select {
	case <-d.checkEnd.C: //종료 시점일 때
		Timelog("단타가 끝났습니다.")
		go d.db.removeNotBuyList()

		if END_DANTA_SELL_ALL {
			Timelog("설정에 따라 모든 주식을 매매합니다.")
			curJusiks := d.kiwoom.GetProfitPercent()
			for _, data := range curJusiks {
				d.SellJusik(data)
			}
		} else {
			Timelog("설정에 따라 주식을 매매하지 않고 종료합니다.")
		}

		Timelog("오늘의 재구매 없는 주식 : ", d.db.getNotBuyList())
		Timelog("오늘의 이득금액 : ", d.db.getCurProfit())
		Timelog("현재 보유금액 : ", d.kiwoom.GetBalance())
		return true
	default:
		return false
	}
}

func (d *DantaTrader) trade() {

	for {
		curProfitJusiks := d.kiwoom.GetProfitPercent()
		notBuyList := d.db.getNotBuyList()

		//매도로 인해 현재 종목수가 부족할 때
		if len(curProfitJusiks) < TOTAL_JONGMOK_NUM {
			buyList := d.getRecommended(notBuyList, curProfitJusiks)
			for _, data := range buyList {
				d.BuyJusik(data)
			}
			curProfitJusiks = d.kiwoom.GetProfitPercent()
		}

		//거래 비교 시작
		for _, data := range curProfitJusiks {
			profitPercent, _ := strconv.ParseFloat(data[6], 32)
			if profitPercent > MAX_PROFIT_PERCENT {
				d.SellJusik(data)
			} else if profitPercent < -1.0*MAX_LOSS_PERCENT {
				go d.db.setNotBuyList(data[1])
				d.SellJusik(data)
			}
		}

		//종료 확인
		if d.isEnd() {
			break
		}
	}
}
