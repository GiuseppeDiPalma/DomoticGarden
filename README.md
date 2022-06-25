# Domotic Garden - Farming at home

<p align="center">
    <img src="resources/greenhouse.png" width=200/>
</p>

### 💡 Idea and reason

Over the years I have always tried to grow plants (chilli, salad, basil, etc.). I have noticed that this idea is very difficult to realise 😴, for various reasons: little space, little green thumb, but the biggest problem is lack of time. 
The **DOMOTIC GARDEN 🎍** could solve this problem!

My idea is to create a small greenhouse, capable of reproducing a functional ecosystem for the growth of different plants. With the use of sensors, placed in the greenhouse, I want to retrieve the parameters of the plants.
With these sensors, I can monitor:

* 🌡Temperature (thermostat);
* ☀ Light Intensity (Luminosity);
* 💧 Soil moisture (Soil moisture).

After collecting this data, the idea is to activate actuators, placed inside the greenhouse.
The actuators inside the greenhouse are, for each plant:

* 💡 Lamp;
* ⛲ Sprinkler;

These actuators are activated for a specific purpose, based on certain information about the cultivation of pot plants.

#### 🎈 How does it work?

Sensors, placed inside each plant in the greenhouse, collect data and publish them on tails. The data is collected by a lambda function and stored in the database (dynamodb).  Then another lambda function reads the data into the database and decides whether to activate the actuators in the plants. There is one last function that again reads the data of the active actuators and if their duration is over, sets them to off.

Everything can be managed and monitored via a telegram bot (![@domoticgarden_bot](https://t.me/domoticgarden_bot)). The bot can manage several users at the same time, allowing the individual user to obtain information only on his or her greenhouse. The user can control the plants in his greenhouse, can force the reading of data, can control active actuators, on/off all actuators.

##### Prerequisites

- [Docker](https://www.docker.com/)
- [AWS CLI](https://awscli.amazonaws.com/v2/documentation/api/latest/index.html)
- [Boto3](https://github.com/boto/boto3)
- [Telebot](https://github.com/eternnoir/pyTelegramBotAPI)

Clone repository:
```bash
https://github.com/GiuseppeDiPalma/DomoticGarden
```

Install python requirements
```bash
pip install -r /path/to/requirements.txt
```

Launch [Docker](https://www.docker.com/) run [localStack](https://localstack.cloud/):
```bash
docker run --rm -it -p 4566:4566 -p 4571:4571 localstack/localstack
```

Start Telegram bot:
```python
python settings/telegram-bot/telegramBot.py
```

On bot [@domoticgarden_bot](https://t.me/domoticgarden_bot) start, in case it was already started give **/start**

Upload lambda function and test it:
```bash
./startAWSres.sh
```

#### This is a view of the general infrastructure

<p align="center">
    <img src="resources/infrastructure.png" width=500/>
</p>

#### 🧰 Toolbox

- 3-input sensors for plant;
- 2-actuator sensors for plant;
- Amazon SQS to collect and distribute data;
- Dynamodb to store data;
- Telegram bot for monitor and run real-time lambda.

#### 🕵️‍♂️ Implementation details

**TelegramBot commands**
- _/help_ - Write hel message
- _/plants_ - Return user's plants
- _/sensor_ - Get latest measurements (lambda func: passDataInDynamo)
- _/actuator_ - Active actuators if values require it (lambda func: activeOutputSensor)
- _/ONactuators_ - Activate all actuators
- _/OFFactuators_ - Deactivate all actuators

**Lambda functions** 

- _**activeMonitoring**_: It randomly generates data (taken from the sensors on the plants), then publishes a message on the queue of the sensor.
- _**passDataInDynamo**_: Reads messages from the queue(s) and adds data to the dynamodb.
- _**activeOutputSensor**_: It reads data from the dynamodb and decides whether to activate the actuators.
- _**switchOffActuator**_: Switches actuators off according to duration.

#### 🔮 In the future

* Add sensor to take pictures of the plant at various times and use artificial intelligence to dose the plants.
* Improving the user interface.
* Generate graphs.
* Allow users to be able to add plants from telegram bots.