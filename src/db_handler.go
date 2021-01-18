package src

import (
	"context"
	redis "github.com/go-redis/redis"
	"strconv"
)

type DBHandler struct {
	//DB 최초 설정시 필요한 값
	ip       string
	port     string
	password string
	user     string
	dbNum    int

	//Redis 접속 시 사용하는 값
	redis    *redis.Client
	redisCtx context.Context

	//기타 프로그램이 지정하는 값
	sellType    map[string]interface{}
	buyType     map[string]interface{}
	notBuyList  string
	todayProfit string
}

func NewDBHandler() *DBHandler {

	dbHandler := DBHandler{}

	//파일에서 설정값 불러들여와 적용
	getFileVal := readFromFile("/setting/" + DB_SETTING_FILE)
	dbHandler.ip = getFileVal["ip"]
	dbHandler.port = getFileVal["port"]
	dbHandler.password = getFileVal["password"]
	dbHandler.user = getFileVal["user"]
	dbHandler.dbNum, _ = strconv.Atoi(getFileVal["db"])

	//Redis에 접속
	dbHandler.redis = dbHandler.connectRedis()
	dbHandler.redisCtx = context.Background()

	//프로그램이 저장하는 값
	dbHandler.sellType = make(map[string]interface{})
	dbHandler.sellType["type"] = "sell"
	dbHandler.sellType["code"] = "code"
	dbHandler.sellType["name"] = "name"
	dbHandler.sellType["amount"] = "amount"
	dbHandler.sellType["price"] = "price"
	dbHandler.sellType["total_price"] = "total_price"
	dbHandler.sellType["profit_percent"] = "profit_percent"
	dbHandler.sellType["profit_price"] = "profit_total_price"

	dbHandler.buyType = make(map[string]interface{})
	dbHandler.buyType["type"] = "buy"
	dbHandler.buyType["code"] = "code"
	dbHandler.buyType["name"] = "name"
	dbHandler.buyType["amount"] = "amount"
	dbHandler.buyType["price"] = "price"
	dbHandler.buyType["total_price"] = "total_price"

	dbHandler.notBuyList = "not_buy_list"
	dbHandler.todayProfit = "today_profit"

	return &dbHandler
}

func (d *DBHandler) connectRedis() *redis.Client {

	client := redis.NewClient(&redis.Options{
		Addr:     d.ip + ":" + d.port, // 접근 url 및 port 설정
		Password: d.password,          // password 설정
		DB:       d.dbNum,             // DB번호 설정
	})

	return client
}

func (d *DBHandler) editCurProfit(profitPrice string) {
	curProfitVal := d.redis.Get(d.redisCtx, d.todayProfit).Val() //비어있으면 "" (키가 없으면), 아니면 value값 return
	if curProfitVal == "" {
		d.redis.Set(d.redisCtx, d.todayProfit, profitPrice, 0)
	}
	curProfitInt, _ := strconv.Atoi(curProfitVal)
	profitPriceInt, _ := strconv.Atoi(profitPrice)
	d.redis.Set(d.redisCtx, d.todayProfit, curProfitInt+profitPriceInt, 0)
}

func (d *DBHandler) getCurProfit() int {
	curProfitVal := d.redis.Get(d.redisCtx, d.todayProfit).Val()
	go d.redis.Set(d.redisCtx, d.todayProfit, 0, 0)
	curProfitValInt, _ := strconv.Atoi(curProfitVal)
	return curProfitValInt
}

func (d *DBHandler) addOrderData(channel chan string) {

	curTime := getCurTimeString()
	go d.redis.RPush(d.redisCtx, d.user, curTime)
	channel <- curTime
}

func (d *DBHandler) addBuyData(code string, name string, amount string, price string, totalPrice string) {

	curTime := make(chan string, 1)
	defer close(curTime)
	go d.addOrderData(curTime)
	d.buyType["code"] = code
	d.buyType["name"] = name
	d.buyType["amount"] = amount
	d.buyType["price"] = price
	d.buyType["total_price"] = totalPrice
	d.redis.HMSet(d.redisCtx, <-curTime, d.buyType)
}

func (d *DBHandler) addSellData(code string, name string, amount string, price string, totalPrice string, profitPercent string, profitTotalPrice string) {

	curTime := make(chan string, 1)
	defer close(curTime)
	go d.addOrderData(curTime)
	go d.editCurProfit(profitTotalPrice)
	d.sellType["code"] = code
	d.sellType["name"] = name
	d.sellType["amount"] = amount
	d.sellType["price"] = price
	d.sellType["total_price"] = totalPrice
	d.sellType["profit_percent"] = profitPercent
	d.sellType["profit_price"] = profitTotalPrice
	d.redis.HMSet(d.redisCtx, <-curTime, d.sellType)
}

func (d *DBHandler) getNotBuyList() []string {

	notBuyMap := d.redis.HGetAll(d.redisCtx, d.notBuyList).Val()
	var notBuyList []string
	for key, val := range notBuyMap {
		if val == "2" {
			notBuyList = append(notBuyList, key)
		}
	}
	return notBuyList
}

func (d *DBHandler) setNotBuyList(codeName string) int {

	counter, _ := strconv.Atoi(d.redis.HGet(d.redisCtx, d.notBuyList, codeName).Val())
	counter++
	d.redis.HSet(d.redisCtx, d.notBuyList, codeName, counter)
	return counter
}

func (d *DBHandler) removeNotBuyList() bool {

	val := d.redis.Del(d.redisCtx, d.notBuyList).Val()
	// 지워졌으면 true, 아니면 false 리턴함
	return val != 0
}

func (d *DBHandler) InputTest() {

	Timelog(d.getNotBuyList())
}
