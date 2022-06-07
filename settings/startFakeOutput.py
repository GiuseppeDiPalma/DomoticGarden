import boto3
import datetime
import random
import string

url = 'http://localhost:4566'
dynamodb = boto3.resource('dynamodb', endpoint_url=url)

greenhouseTable = dynamodb.Table('greenhouse')

#read data from dynamodb
def read_data(table):
    response = table.scan()
    items = response['Items']
    return items

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

measurementOutputSensorTable = dynamodb.Table('measurement')
sensorOutputType = ['Sprinkler', 'light']
data = read_data(greenhouseTable)

#for each plant take value of light and temperature
for i in data:
    plant = i['plant']
    light = i['light(lx)']
    temperature = float(i['temperature(°)'])
    moisture = int(i['moisture(%)'])
    measure_date = i['measure_date']
    #print("Plant: ", plant, " Light: ", light, " Temperature: ", temperature, " Moisture: ", moisture, " Measure_date: ", measure_date)
    print(f"Plant: {plant} Light: {light} Temperature: {temperature} Moisture: {moisture} Measure_date: {measure_date}")
    activationDate = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    #per regolare umidità attiviamo innaffiatoio
    if moisture < 50:
        item = {
            'sensor': 'Sprinkler',
            'activationDate': str(activationDate),
            'plant': plant,
            'state': 'ON',
            'lifetime': str(random.randint(0,10))+'min',
            'measureID': id_generator(5)
        }
        measurementOutputSensorTable.put_item(Item=item)
    else:
        print(f"No need to activate sprinkler for plant: {plant}")

    #per regolare temperatura attiviamo lampada
    if temperature < 15:
        item = {
            'sensor': 'lamp',
            'activationDate': str(activationDate),
            'plant': plant,
            'state': 'ON',
            'lifetime': str(random.randint(0,10))+'min',
            'measureID': id_generator(5)
        }
        measurementOutputSensorTable.put_item(Item=item)
    else:
        print(f"No need to activate lamp for plant: {plant}")