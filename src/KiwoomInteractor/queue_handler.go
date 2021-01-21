package KiwoomInteractor

import (
	"bytes"
	"github.com/streadway/amqp"
	"strconv"
	"time"
)

type QueueHandler struct {
	url       string
	port      string
	vhost     string
	cred      string
	sendQueue string
	recvQueue string

	//recvQueue connection과 channel
	recvQueueConnection *amqp.Connection
	recvQueueChannel    *amqp.Channel

	//sendQueue connection과 channel
	sendQueueConnection *amqp.Connection
	sendQueueChannel    *amqp.Channel

	//sender와 consumer를 이어주는 channel들과, 해당 channel의 빈 방을 알려주는 channel 생성
	connector             [10]chan string
	connectorEmpthChecker chan int
	differ                int

	//요청당 Timeout 설정
	timeout chan int64
}

func NewQueueHandler() *QueueHandler {
	queueHandler := QueueHandler{}

	// 파일에서 설정값을 읽어들여와 저장함
	getFileVal := readFromFile("/setting/" + MQ_SETTING_FILE)
	queueHandler.url = getFileVal["MQ_URL"]
	queueHandler.port = getFileVal["MQ_PORT"]
	queueHandler.vhost = getFileVal["MQ_VHOST"]
	queueHandler.cred = getFileVal["MQ_ID"] + ":" + getFileVal["MQ_PW"]
	queueHandler.sendQueue = getFileVal["MQ_OUT_QUEUE"]
	queueHandler.recvQueue = getFileVal["MQ_IN_QUEUE"]

	//sender와 consumer를 잇는 connector 설정
	queueHandler.connectorEmpthChecker = make(chan int, 10)
	for i := 0; i < 10; i++ {
		queueHandler.connector[i] = make(chan string, 1)
		i := i
		go func() { queueHandler.connectorEmpthChecker <- i }()
	}
	rawVal := strconv.Itoa(int(time.Now().Unix()))[5:]
	val, _ := strconv.Atoi(rawVal)
	queueHandler.differ = val * 10
	Timelog("setting connector complete, differ : ", queueHandler.differ)

	//recvQueue, sendQueue를 받는 connection 및 channel 생성 및 return
	queueHandler.recvQueueConnection, queueHandler.recvQueueChannel = queueHandler.getConnection()
	queueHandler.sendQueueConnection, queueHandler.sendQueueChannel = queueHandler.getConnection()
	go queueHandler.consumeQueue(queueHandler.recvQueueChannel, queueHandler.recvQueue)
	//time.Sleep(time.Second * 3)

	//timeout 시간 설정
	queueHandler.timeout = make(chan int64, 1)
	go func() { queueHandler.timeout <- time.Now().UnixNano() }()

	return &queueHandler
}

func (q *QueueHandler) getConnection() (*amqp.Connection, *amqp.Channel) {
	//Timelog("amqp://" + q.cred + "@" + q.url + ":" + q.port + "/" + q.vhost)
	connection, err := amqp.Dial("amqp://" + q.cred + "@" + q.url + ":" + q.port + "/" + q.vhost)
	if err != nil {
		Timelog("amqp://" + q.cred + "@" + q.url + ":" + q.port + "/" + q.vhost)
		Timelog("connection을 맺는 데 오류가 발생했습니다.\t", err)
		panic("connection 연결 오류")
	}

	channel, err := connection.Channel()
	if err != nil {
		Timelog("connection에서 channel을 얻어오는 데 오류가 발생했습니다. 프로그램을 종료합니다.")
		panic("channel 얻기 오류")
	}

	return connection, channel
}

