import os

class BuildConfig:
    def __init__(self):
        self.db_url = ""
        self.base_url = ""
        self.bot_token = ""
        self.chat_id = []
        self.bitly_token = ""
        self.twilio_account_sid = ""
        self.twilio_auth_token = ""
        self.twilio_phone_number = ""

    def get_user_input(self):
        self.db_url = input("Enter the MongoDB URL: ")
        self.base_url = input("Enter the base URL: ")
        self.bot_token = input("Enter the bot token: ")
        chat_id_input = input("Enter the chat IDs (comma-separated): ")
        self.chat_id = chat_id_input.split(",")
        self.bitly_token = input("Enter the Bitly token: ")
        self.twilio_account_sid = input("Enter the Twilio account SID: ")
        self.twilio_auth_token = input("Enter the Twilio auth token: ")
        self.twilio_phone_number = input("Enter the Twilio phone number: ")
            
    def check_pre_requesites(self):
        if os.path.exists('.env'):
            user_input = input("`.env` already exists. Are you sure you want to proceed? (y/n): ")
            if user_input.lower() != 'y':
                print("Exiting...")
                os.abort()
            else:
                return False
        

    def save_config(self):
        x = self.check_pre_requesites()
        if x == False:
            return

        with open('.env', 'w') as f:
            f.write(f"DB_URL={self.db_url}\n")
            f.write(f"BASE_URL={self.base_url}\n")
            f.write(f"BOT_TOKEN={self.bot_token}\n")
            f.write(f"CHAT_ID={','.join(self.chat_id)}\n")
            f.write(f"BITLY_TOKEN={self.bitly_token}\n")
            f.write(f"TWILIO_ACCOUNT_SID={self.twilio_account_sid}\n")
            f.write(f"TWILIO_AUTH_TOKEN={self.twilio_auth_token}\n")
            f.write(f"TWILIO_PHONE_NUMBER={self.twilio_phone_number}\n")
            print("Config saved successfully.")
            return

config = BuildConfig()
config.get_user_input()
config.save_config()