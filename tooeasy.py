from flask import Flask, render_template,redirect,request,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,login_user,logout_user,login_required,UserMixin,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime
import os
import pymysql
import requests


#configurations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root@localhost/sample_db'
app.secret_key=os.urandom(24)
db=SQLAlchemy(app)
login_manager=LoginManager(app)
login_manager.login_view='login'

#database as a class
class reg(db.Model ,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(200),unique=True,nullable=False)
    password=db.Column(db.String(200),nullable=False)
    date_time=db.Column(db.Integer,default=datetime.utcnow)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self) -> str:
        return f"{self.id} - {self.email}"

#create the db
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(reg_id):
    return reg.query.get(int(reg_id))


#home route
@app.route('/')
def main():
    return redirect(url_for('user_reg'))

#reg route
@app.route('/reg',methods=['GET', 'POST'])
def user_reg():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        user_ex=reg.query.filter_by(email=email).first()
        if user_ex:
            flash('user acc already created')
            return redirect(url_for('user_login'))
        else:
            new_user=reg(email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('acc created')
            return redirect(url_for('user_login'))
    return render_template('reg.html')


   
#login route
@app.route('/login',methods=['GET', 'POST'])
def user_login():
    if request.method=='POST':
        emailr=request.form['email']
        passwordr=request.form['password']
        recaptcha_response = request.form.get('g-recaptcha-response')  # Get CAPTCHA token
        
        secret_key = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"
        captcha_verify_url = "https://www.google.com/recaptcha/api/siteverify"
        data = {
            'secret': secret_key,
            'response': recaptcha_response
        }
        response = requests.post(captcha_verify_url, data=data)
        result = response.json()

        if not result.get('success'):
            flash('reCAPTCHA verification failed. Please try again.', 'danger')
            return redirect(url_for('user_login'))

        if not result.get('success'):
            flash('reCAPTCHA verification failed. Please try again.', 'danger')
            return redirect(url_for('user_login'))
        
        
        user=reg.query.filter_by(email=emailr).first()

        if user and user.check_password(passwordr):
            login_user(user)
            flash('log in success')
            return redirect(url_for('user_reg'))
        else:
            flash('invalid email or password')

    
    return render_template('login.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)