func (q *QueueHandler) consumeQueue(channel *amqp.Channel, queueName string) {

	//Timelog(queueName)
	val1, _ := channel.Consume(queueName, "", true, true, true, false, nil)
	amqpHandler := AMQPHandler{queDelivery: val1}

	for {
		receiveVal := bytes.Split(amqpHandler.GetFromQueue(), []byte("|"))
		roomNum, err := strconv.Atoi(string(receiveVal[0]))
		rawRoomNum := roomNum
		roomNum = roomNum - q.differ
		if err != nil {
			Timelog(rawRoomNum, roomNum, q.differ, " 안되는 이유 파악하기")
			Timelog("channel 숫자 변환에 오류가 발생했습니다. 프로그램을 종료합니다.")
			panic("숫자 변환 오류")
		}

		if -1 < roomNum && roomNum < 10 {
			q.connector[roomNum] <- string(receiveVal[1])
		} else {
			Timelog("현재 프로그램에서 Publish한 값이 아니므로 무시됩니다.\trawRoomNum:", rawRoomNum, "\tq.differ:", q.differ, "\troomNum:", roomNum)
		}
	}
}

func (q *QueueHandler) publishQueue(channel *amqp.Channel, queueName string, value string, timeout float32) [][]interface{} {

	Timelog(value)
	//timeout에 따라 정해진 시간만큼 timeout 해줌
	for {
		roomNum := <-q.connectorEmpthChecker
		passValue := strconv.Itoa(roomNum+q.differ) + "|" + value

		timeSleep(q.timeout, timeout)

		err := channel.Publish(
			"",
			queueName,
			false,
			false,
			amqp.Publishing{
				ContentType: "text/plain",
				Body:        []byte(passValue),
			},
		)
		if err != nil {
			Timelog("Queue : " + queueName + "  를 Publishing하는 과정에서 Error 발생")
			panic("Queue publishing 과정 중 문제 발생")
		}
		//Timelog("send to " + queueName + ", send " + passValue + " complete")

		//Timer와 callback을 이용해서 20초 이상 요청이 안 올 시 ""값을 넘기도록 함
		queueData := ""
		isBreak := false
		timer := time.NewTimer(time.Second * 20)
		for {
			select {
			case data := <-q.connector[roomNum]:
				queueData = data
				isBreak = true
			case <-timer.C:
				isBreak = true
			default:
			}
			if isBreak {
				timer.Stop()
				break
			}
		}

		// 데이터를 받아온 뒤에야 빈 방이 있다고 다시 알려줌
		receiveVal := queueOutputToData(value, queueData)
		q.connectorEmpthChecker <- roomNum

		// 이후 데이터가 잘못되면 재시도, 아니면 정상 값을 return
		if receiveVal[0][0] != "ERROR" {
			return receiveVal
		}
		Timelog("Failed To Receive Data")
	}

}

func (q *QueueHandler) basicGetDayData(reqNum string, code string, dayString string, reqIter int) [][]interface{} {
	if reqIter == 1 {
		queueOutput := q.publishQueue(q.sendQueueChannel, q.sendQueue, parseDayData(reqNum, code, dayString, false), 3.6)
		return queueOutput
	} else {
		queueOutput := q.publishQueue(q.sendQueueChannel, q.sendQueue, parseDayData(reqNum, code, dayString, false), 3.6)
		for i := 1; i < reqIter; i++ {
			queueOutput = append(queueOutput, q.publishQueue(q.sendQueueChannel, q.sendQueue, parseDayData(reqNum, code, dayString, true), 3.6)...)
		}
		return queueOutput
	}
}

func (q *QueueHandler) GetBalance() int {
	queueOutput := q.publishQueue(q.sendQueueChannel, q.sendQueue, qrBalance, 3.6)
	returnVal, err := strconv.Atoi(queueOutput[0][0].(string))
	if err != nil {
		Timelog("잔액요청이 완료되었지만, 잔액 값이 이상해 숫자 변환에 실패했습니다. 값 : ", returnVal)
		panic("숫자 변환 오류")
	}
	return returnVal
}

