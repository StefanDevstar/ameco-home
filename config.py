import os
from dotenv import load_dotenv

load_dotenv()

class SystemConfig:
    db_url = os.getenv('db_url')
    base_url = os.getenv('base_url', '')
    bot_token = os.getenv('bot_token', '')
    chat_id = os.getenv('chat_id', '').split(',')
    bitly_token = os.getenv('bitly_token', '')
    twilio_account_sid = os.getenv('twilio_account_sid', '')
    twilio_auth_token = os.getenv('twilio_auth_token', '')
    twilio_phone_number = os.getenv('twilio_phone_number', '')
