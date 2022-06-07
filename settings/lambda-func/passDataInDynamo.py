import boto3
import datetime
import json

import os
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    url = 'http://localhost:4566'
    
    dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    sqs = boto3.resource('sqs', endpoint_url=url)
    
    plantList = []
    for q in sqs.queues.all():
        name = q.url.split('/')[-1]
        plantList.append(name)

    greenhouseTable = dynamodb.Table('greenhouse')


    for plant in plantList:
        queue = sqs.get_queue_by_name(QueueName=plant)
        messages = []
        while True:
            response = queue.receive_messages(MaxNumberOfMessages=10, VisibilityTimeout=10, WaitTimeSeconds=10)
            if len(response) == 0:
                break
            else:
                messages.extend(response)
                for message in messages:
                    content = json.loads(message.body)
                    measure_date = datetime.datetime.strptime(content['measure_date'], "%d-%m-%Y %H:%M:%S")
                    temperatureVal = content['temperature(°)']
                    moistureVal = content['moisture(%)']
                    lightVal = content['light(lx)']

                    message.delete()
                    item = {
                        'plant': plant,
                        'measure_date': str(measure_date),
                        'temperature(°)': str(temperatureVal),
                        'moisture(%)': str(moistureVal),
                        'light(lx)': str(lightVal)
                    }
                    greenhouseTable.put_item(Item=item)
    