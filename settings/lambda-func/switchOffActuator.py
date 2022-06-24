import time
import boto3
import datetime

url='http://localhost:4566'

def query_data_dynamodb(table):
    dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    measurementTable = dynamodb.Table(table)
    response = measurementTable.scan()
    return response['Items']

def transform_minutes(minutes):
    minutes = minutes.replace('min', '')
    minutes = int(minutes)
    days = minutes // 1440
    minutes = minutes % 1440
    hours = minutes // 60
    minutes = minutes % 60
    return datetime.timedelta(days=days, hours=hours, minutes=minutes)

def get_difference_seconds(date_total, date2):
    difference = date_total - date2
    return difference.total_seconds()

def sum_dates(date1, date2):
    date1 = datetime.datetime.strptime(date1, '%d-%m-%Y %H:%M:%S')
    return date1 + date2

def delete_item(table, key_id, key_value):
    dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    table = dynamodb.Table(table)
    response = table.scan()
    items = response['Items']
    for item in items:
        table.delete_item(Key={key_id: item[key_value]})

def lambda_handler(event, context):
    data = query_data_dynamodb('measurement')
    for item in data:
        str_to_datetime = transform_minutes(item['lifetime'])
        sum = sum_dates(item['activationDate'], str_to_datetime)
        diff = get_difference_seconds(sum, datetime.datetime.now())
        #print(f"activationDate: {item['activationDate']} | lifetime: {str_to_datetime} | sum: {sum} | diff: {diff}")
        if diff < 0:
            print(f"{item['sensor_id']} verrà spento")
            delete_item('measurement', 'sensor_id', 'sensor_id')
        else:
            print(f"{item['sensor_id']} resterà attivo, si spegnerà alle {sum}")