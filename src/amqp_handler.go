package src

import (
	"github.com/streadway/amqp"
)

type AMQPHandler struct {
	queDelivery <-chan amqp.Delivery
}

func (a *AMQPHandler) GetFromQueue() []byte {
	for d := range a.queDelivery {
		return d.Body
	}
	return []byte("error")
}
