from flask import *
from database import Admin

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['pwd']
        if Admin.Authorize(username, password):
            session['is_loggedin'] = True
            session['username'] = username
            return redirect(url_for('admin.admin_home'))
        else:
            return render_template("admin/login.html", error="Invalid Credentials")
    else:
        if session.get('message'):
            return render_template('admin/login.html', success=session['message'])
        return render_template('admin/login.html')

@auth.route('/logout')
def logout():
    session.clear()
    session['message'] = "Logout success, cya later"
    return redirect(url_for('auth.login'))