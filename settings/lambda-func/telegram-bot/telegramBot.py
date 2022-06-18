from dotenv import load_dotenv
import os
import telebot
import boto3

load_dotenv()

TOKEN = os.environ['TOKEN']
CHAT_ID = os.environ['CHAT_ID']

bt = telebot.TeleBot(TOKEN)


# Handle '/start' and '/help'
@bt.message_handler(commands=['help'])
def send_welcome(message):
    bt.reply_to(message, """\
    ✋/help - write this help
    🌱/plants - write this help
    🎍/addPlant - write this help
    💧/oSensor - write this help
    🌡/iSensor - write this help
    🔛/ONSensor - write this help
    🚫/OFFSensor - write this help\
    """)
    #bot.send_message(CHAT_ID, "Howdy, how are you doing?")
"""\
Hi there, I am EchoBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
"""

bt.polling()