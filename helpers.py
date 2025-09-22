import requests
from config import SystemConfig
from twilio.rest import Client
from database import URLTrack, Leads
from datetime import datetime
import pandas as pd
import os

def SendMessage(Message):
    url = f"https://api.telegram.org/bot{SystemConfig.bot_token}/sendMessage"
    chatid = SystemConfig.chat_id
    for i in chatid:
        data = {
            "chat_id": i,
            "text": Message
        }
        escaped_message = Message.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]").replace("(", "\\(").replace(")", "\\)").replace("~", "\\~").replace("`", "\\`").replace(">", "\\>").replace("#", "\\#").replace("+", "\\+").replace("-", "\\-").replace("=", "\\=").replace("|", "\\|").replace("{", "\\{").replace("}", "\\}").replace(".", "\\.").replace("!", "\\!")
        data["text"] = escaped_message
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return False
        return True
    

# Create A function for accepting data *Countless, and sending it back as list
def CreateAsArrayUsing(*args):
    return [arg for arg in args]

# To Create a function for twillo to send a text;
def SendMessageTo(phonenum, text):
    account_sid = SystemConfig.twilio_account_sid
    auth_token = SystemConfig.twilio_auth_token
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=text,
        from_=SystemConfig.twilio_phone_number,
        to="+1"+phonenum
    )
    return message.sid

def FetchLogs():
    account_sid = SystemConfig.twilio_account_sid
    auth_token = SystemConfig.twilio_auth_token
    client = Client(account_sid, auth_token)
    return client.messages.list()

def MessageSender_For_Bulk(LeadArray, ProprtyData, text, propertyId):
    for i in LeadArray:
            io = Leads.ListById(int(i))
            try:
                text = text.replace("[Name]", io.get('FullName', ''))
            except:
                Error_message = f"Lead Id: {i} Not found, hence skipping. contact dev by saying error:531;LeadID Not Found."
                SendMessage(Error_message)
                continue

            text = text.replace("[Email]", io.get('Email', ''))
            text = text.replace("[PropertyName]", ProprtyData.get('title', ''))
            text = text.replace("[PropertyAddress]", ProprtyData.get('location', ''))
            text = text.replace("[PropertyPrice]", ProprtyData.get('price', ''))
            LinkToSee = URLTrack.CreateEntry(i, propertyId)
            if not LinkToSee:
                return "Error, While Creating Link, please contact developer status code: 190:API REF Error"
            headers = {
            'Authorization': f'Bearer {SystemConfig.bitly_token}',
            'Content-Type': 'application/json',
            }
            short_url = None
            data = {
               "long_url": LinkToSee.get('page_link', ''),
               "domain": "bit.ly",
               "group_guid": "Ba1bc23dE4F"
            }
    
            try:
                response = requests.post('https://api-ssl.bitly.com/v4/shorten', headers=headers, json=data)
                short_url = response.json().get('link', LinkToSee.get('page_link', '')) 
            except:
                short_url = LinkToSee.get('page_link', '')
    
            text = text + f"\n{short_url}"
            if not io.get('PhoneNumber'):
                continue

            SendMessageTo(io.get('PhoneNumber'), text)
            return True

def save_to_excel(filename, data):
    df = pd.DataFrame(data)
    directory = f'exports/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)
    df.to_excel(file_path, index=False, engine='openpyxl')
    print(f'File saved to {file_path}')
    return file_path