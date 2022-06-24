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

def get_difference_seconds(date_total, date2=datetime.datetime.now()):
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
        transform = transform_minutes(item['lifetime'])
        sum_date = sum_dates(item['activationDate'], transform)
        diff_2 = get_difference_seconds(sum_date)
        if diff_2 < 0:
            print(f"{item['sensor_id']} is off")
            delete_item('measurement', 'sensor_id', 'sensor_id')
        else:
            print(f"{item['sensor_id']} is on")