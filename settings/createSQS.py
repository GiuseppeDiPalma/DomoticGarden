import boto3
import argparse

url = 'http://localhost:4566'

parser = argparse.ArgumentParser()
parser.add_argument('-qn','--queue-name', nargs='+', required=True, help='list of plants')
sqsName = parser.parse_args()


sqs = boto3.resource('sqs', endpoint_url=url)

for plant in sqsName.queue_name:
    queue = sqs.create_queue(QueueName=plant)
    print(queue.url)

# to run: python createSQS.py -qn basil tomato chilli