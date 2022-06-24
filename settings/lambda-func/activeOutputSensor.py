# leggo i dati dalla tabella greenhouse e attivo sensori (simulato scrivendo su un altra tabella measurements)
import boto3
import datetime
import string, random

#split the queue name into userID and plantID
def split_queue_name(queueName):
    userID = queueName.split('_')[0]
    plantID = queueName.split('_')[1]
    return userID, plantID

def lambda_handler(event, context):
    url = 'http://localhost:4566'
    
    dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    
    greenhouseTable = dynamodb.Table('greenhouse')
    response = greenhouseTable.scan()
    items = response['Items']

    measurementOutputSensorTable = dynamodb.Table('measurement')
    
    for i in items:
        plant, userID= split_queue_name(i['plant_id'])
        light = i['light(lx)']
        temperature = float(i['temperature(°)'])
        moisture = int(i['moisture(%)'])
        measure_date = i['measure_date']
        print(f"Plant: {plant} Light: {light} Temperature: {temperature} Moisture: {moisture} Measure_date: {measure_date}")
        activationDate = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        if moisture > 50:
            item = {
                'sensor_id': 'sprinkler' + '_' + str(userID) + '_' + str(plant),
                'activationDate': str(activationDate),
                'lifetime': str(random.randint(1,10))+'min'
                }
            measurementOutputSensorTable.put_item(Item=item)
        else:
            print(f"No need to activate sprinkler for plant: {plant}")

        if temperature < 15:
            item = {
                'sensor_id': 'lamp'+ '_' + str(userID) + '_' + str(plant),
                'activationDate': str(activationDate),
                'lifetime': str(random.randint(1,10))+'min'
                }
            measurementOutputSensorTable.put_item(Item=item)
        else:
            print(f"No need to activate lamp for plant: {plant}")