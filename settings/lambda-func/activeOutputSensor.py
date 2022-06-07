# leggo i dati dalla tabella greenhouse e attivo sensori (simulato scrivendo su un altra tabella measurements)
import boto3
import datetime
import json
import string, random
import os
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    url = 'http://localhost:4566'
    
    dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    
    greenhouseTable = dynamodb.Table('greenhouse')
    response = greenhouseTable.scan()
    items = response['Items']

    measurementOutputSensorTable = dynamodb.Table('measurement')
    
    for i in items:
        plant = i['plant']
        light = i['light(lx)']
        temperature = float(i['temperature(°)'])
        moisture = int(i['moisture(%)'])
        measure_date = i['measure_date']
        print(f"Plant: {plant} Light: {light} Temperature: {temperature} Moisture: {moisture} Measure_date: {measure_date}")
        activationDate = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        #per regolare umidità attiviamo innaffiatoio
        if moisture < 50:
            randomId = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
            item = {
                'sensor': 'Sprinkler',
                'activationDate': str(activationDate),
                'plant': plant,
                'state': 'ON',
                'lifetime': str(random.randint(0,10))+'min',
                'measureID': str(randomId)
            }
            measurementOutputSensorTable.put_item(Item=item)
        else:
            print(f"No need to activate sprinkler for plant: {plant}")

        #per regolare temperatura attiviamo lampada
        if temperature < 15:
            randomId = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
            item = {
                'sensor': 'lamp',
                'activationDate': str(activationDate),
                'plant': plant,
                'state': 'ON',
                'lifetime': str(random.randint(0,10))+'min',
                'measureID': str(randomId)
            }
            measurementOutputSensorTable.put_item(Item=item)
        else:
            print(f"No need to activate lamp for plant: {plant}")