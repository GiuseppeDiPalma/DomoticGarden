from dotenv import load_dotenv
from boto3.dynamodb.conditions import Key
import os, datetime, random, string, json
import telebot
import boto3

# Extra commands
    #/clean - clear all table
    #/end - delete all tables

load_dotenv()
plants = ['basil', 'chilli', 'tomato']
TOKEN = os.environ['TOKEN']
CHAT_ID = os.environ['CHAT_ID']
url = 'http://localhost:4566'

bot = telebot.TeleBot(TOKEN)

def create_table():
    dynamoDb = boto3.resource('dynamodb', endpoint_url=url)
    greenhouseTable = dynamoDb.create_table(
    TableName='greenhouse',
    KeySchema=[
        {
            'AttributeName': 'plant_id',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'plant_id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'userID',
            'AttributeType': 'S'
        }
    ],
    GlobalSecondaryIndexes=[
        {
            'IndexName': 'cid-index',
            'KeySchema': [
                {
                    'AttributeName': 'userID',
                    'KeyType': 'HASH',
                },
            ],
            'Projection': {
                'ProjectionType': 'ALL',
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 2,
                'WriteCapacityUnits': 2,
            }
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

    measurementOutputSensorTable = dynamoDb.create_table(
        TableName='measurement',
        KeySchema=[
            {
                'AttributeName': 'sensor_id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'sensor_id',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    print("Table status: ", greenhouseTable.table_status)
    print("Table status: ", measurementOutputSensorTable.table_status)

def query_data_dynamodb(table):
    dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    measurementTable = dynamodb.Table(table)
    response = measurementTable.scan()
    return response['Items']

def query_data_dynamodb_gsi(table, indexName, columnName, userID):
    dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    table = dynamodb.Table(table)
    response = table.query(
        IndexName=indexName,
        KeyConditionExpression=Key(columnName).eq(userID)
    )
    return response['Items']

def read_data(table):
    response = table.scan()
    items = response['Items']
    return items

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def loadData(cid):
    dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    greenhouseTable = dynamodb.Table('greenhouse')
    for i in range(len(plants)):
        measure_date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        moisture = random.randint(0, 100)
        light = random.randint(0, 100)
        temperature = round(random.uniform(-5.0, 30.0), 2)
        plant_id = plants[i] + '_' + str(cid)
        item = {
            'plant_id': str(plant_id),
            'userID': str(cid),
            'measure_date': str(measure_date),
            'temperature(°)': str(temperature),
            'moisture(%)': str(moisture),
            'light(lx)': str(light)
        }
        greenhouseTable.put_item(Item=item)
        print("Add item: ", item)

def split_queue_name(queueName):
    userID = queueName.split('_')[0]
    plantID = queueName.split('_')[1]
    return userID, plantID
    
@bot.message_handler(commands=['start'])
def first_start(message):
    # create table dynamodb
    try:
        create_table()
    except Exception as e:
        print(e)
    cid = message.chat.id
    name = message.chat.username
    bot.send_message(cid, f"Hi, *{name}* and welcome, I am building the infrastructure to run your home greenhouse! Give me a moment ☺", parse_mode='Markdown')
    # Create queue for each plant and each user
    sqs = boto3.resource('sqs', endpoint_url=url)
    for plant in plants:
        qname = plant+'_'+str(cid)
        queue = sqs.create_queue(QueueName=qname)
        print(queue.url)

    bot.send_message(
        cid, f"Greenhouse initialised! Now type _/help_ to get the list of commands.", parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, """\
    Hi 👋, now you can manage your home greenhouse with ease, choose a command!

    ❓/help - Write this help
    🌱/plants - Return user's plants
    🌡/iSensor - write this helpXXXX
    💧/oSensor - write this helpXXXX
    🔛/ONactuators - Activate all actuators
    🚫/OFFactuators - Deactivate all actuators\
    """)

@bot.message_handler(commands=['plants'])
def plants_command(message):
    cid = message.chat.id
    name_plant_list = []

    test = query_data_dynamodb_gsi('greenhouse', 'cid-index', 'userID', str(message.chat.id))
    for item in test:
        plant, userID= split_queue_name(item['plant_id'])
        name_plant_list.append(plant)

    if len(name_plant_list) == 0:
        bot.send_message(cid, f"You have no plants, or there are no measurements available 😕")
    else:
        one_string = ' 🌱 '.join(name_plant_list).upper()
        bot.send_message(cid, f"Your plants in the 🎍 greenhouse: {one_string}")


@bot.message_handler(commands=['iSensor'])
def iSensor_command(message):
    cid = message.chat.id
    lambda_client = boto3.client('lambda', endpoint_url=url)
    response = lambda_client.invoke(
        FunctionName='passDataInDynamo',
        InvocationType='RequestResponse',
        Payload=json.dumps({'cid': cid})
    )
    print(f"Lambda function \"passDataInDynamo\" return: {response['StatusCode']} status code")
    bot.send_message(cid, f"Data loaded!")

@bot.message_handler(commands=['oSensor'])
def oSensor_command(message):
    cid = message.chat.id
    responseLambda = boto3.client('lambda', endpoint_url=url)
    responseLambda = responseLambda.invoke(
        FunctionName='activeOutputSensor',
        InvocationType='RequestResponse',
        Payload=json.dumps({'cid': cid})
    )
    bot.send_message(cid, f"Active actuators: ")
    responseMeasurementTable = query_data_dynamodb('measurement')
    for item in responseMeasurementTable:
        sensor, userID= split_queue_name(item['sensor_id'])
        bot.send_message(cid, f"🟢 _{sensor}_ ➡ _{item['plant']}_ for {item['lifetime']} 🕐", parse_mode='Markdown')

    print(f"Lambda function \"activeOutputSensor\" return: {responseLambda['StatusCode']} status code")

@bot.message_handler(commands=['ONactuators'])
def ONSensor_command(message):
    cid = message.chat.id
    dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    responseGreenhouse = query_data_dynamodb('greenhouse')
    responseMeasurementTable = dynamodb.Table('measurement')

    activationDate = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    for item in responseGreenhouse:
        plant_name, userID= split_queue_name(item['plant_id'])
        plants = []
        plants.append(plant_name)
        if userID == str(cid):
            for plant in plants:
                item_sprinkler = {
                    'sensor_id': 'Sprinkler' + '_' + str(userID) + '_' + str(plant),
                    'activationDate': str(activationDate),
                    'lifetime': str(random.randint(1,10))+'min'
                }
                responseMeasurementTable.put_item(Item=item_sprinkler)
                item_lamp = {
                    'sensor_id': 'Lamp' + '_' + str(userID) + '_' + str(plant),
                    'activationDate': str(activationDate),
                    'lifetime': str(random.randint(1,10))+'min'
                }
                responseMeasurementTable.put_item(Item=item_lamp)
    
    bot.send_message(cid, f"🟢 All actuators activated 🟢")

@bot.message_handler(commands=['OFFactuators'])
def OFFSensor_command(message):
    cid = message.chat.id
    dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    measurementTable = dynamodb.Table('measurement')
    response = measurementTable.scan()
    items = response['Items']
    for item in items:
        measurementTable.delete_item(Key={'sensor_id': item['sensor_id']})
    bot.send_message(cid, f"❌ All actuators deactivated ❌")

@bot.message_handler(commands=['clean'])
def clean_command(message):
    dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    greenhouseTable = dynamodb.Table('greenhouse')
    response = greenhouseTable.scan()
    items = response['Items']
    for item in items:
        greenhouseTable.delete_item(Key={'plant_id': item['plant_id']})

    measurementTable = dynamodb.Table('measurement')
    response = measurementTable.scan()
    items = response['Items']
    for item in items:
        measurementTable.delete_item(Key={'sensor_id': item['sensor_id']})
    bot.reply_to(
        message, f"All item removed in GREENHOUSE and MEASUREMENT tables")

@bot.message_handler(commands=['end'])
def end_command(message):
    # delete all tables
    dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    dynamodb.Table('greenhouse').delete()
    dynamodb.Table('measurement').delete()
    bot.reply_to(message, f"Tables deleted")

bot.polling()