import json
import telebot
import datetime
import boto3

TOKEN = '5503375377:AAEc_dP-_lESOg2_LDoBdoqbg2m7hfn1wtQ'

def message_check_in(event):
    
    # Extract the message key over payload's body
    message = json.loads(event['body'])['message']
    
    # Split between three variables bellow
    chat_id = message['chat']['id'] # Chat ID will guide your chatbot reply 
    sender = message['from']['first_name'] # Sender's first name, registered by user's telegram app
    text = message['text'] # The message content
    
    return chat_id, sender, text

def lambda_handler(event, context):
    
    chat_id, sender, text = message_check_in(event)
    
    bot = telebot(TOKEN)
    
    if text.lower().strip() == "/time":
    
        current_time = datetime.strftime(datetime.now(), "%H:%M:%S")
        bot.send_message(chat_id, "Right now its {} UTC.".format(current_time))
        
    # Return instructions to user with /help command.
    elif text.lower().strip() == "/help":
        
        existing_commands = """
        
        These are the commands you can ask to me: \n\n
        
        /time to get the current hour. \n
        
        /add to insert new items on your grocery shoplist. \n
        
        Example: /add 3 Bananas - means you're adding three bananas to the list.
        
        """.strip()
    else:
        pass
    