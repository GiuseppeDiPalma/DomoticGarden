import string, random, datetime, json
import boto3

def split_queue_name(queueName):
    plantID = queueName.split('_')[0]
    return plantID

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def lambda_handler(event, context):
    url = 'http://localhost:4566'
    
    dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    sqs = boto3.resource('sqs', endpoint_url=url)
    
    plantList = []
    for q in sqs.queues.all():
        name = q.url.split('/')[-1]
        plantList.append(name)
    
    if len(plantList) == 0:
        print('No queue found!')
        print('Create queues with the /start command on the telegram bot.')

    greenhouseTable = dynamodb.Table('greenhouse')


    for plant in plantList:
        plant_name = split_queue_name(plant)
        queue = sqs.get_queue_by_name(QueueName=plant)
        messages = []
        while True:
            # response = queue.receive_messages(MaxNumberOfMessages=10, VisibilityTimeout=10, WaitTimeSeconds=10)
            response = queue.receive_messages()
            if len(response) == 0:
                print(f'NO MESSAGE FOUND ON: [{plant}]')
                break
            else:
                messages.extend(response)
                for message in messages:
                    content = json.loads(message.body)
                    print(content)
                    measure_date = datetime.datetime.strptime(content['measure_date'], "%d-%m-%Y %H:%M:%S")

                    message.delete()
                    item = {
                        'id':id_generator(5),
                        'userID': content['userID'],
                        'plant': plant_name,
                        'measure_date': str(measure_date),
                        'temperature(°)': content['temperature(°)'],
                        'moisture(%)': content['moisture(%)'],
                        'light(lx)': content['light(lx)']
                    }
                    greenhouseTable.put_item(Item=item)

lambda_handler(None, None)