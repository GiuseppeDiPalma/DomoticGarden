from dotenv import load_dotenv
from boto3.dynamodb.conditions import Key
import os, datetime, random, string, json
import telebot
import boto3

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
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
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
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10,
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
                'AttributeName': 'measureID',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'measureID',
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

def query_data_dynamodb(table, indexName, columnName, userID):
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
        item = {
            'id': id_generator(5),
            'userID': str(cid),
            'plant': plants[i],
            'measure_date': str(measure_date),
            'temperature(°)': str(temperature),
            'moisture(%)': str(moisture),
            'light(lx)': str(light)
        }
        greenhouseTable.put_item(Item=item)
        print("Add item: ", item)

def unique_item_list(list):
    unique_list = []
    for x in list:
        if x not in unique_list:
            unique_list.append(x)
    return unique_list

@bot.message_handler(commands=['start'])
def first_start(message):
    # create table dynamodb
    try:
        create_table()
    except Exception as e:
        print(e)
    cid = message.chat.id
    name = message.chat.username
    bot.send_message(
        cid, f"Hi, *{name}* and welcome, I am building the infrastructure to run your home greenhouse! Give me a moment ☺", parse_mode='Markdown')
    bot.send_message(
        cid, f"We start with three predefined 🌱plants: _Basil_ | _Tomato_ | _Chilli_.", parse_mode='Markdown')

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

    ❓/help - write this help
    🌱/plants - write this help
    💧/oSensor - write this help
    🌡/iSensor - write this help
    🔛/ONSensor - write this help
    🚫/OFFSensor - write this help
    🧹/clean - 
    /end - delete tables\
    """)
    #bot.send_message(cid, "Howdy, how are you doing?")


@bot.message_handler(commands=['plants'])
def plants_command(message):
    cid = message.chat.id
    # scan table and get all plants
    name_plant_list = []
    measuredate_plant_list = []

    test = query_data_dynamodb(
        'greenhouse', 'cid-index', 'userID', str(message.chat.id))
    for item in test:
        plants_dict = {
            'id': item['id'],
            'plant': item['plant'],
            'temperature': item['temperature(°)'],
            'moisture': item['moisture(%)'],
            'light': item['light(lx)'],
            'measure_date': item['measure_date']
        }

        for key, value in plants_dict.items():
            if key == 'plant':
                name_plant_list.append(value)
            # get last 3 measurements for each plant
            if key == 'measure_date':
                measuredate_plant_list.append(value)

    unique = unique_item_list(name_plant_list)
    one_string = ' 🌱 '.join(unique).upper()
    bot.send_message(cid, f"Your plants in the greenhouse: {one_string}")


@bot.message_handler(commands=['oSensor'])
def oSensor_command(message):
    bot.reply_to(message, f"Hai scelto il comando {message.text}")


@bot.message_handler(commands=['iSensor'])
def iSensor_command(message):
    #invoke lambda function
    cid = message.chat.id
    lambda_client = boto3.client('lambda')
    response = lambda_client.invoke(
        FunctionName='iot_lambda_function',
        InvocationType='RequestResponse',
        Payload=json.dumps({'cid': cid})
    )
    print(response)
    bot.reply_to(message, f"Hai scelto il comando {message.text}")


@bot.message_handler(commands=['ONSensor'])
def ONSensor_command(message):
    bot.reply_to(message, f"Hai scelto il comando {message.text}")


@bot.message_handler(commands=['OFFSensor'])
def OFFSensor_command(message):
    bot.reply_to(message, f"Hai scelto il comando {message.text}")


@bot.message_handler(commands=['clean'])
def clean_command(message):
    dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    greenhouseTable = dynamodb.Table('greenhouse')
    response = greenhouseTable.scan()
    items = response['Items']
    for item in items:
        greenhouseTable.delete_item(Key={'id': item['id']})

    measurementTable = dynamodb.Table('measurement')
    response = measurementTable.scan()
    items = response['Items']
    for item in items:
        greenhouseTable.delete_item(Key={'measureID': item['measureID']})
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
