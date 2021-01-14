package src

import (
	"bytes"
	"github.com/streadway/amqp"
	"strconv"
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
}

func InitQueueHandler() *QueueHandler {
	queueHandler := QueueHandler{}

	// 파일에서 설정값을 읽어들여와 저장함
	getFileVal := readFromFile("/setting/" + DB_SETTING_FILE)
	queueHandler.url = getFileVal["MQ_URL"]
	queueHandler.port = getFileVal["MQ_PORT"]
	queueHandler.vhost = getFileVal["MQ_VHOST"]
	queueHandler.cred = getFileVal["MQ_ID"] + ":" + getFileVal["MQ_PW"]
	queueHandler.sendQueue = getFileVal["MQ_OUT_QUEUE"]
	queueHandler.recvQueue = getFileVal["MQ_IN_QUEUE"]

	//sender와 consumer를 잇는 connector 설정
	queueHandler.connectorEmpthChecker = make(chan int)
	for i := 0; i < 10; i++ {
		queueHandler.connector[i] = make(chan []byte)
		i := i
		go func() { queueHandler.connectorEmpthChecker <- i }()
	}
	Timelog("setting connector complete")

	//recvQueue, sendQueue를 받는 connection 및 channel 생성 및 return
	queueHandler.recvQueueConnection, queueHandler.recvQueueChannel = queueHandler.getConnection()
	queueHandler.sendQueueConnection, queueHandler.sendQueueChannel = queueHandler.getConnection()
	go queueHandler.consumeQueue(queueHandler.recvQueueChannel, queueHandler.recvQueue)
	//time.Sleep(time.Second * 3)

	return &queueHandler
}

func (q *QueueHandler) getConnection() (*amqp.Connection, *amqp.Channel) {
	//Timelog("amqp://" + q.cred + "@" + q.url + ":" + q.port + "/" + q.vhost)
	connection, err := amqp.Dial("amqp://" + q.cred + "@" + q.url + ":" + q.port + "/" + q.vhost)
	if err != nil {
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

	Timelog(queueName)

	val1, _ := channel.Consume(queueName, "", true, true, true, false, nil)
	amqpHandler := AMQPHandler{queDelivery: val1}

	for {
		receiveVal := bytes.Split(amqpHandler.GetFromQueue(), []byte("|"))
		Timelog(receiveVal)
		roomNum, err := strconv.Atoi(string(receiveVal[0]))
		if err != nil {
			Timelog("숫자 변환에 오류가 발생했습니다. 프로그램을 종료합니다.")
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

func (q *QueueHandler) publishQueue(channel *amqp.Channel, queueName string, value string) string {

	roomNum := <-q.connectorEmpthChecker
	value = strconv.Itoa(roomNum) + "|" + value

	err := channel.Publish(
		"",
		queueName,
		false,
		false,
		amqp.Publishing{
			ContentType: "text/plain",
			Body:        []byte(value),
		},
	)
	if err != nil {
		Timelog("Queue : " + queueName + "  를 Publishing하는 과정에서 Error 발생")
		panic("Queue publishing 과정 중 문제 발생")
	}
	Timelog("send to " + queueName + ", send " + value + " complete")

	receiveVal := string(<-q.connector[roomNum])
	Timelog("PublishQueue - " + strconv.Itoa(roomNum) + "번 방에서 데이터 읽음 : " + receiveVal)
	go addValueToChannel(q.connectorEmpthChecker, roomNum)
	return receiveVal
}

func (q *QueueHandler) PublishTest() {
	for i := 0; i < 30; i++ {
		q.publishQueue(q.recvQueueChannel, q.recvQueue, "test"+strconv.Itoa(i))
	}
}

func (q *QueueHandler) GetBalance() int {
	queueOutput := q.publishQueue(q.sendQueueChannel, q.sendQueue, "잔액요청")
	returnVal, err := strconv.Atoi(queueOutput)
	if err != nil {
		Timelog("잔액요청이 완료되었지만, 잔액 값이 이상해 숫자 변환에 실패했습니다. 값 : ", returnVal)
		panic("숫자 변환 오류")
	}
	return returnVal
}

func (q *QueueHandler) GetHighestTrade() string {
	queueOuptut := q.publishQueue(q.sendQueueChannel, q.sendQueue, "거래량급증요청,15,101,1,1")
	return queueOuptut
}

func (q *QueueHandler) GetProfitPercent() string {
	queueOutput := q.publishQueue(q.sendQueueChannel, q.sendQueue, "수익률요청")
	return queueOutput
}
