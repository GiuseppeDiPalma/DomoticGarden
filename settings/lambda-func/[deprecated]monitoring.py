import json
import boto3

def lamba_handler(event, context):
    url = 'http://localhost:4566'

    dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    sqs = boto3.resource('sqs', endpoint_url=url)

    greenhouseTable = dynamodb.Table('greenhouse')
    response = greenhouseTable.scan()
    items = response['Items']

    for i in items:
        plant = i['plant']
        light = i['light(lx)']
        temperature = float(i['temperature(°)'])
        moisture = int(i['moisture(%)'])
        measure_date = i['measure_date']
        print(f"Plant: {plant} Light: {light} Temperature: {temperature} Moisture: {moisture} Measure_date: {measure_date}")

        queue = sqs.get_queue_by_name(QueueName=plant)
        messages = []
        while True:
            response = queue.receive_messages(MaxNumberOfMessages=10, VisibilityTimeout=10, WaitTimeSeconds=10)
            if response:
                messages.extend(response)
                for message in messages:
                    content = json.loads(message.body)
            else:
                print("No more messages!!")
                break