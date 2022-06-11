import json
import telebot
import boto3

CHAT_ID = ''
TOKEN = ''
WBH_URL = ''


def lambda_handler(event, context):
    bot = telebot.TeleBot(TOKEN)

    message = json.loads(event['body'])['message']
    rcv_message = message['text']
    message_username = message['from']['username']

    if rcv_message.lower().strip() == "/help":
        existing_commands = """
        These are the commands you can ask to me:\n
        /time to get the current hour. \n
        /add to insert new items on your grocery shoplist.
        """.strip()
        bot.send_message(CHAT_ID, existing_commands)
    
    elif rcv_message.lower().strip() == "/test":
        bot.send_message(CHAT_ID, "TEST MESSAGE!")
        bot.send_message(CHAT_ID, "rcv_message: " + rcv_message)
        bot.send_message(CHAT_ID, "username: " + message_username)