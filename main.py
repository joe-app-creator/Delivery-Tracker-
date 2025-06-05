from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import check_password_hash
import json
import os

app = Flask(__name__)
app.secret_key = 'super-secret-key'

login_manager = LoginManager()
login_manager.init_app(app)

# Load users
with open("users.json") as f:
    users = json.load(f)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/track', methods=['POST'])
def track():
    code = request.form['code'].upper()
    if os.path.exists("tracking_data.json"):
        with open("tracking_data.json") as f:
            data = json.load(f)
        status = data.get(code, "Tracking code not found.")
    else:
        status = "Tracking code not found."
    return render_template('status.html', code=code, status=status)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and check_password_hash(users[username], password):
            user = User(username)
            login_user(user)
            return redirect(url_for('admin'))
        else:
            return "Invalid login"
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        code = request.form['code'].upper()
        status = request.form['status']
        if os.path.exists("tracking_data.json"):
            with open("tracking_data.json") as f:
                data = json.load(f)
        else:
            data = {}
        data[code] = status
        with open("tracking_data.json", "w") as f:
            json.dump(data, f)
    return render_template('admin.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

import os

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