// [n][0]은 string, 이하 [n][i] (i != 0) 은 int
func (q *QueueHandler) GetJongmokMinData(code string, reqIter int) [][]interface{} {
	if reqIter == 1 {
		queueOutput := q.publishQueue(q.sendQueueChannel, q.sendQueue, parseMinData(code, false), 3.6)
		return queueOutput
	} else {
		queueOutput := q.publishQueue(q.sendQueueChannel, q.sendQueue, parseMinData(code, false), 3.6)
		for i := 1; i < reqIter; i++ {
			queueOutput = append(queueOutput, q.publishQueue(q.sendQueueChannel, q.sendQueue, parseMinData(code, true), 3.6)...)
		}
		return queueOutput
	}
}

// [n][0]은 string, 이하 [n][i] (i != 0) 은 int
func (q *QueueHandler) GetJongmokDayData(code string, dayString string, reqIter int) [][]interface{} {
	return q.basicGetDayData(qrGetPastDayData, code, dayString, reqIter)
}

// [n][0]은 string, 이하 [n][i] (i != 0) 은 int
func (q *QueueHandler) GetJisuDayData(jisu Jisu, dayString string, reqIter int) [][]interface{} {
	return q.basicGetDayData(qrGetJisuDayData, string(jisu), dayString, reqIter)
}

func (q *QueueHandler) GetHighestTrade(market string, isPercent bool, isMin bool) [][]interface{} {
	queueOuptut := q.publishQueue(q.sendQueueChannel, q.sendQueue, parseHighestRaiseInput(market, isPercent, isMin), 3.6)
	return queueOuptut
}

func (q *QueueHandler) GetProfitPercent() [][]interface{} {
	queueOutput := q.publishQueue(q.sendQueueChannel, q.sendQueue, qrGetProfit, 3.6)
	return queueOutput
}

func (q *QueueHandler) ProgramRestart(waitTime int) int {
	queueOutput := q.publishQueue(q.sendQueueChannel, q.sendQueue, qrProgramRestart+","+strconv.Itoa(waitTime), 0.0)
	time.Sleep(time.Second * time.Duration(waitTime+30)) // 프로그램 재시작 후에 얼마나 더 기다릴것인지, 현재는 10초로 설정이지만 더 늘려야 함
	sleepTime, err := strconv.Atoi(queueOutput[0][0].(string))
	if err != nil {
		Timelog("프로그램 재시작 시간을 Parsing 하던 중 오류가 발생했습니다.")
		panic("Parsing 오류")
	}
	return sleepTime
}

func (q *QueueHandler) BuyJusik(code string, amount string, price string) int {
	queueOutput := q.publishQueue(q.sendQueueChannel, q.sendQueue, parseTradeJusikInput(qrBuyJusik, code, amount, price, qrSijangGaTrade), 0.2)
	returnVal, err := strconv.Atoi(queueOutput[0][0].(string))
	if err != nil {
		Timelog("주식 구매가 완료되었지만, 결과값을 Parsing중 오류가 발생했습니다. 값 : ", returnVal)
	}
	return returnVal
}

func (q *QueueHandler) SellJusik(code string, amount string, price string) int {
	queueOutput := q.publishQueue(q.sendQueueChannel, q.sendQueue, parseTradeJusikInput(qrSellJusik, code, amount, price, qrSijangGaTrade), 0.2)
	returnVal, err := strconv.Atoi(queueOutput[0][0].(string))
	if err != nil {
		Timelog("주식 판매가 완료되었지만, 결과값을 Parsing중 오류가 발생했습니다. 값 : ", returnVal)
	}
	return returnVal
}

func (q *QueueHandler) GetJogunSik(jogunsikNum int) [][]interface{} {
	queueOutput := q.publishQueue(q.sendQueueChannel, q.sendQueue, parseJogunSik(jogunsikNum), 3.6)
	return queueOutput
}

func (q *QueueHandler) Test() {

	for i := 0; i < 10; i++ {
		Timelog(<-q.connectorEmpthChecker)
	}

}
