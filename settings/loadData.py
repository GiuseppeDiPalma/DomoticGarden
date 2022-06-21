import boto3
import datetime
import random
import string

url = 'http://localhost:4566'

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))



plants = ['basil', 'chilli', 'tomato']

def loadData(userID):
    dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    greenhouseTable = dynamodb.Table('greenhouse')
    for i in range(len(plants)):
        measure_date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        moisture = random.randint(0, 100) #umidità
        light = random.randint(0, 100)
        temperature = round(random.uniform(-5.0, 30.0), 2) #quantità
        item ={
            'id': id_generator(5),
            'userID': str(userID),
            'plant': plants[i],
            'measure_date': str(measure_date),
            'temperature(°)': str(temperature),
            'moisture(%)': str(moisture),
            'light(lx)': str(light)
        }
        greenhouseTable.put_item(Item=item)
        print("Add item: ", item)

loadData(211545788)