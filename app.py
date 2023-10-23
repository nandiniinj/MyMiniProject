#importing required libraries

from flask import Flask,render_template,request,redirect, url_for, session, flash, get_flashed_messages
from flask_pymongo import PyMongo
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#log file

logging.basicConfig(filename="log.log",format='%(asctime)s :: %(levelname)s :: %(message)s',filemode="w")
logger=logging.getLogger(__name__)

#setting up the flask application

app = Flask(__name__)

app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydatabase'

#initializing MongoDB and global variables

db = PyMongo(app).db

user_data={}
theater=[]

#setting up smtp for sending email notifications
from_email='xyz@mail.com'
from_pass='xyz'

smtp = smtplib.SMTP("smtp-mail.outlook.com", 587)
smtp.starttls()
smtp.login(from_email, from_pass)


#***********************route definitions*********************************

#routing to the login page- the first page is the login page
@app.route('/') 
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


#routing to the home page
@app.route('/home/<uid>')
def home(uid):
    return render_template('index.html',user=uid)


#routing to the register page
@app.route('/signup',methods=['GET','POST'])
def signup():
    try:
        if request.method == 'POST':
            email = request.form['email']
            uid=email
            name = request.form['name']
            pass1 = request.form['password1']
            pass2 = request.form['password2']

            # Check if password fields match.
            if pass1 != pass2:
                flash('Passwords do not match', 'error')
                print(get_flashed_messages())
                return render_template('signup.html')
            else:
                user_exists = db.user.find_one({'email': email})

                if not user_exists:
                    msg = MIMEText("Logged in successfully")
                    msg["From"] = from_email
                    msg["To"] = email
                    msg["Subject"] = "Successfully registered"
                    msg.set_payload("The email is registered successfully!")
                    smtp.sendmail(from_email, email, msg.as_string())
                    smtp.quit()

                    # Add the new user to the database
                    db.user.insert_one({'email': email, 'password': pass1, 'name': name})
                    return redirect('/home/'+str(uid))
                else:
                    # The username already exists in the database, display an error message to the user
                    flash('User already registered! Please Login', 'error')
                    print(get_flashed_messages())
                    app.logger.error('Email already registered: %s', email)
                    return render_template('signup.html', error='Email already registered')
        return render_template('signup.html')
    
    except Exception as e:
        logger.error(f"An error occurred while processing signup request: {str(e)}")
        return render_template('signup.html', error='An error occurred. Please try again later.')


#checking the login credentials 
@app.route('/login_check',methods=['GET','POST']) 
def login_check():
    try:
        global user_data
        data = None
        if(request.method=='POST'):
            req=request.form
            session['email'] = req['email']
            session['password'] = req['password']
            req=dict(req)
            query=db.user.find({'email':req['email']})
            print(query)
            flag=0
            temp=None
            for x in query:
                if(x['email']==req['email']):
                    flag=1
                    temp=x
                    break
            if(flag==1):
                if(temp['password']==req['password']):
                    uid=req['email']
                    user_data[uid]={}
                    user_data[uid]['movie']=[]
                    user_data[uid]['num_tickets']=[]
                    user_data[uid]['seats']={}
                    return redirect('/home/'+str(uid))
                else:
                    flash('Incorrect Password!!', category='error')
                    data = 'Incorrect Password!!'
            else:
                logger.warn('Unregistered User')
                flash('User is not registered!!','error')
                print(get_flashed_messages())
        return render_template('login.html', data = data)
    
    except Exception as e:
        logger.error(f"An error occurred while processing your request: {str(e)}")
        return render_template('login.html', error='An error occurred. Please try again later.')


#logout page
@app.route('/logout',methods=['GET','POST'])
def logout():
    if 'email' in session:  
        session.clear()
    flash('You have been logged out.', 'info')
    return render_template('logout.html')


@app.route('/movies/<uid>')
def movies(uid):
    return render_template('movies.html',user=uid)

@app.route('/events/<uid>')
def events(uid):
    return render_template('events.html',user=uid)

@app.route('/bookshow/<uid>')
def bookshow(uid):
    return render_template('bookshow.html',user=uid)

@app.route('/food/<uid>')
def food(uid):
    return render_template('food.html',user=uid)

@app.route('/about/<uid>')
def about(uid):
    return render_template('about.html',user=uid)

@app.route('/contact/<uid>')
def contact(uid):
    return render_template('contact.html',user=uid)

@app.route('/theater/<uid>')
def seats(uid):
    return render_template('theater.html',user=uid)

@app.route('/success/<uid>')
def success(uid):
    return render_template('success.html',user=uid)


if __name__ == '__main__':  
    app.run()