import boto3
import datetime
import random
import string

url = 'http://localhost:4566'

dynamodb = boto3.resource('dynamodb', endpoint_url=url)

greenhouseTable = dynamodb.Table('greenhouse')
measurementOutputSensorTable = dynamodb.Table('measurement')

plants = ['basil', 'chilli', 'tomato']

for i in range(len(plants)):
    measure_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    moisture = random.randint(0, 100) #umidità
    light = random.randint(0, 100)
    temperature = round(random.uniform(-5.0, 30.0), 2) #quantità
    item ={
        'plant': plants[i],
        'measure_date': str(measure_date),
        'temperature(°)': str(temperature),
        'moisture(%)': str(moisture),
        'light(lx)': str(light)
    }
    greenhouseTable.put_item(Item=item)
    print("Add item: ", item)

sensorOutputType = ['Sprinkler', 'light']

spriklerState = ""
spriklerOnState = ""
lightState = ""
lightOnState = ""

#per regolare umidita attiviamo innaffiatoio
if moisture < 50:
    spriklerState = "ON"
    spriklerOnState = "10m"
else:
    spriklerState = "OFF"
    spriklerOnState = "-"

#per regolare temperatura attiviamo lampada
if temperature < 15:
    lightState = "ON"
    lightOnState = "10m"
else:
    lightState = "OFF"
    lightOnState = "-"

#function to generate random string
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

for plant in range(len(plants)):
    print("Plant: ", plants[plant])
    for outputSensor in sensorOutputType:
        for i in range(len(sensorOutputType)):
            print("Output sensor: ", outputSensor)
            activationDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if outputSensor == "Sprinkler":
                item ={
                    'sensorType': outputSensor,
                    'plant': plants[plant],
                    'state': spriklerState,
                    'lifetime': spriklerOnState,
                    'measureID': id_generator(5)
                }
            
            if outputSensor == "light":
                item ={
                    'sensorType': outputSensor,
                    'plant': plants[plant],
                    'state': lightState,
                    'lifetime': lightOnState,
                    'measureID': id_generator(5)
                }
            measurementOutputSensorTable.put_item(Item=item)
            print("Add item: ", item)
