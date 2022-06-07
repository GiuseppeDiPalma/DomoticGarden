import boto3
import datetime
import random

url='http://localhost:4566'

sqs = boto3.resource('sqs', endpoint_url=url)

def get_all_queues_name():
    queue = []
    for q in sqs.queues.all():
        name = q.url.split('/')[-1]
        queue.append(name)
    return queue

queueNameList = get_all_queues_name()

for queueName in queueNameList:
    measure_date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
    if queueName == 'error':
        error_msg = '{ "ERROR" ,"measure_date": "' + str(measure_date) + '" }'
    else:
        queue = sqs.get_queue_by_name(QueueName=queueName)

        moisture = random.randint(0, 100) #umidità
        light = random.randint(0, 100)
        temperature = round(random.uniform(-5.0, 30.0), 2) #quantità

        msg_body = '{"plant": "' + queueName + '", "measure_date": "' + str(measure_date) + '", "temperature(°)": "' + str(temperature) + '", "moisture(%)": "' + str(moisture) + '", "light(lx)": "' + str(light) + '"}'
        print(msg_body)
        queue.send_message(MessageBody=msg_body)