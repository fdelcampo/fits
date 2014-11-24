#!/usr/bin/env python
import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='master.wall'))
channel = connection.channel()


channel.queue_declare(queue='hello')

msg = {'msg': 'Hello World!'}

channel.basic_publish(exchange='',
                      routing_key='hello',
                      body=json.dumps(msg))
print " [x] Sent 'Hello World!'"
connection.close()
