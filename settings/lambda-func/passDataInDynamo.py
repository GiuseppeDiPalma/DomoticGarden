import string, random, datetime, json, io, csv
import boto3

#split the queue name into userID and plantID
def split_queue_name(queueName):
    userID = queueName.split('_')[0]
    plantID = queueName.split('_')[1]
    return userID, plantID

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
        plant_name, plant_id = split_queue_name(plant)
        print(f"Plant: {plant_name} | ID: {plant_id}")
        plant_id = plant_name + '_' + str(plant_id)
        queue = sqs.get_queue_by_name(QueueName=plant)
        messages = []
        while True:
            response = queue.receive_messages()
            if len(response) == 0:
                print(f'NO MESSAGE FOUND ON QUEUE: [{plant}]')
                break
            else:
                messages.extend(response)
                for message in messages:
                    content = json.loads(message.body)
                    print(content)
                    measure_date = datetime.datetime.strptime(content['measure_date'], "%d-%m-%Y %H:%M:%S")

                    item = {
                        'plant_id':plant_id,
                        'userID': content['userID'],
                        'measure_date': str(measure_date),
                        'temperature(°)': content['temperature(°)'],
                        'moisture(%)': content['moisture(%)'],
                        'light(lx)': content['light(lx)']
                    }
                    greenhouseTable.put_item(Item=item)
                    message.delete()