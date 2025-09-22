from flask import *
from database import Leads, PropertyData, URLTrack
from config import SystemConfig
from helpers import SendMessageTo, MessageSender_For_Bulk, SendMessage
import requests, threading
from datetime import datetime
import traceback

Util = Blueprint('main', __name__)

@Util.before_request
def before_request():
    if not session.get('is_loggedin') and not session.get('username'):
        return redirect(url_for('auth.login'))
    else:
        g.username = session.get('username')

@Util.route('/send_text/single/<string:type>/<int:id>')
def show_avl(type, id):
    data = PropertyData.fetch_all()
    return render_template('admin/choose-property.html', properties=data, type=type, id=id)

@Util.route('/createLink/<string:type>/<int:leadId>/<int:propertyId>', methods=["POST", "GET"])
def createLink(type, leadId, propertyId):
    ProprtyData = PropertyData.fetch_pid(int(propertyId))
    LeadData = Leads.ListById(int(leadId))
    if not ProprtyData or not LeadData:
        return redirect(url_for('main.show_avl', type=type, id=leadId))
    
    if request.method == "GET":
        return render_template('admin/create-link.html', type=type, lead=LeadData, property=ProprtyData)
    
    else:
        form_data = request.form.to_dict()
        
        text = form_data['texttosend']
        try:
            text = text.replace("[Name]", LeadData.get('FullName', ''))
            text = text.replace("[Email]", LeadData.get('Email', ''))
            text = text.replace("[PropertyName]", ProprtyData.get('title', ''))
            text = text.replace("[PropertyAddress]", ProprtyData.get('location', ''))
            text = text.replace("[PropertyPrice]", ProprtyData.get('price', ''))
        except Exception as e:
       #     error_stack = ''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
            message = (
                f"Error Occurred while handling: {request} at {datetime.now()}\n\n"
                f"With Headers:\n{request.headers}\n\n"
                f"Error Stack:\n{error_stack}"
            )
            SendMessage(message)
            pass
        
        PhoneNum = LeadData.get('PhoneNumber', '')
        LinkToSee = URLTrack.CreateEntry(leadId, propertyId)
        if not LinkToSee:
            message = (
                f"Error Occurred while handling: {request} at {datetime.now()}\n\n"
                f"With Headers:\n{request.headers}\n\n"
                f"Error Stack:\nLinkToSee() Function returned: {LinkToSee} @ Line 60 of admin_utils.py"
            )
            SendMessage(message)
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
        try:
            text = text + f"\n{short_url}"
            SendMessageTo(PhoneNum, text)
        except Exception as e:
            error_stack = ''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
            message = (
                f"Error Occurred while handling: {request} at {datetime.now()}\n\n"
                f"With Headers:\n{request.headers}\n\n"
                f"Error Stack:\n{error_stack}"
            )
            SendMessage(message)
            return "Error, While Sending Message, please contact developer status code: 190:API REF Error"
            
        return "Success, Lead Notification Sent Successfully" 

@Util.route('/send_text/bulk/<string:type>/<ArrayList>')
def send_bulk(type, ArrayList):
    #List_of_Idea = ArrayList.split('_')
    data = PropertyData.fetch_all()
    return render_template('admin/choose-property.html', properties=data, type=type, id=ArrayList, data_bulk="yes")

# /createLinkBulk/{{String: type}}/{{Array: id}}/{{ int: property.PropertyID }}
@Util.route('/createLinkBulk/<string:type>/<ArrayList>/<int:propertyId>', methods=["POST", "GET"])
def createLinkBulk(type, ArrayList, propertyId): 
    List_of_Idea = ArrayList.split('_')
    ProprtyData = PropertyData.fetch_pid(int(propertyId))
    if not ProprtyData:
        return redirect(url_for('main.send_bulk', type=type, id=List_of_Idea))
    
    if request.method == "GET":
        return render_template('admin/create-link.html', type=type, leads=List_of_Idea, property=ProprtyData, bulk="yes")
    
    else:
        form_data = request.form.to_dict()
        text = form_data['texttosend']
        Thred = threading.Thread(target=MessageSender_For_Bulk, args=(List_of_Idea, ProprtyData, text, propertyId))
        Thred.start()
        ThreadId = Thred.ident
        return f"Message Scheduled, ThreadID: {ThreadId}"
        
