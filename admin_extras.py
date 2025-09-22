from flask import *
from database import *
from helpers import SendMessage
import threading


Extras = Blueprint('Extras', __name__, url_prefix='/extras')

@Extras.before_request
def before_request():
    if not session.get('is_loggedin') and not session.get('username'):
        return redirect(url_for('auth.login'))
    else:
        g.username = session.get('username')
    
@Extras.route('/report/user/timeout/<lockTime>')
def user_timeout(lockTime):
    Message = f"Timeout Error Occured, During Handling Resetting Over Page. TimeOut Occured: {lockTime}"
    threading.Thread(SendMessage, args=(Message)).start()
    return 'Ok'

