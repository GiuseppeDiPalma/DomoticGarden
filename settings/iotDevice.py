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

def split_queue_name(queueName):
    userID = queueName.split('_')[0]
    plantID = queueName.split('_')[1]
    return userID, plantID

if len(queueNameList) == 0:
    print('No queue found!')
    print('Create queues with the /start command on the telegram bot.')
else :
    for queueName in queueNameList:
        plant, userID= split_queue_name(queueName)
        measure_date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        queue = sqs.get_queue_by_name(QueueName=queueName)
        moisture = random.randint(0, 100)
        light = random.randint(0, 100)
        temperature = round(random.uniform(-5.0, 30.0), 2)

        msg_body = '{"plant_id": "' + queueName + '", "userID": "' + userID + '", "measure_date": "' + str(measure_date) + '", "temperature(°)": "' + str(temperature) + '", "moisture(%)": "' + str(moisture) + '", "light(lx)": "' + str(light) + '"}'
        print(f"Message send: {msg_body}")
        queue.send_message(MessageBody=msg_body)