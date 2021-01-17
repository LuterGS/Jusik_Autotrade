package src

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
	connector             [10]chan []byte
	connectorEmpthChecker chan int

	//요청당 Timeout 설정
	timeout chan int64
}

func NewQueueHandler() *QueueHandler {
	queueHandler := QueueHandler{}

	// 파일에서 설정값을 읽어들여와 저장함
	getFileVal := readFromFile("/setting/" + MQ_SETTING_FILE)
	Timelog(getFileVal)
	queueHandler.url = getFileVal["MQ_URL"]
	queueHandler.port = getFileVal["MQ_PORT"]
	queueHandler.vhost = getFileVal["MQ_VHOST"]
	queueHandler.cred = getFileVal["MQ_ID"] + ":" + getFileVal["MQ_PW"]
	queueHandler.sendQueue = getFileVal["MQ_OUT_QUEUE"]
	queueHandler.recvQueue = getFileVal["MQ_IN_QUEUE"]

	Timelog(queueHandler.cred)

	//sender와 consumer를 잇는 connector 설정
	queueHandler.connectorEmpthChecker = make(chan int)
	for i := 0; i < 10; i++ {
		queueHandler.connector[i] = make(chan []byte, 1)
		i := i
		go func() { queueHandler.connectorEmpthChecker <- i }()
	}
	Timelog("setting connector complete")

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
		//Timelog(receiveVal)
		roomNum, err := strconv.Atoi(string(receiveVal[0]))
		if err != nil {
			Timelog("channel 숫자 변환에 오류가 발생했습니다. 프로그램을 종료합니다.")
			panic("숫자 변환 오류")
		}
		q.connector[roomNum] <- bytes.Trim(receiveVal[1], "\x00")
	}

	//go func(test <- chan amqp.Delivery){
	//	for d := range test{
	//		timelog(d.Body)
	//	}
	//}(val1)
}

func (q *QueueHandler) publishQueue(channel *amqp.Channel, queueName string, value string, timeout float32) [][]string {

	//timeout에 따라 정해진 시간만큼 timeout 해줌
	for {
		roomNum := <-q.connectorEmpthChecker
		passValue := strconv.Itoa(roomNum) + "|" + value

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
		Timelog("send to " + queueName + ", send " + passValue + " complete")

		// 데이터를 받아온 뒤에야 빈 방이 있다고 다시 알려줌
		receiveVal := queueOutputToData(value, string(<-q.connector[roomNum]))
		go func() { q.connectorEmpthChecker <- roomNum }()
		Timelog("receiveVal ", receiveVal)

		// 이후 데이터가 잘못되면 재시도, 아니면 정상 값을 return
		if receiveVal != nil {
			return receiveVal
		}
		Timelog("Failed To Receive Data")
	}

}

func (q *QueueHandler) PublishTest() {
	for i := 0; i < 30; i++ {
		q.publishQueue(q.recvQueueChannel, q.recvQueue, "test"+strconv.Itoa(i), 3.6)
	}
}

func (q *QueueHandler) GetBalance() int {
	queueOutput := q.publishQueue(q.sendQueueChannel, q.sendQueue, "잔액요청", 3.6)
	returnVal, err := strconv.Atoi(queueOutput[0][0])
	if err != nil {
		Timelog("잔액요청이 완료되었지만, 잔액 값이 이상해 숫자 변환에 실패했습니다. 값 : ", returnVal)
		panic("숫자 변환 오류")
	}
	return returnVal
}

func (q *QueueHandler) GetHighestTrade(market string, isPercent bool, isMin bool) [][]string {
	queueOuptut := q.publishQueue(q.sendQueueChannel, q.sendQueue, parseHighestRaiseInput(market, isPercent, isMin), 3.6)
	return queueOuptut
}

func (q *QueueHandler) GetProfitPercent() [][]string {
	queueOutput := q.publishQueue(q.sendQueueChannel, q.sendQueue, "수익률요청", 3.6)
	return queueOutput
}

func (q *QueueHandler) ProgramRestart(waitTime int) bool {
	queueOutput := q.publishQueue(q.sendQueueChannel, q.sendQueue, "프로그램재시작,"+strconv.Itoa(waitTime), 0.0)
	time.Sleep(time.Second * time.Duration(waitTime+10)) // 프로그램 재시작 후에 얼마나 더 기다릴것인지, 현재는 10초로 설정이지만 더 늘려야 함
	if queueOutput[0][0] == "RESTART" {
		return true
	} else {
		return false
	}
}
