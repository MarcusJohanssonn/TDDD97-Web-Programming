from flask import Flask, request, jsonify, current_app
from flask_sockets import Sockets
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
import database_helper
import json
import random
import secrets
from geventwebsocket import WebSocketError
import uuid
import yagmail
import keyring.backend


app = Flask(__name__)
print(app)
print(__name__)
app.debug = True

sockets = Sockets(app)
logged_in_users = dict()
totalusers = 0

@app.teardown_request
def after_request(exception):
    database_helper.disconnect_db()

@app.route('/')
def hello_world():
    return current_app.send_static_file('client.html')

#-------------------- SIGNUP SIGNIN SIGNOUT -------------------------------------

@app.route('/signup', methods = ['POST'])
def sign_up():
    global totalusers
    data = request.get_json()
    #return str(len(data['firstname']))
    if validateData(data):
        if database_helper.find_user(data['email'], data['password']):
            return json.dumps({"msg" : "user with that email already exists"}), 500
        if validatePW(data['password']):
            result = database_helper.save_user(data['email'], data['password'],
            data['firstname'], data['familyname'], data['gender'],
            data['city'], data['country'])
            if result == True:
                totalusers += 1
                return json.dumps({"message" : "User saved!"}), 200
            else:
                return json.dumps({"message" : "Something went wrong!"}), 500
        else:
            return json.dumps({"message": 'Password is too short'}), 400
    else:
        return json.dumps({"message": 'One or more fields are empty, retry!'}), 400


@app.route('/signin', methods = ['POST'])
def sign_in():
    data = request.get_json()
    email = data['email']

    if (database_helper.find_user(data['email'], data['password'])):     #verify with database password,
        userToken = secrets.token_hex(12)       #CREATE TOKEN
        if database_helper.login_user(data['email'], userToken):
             return jsonify(success="true", message="Login checks outasdasd B)", token=userToken) #SAVE TOKEN
        else:
             return jsonify(success=False, message="couldnt add a user with that email")
    else:
        return 'wrong credentials', 400

@app.route('/signout', methods = ['POST'])
def signout():
    userToken = request.headers.get('token')   # Got THROUGH request.header() instead  #have to send in token as json string for now
    if database_helper.find_active_user(userToken):
        if database_helper.signout_user(userToken):
             return jsonify(success="true", message="Logout successfull")
        else:
             return jsonify(success=False, message="Couldnt log out")
    else:
        return jsonify(success=False, message="User not logged in")

#-------------------------------------------------------------------------------

#------------------ CHANGE PASSWORD RESET PASSWORD -----------------------------

@app.route('/changePW', methods = ['POST'])
def changePW():
    data = request.get_json()
    oldPW = data['password']
    newPW = data['newPW']

    userToken = request.headers.get('token')   # Got THROUGH request.header() instead

    if (oldPW == newPW):
        return jsonify(success=False, message="dont use same password")
    if not validatePW(newPW):
        return jsonify(success=False, message="use a longer password")

    email = database_helper.get_email_by_token(userToken)
    if email is None:
        return jsonify(success=False, message="Cant find logged in user")


    if database_helper.find_user(email, oldPW):
        if database_helper.change_user_PW(email, newPW):
            return jsonify(success=True, message="successfully changed pw")
        else:
            return jsonify(success=False, message="Couldnt change pw")
    else:
        return jsonify(success=False, message="Password is wrong for that email")


def make_key():
    return uuid.uuid4()

@app.route('/forgotpw', methods = ['POST'])
def resetPassword():
    #frst kolla att den mailen finns reggad
    data = request.get_json()
    email = data['email']

    if (database_helper.find_email(data['email'])):     #verify with database,
        key = make_key()

        if database_helper.change_user_PW(email, str(key)):
            pw = keyring.get_password("yagmail", "kallbergz@gmail.com")
            yag = yagmail.SMTP('kallbergz@gmail.com', pw)
            contents = [
                "Hello someone requested a password reset for this mail in Twidder, here is your new password: ", str(key)
            ]
            yag.send(email, 'Twidder New Password', contents)
            return jsonify(success=True, message="Email sent", data=key)
        else:
            return jsonify(success=False, message="Couldnt change pw for that email")
    else:
        return jsonify(success=False, message="couldnt find email"), 400

    #generera ett nytt lsenord till den mailen
    #ndra i databasen
    #skicka mail


#-------------------------------------------------------------------------------

#------------------- SEND MESSAGE BROWSE MESSAGETOKEN --------------------------
@app.route('/sendmessage', methods = ['POST'])
def sendmessage():
    data = request.get_json()   #have to send in token as json string for now
    senderToken = request.headers.get('token')   # Got THROUGH request.header() instead
    reciever = data['reciever']
    message = data['message']

    emailSender = database_helper.get_email_by_token(senderToken)
    if emailSender is None:
        return jsonify(success=False, message="Cant find email with that token")

    if database_helper.post_message(message, reciever, emailSender):
         return jsonify(success=True, message="Sent message")
    else:
         return jsonify(success=False, message="Failed to send message")

#This is for the "home page", for that case we use the token to get data
@app.route('/user/', methods = ['GET'])
def data_token():
    token = request.headers.get('token')        #Was old verision that used "args.get"
    if database_helper.find_active_user(token):
        email = database_helper.get_email_by_token(token)
        if email is None:
            return jsonify(success=False, message="Cant find email with that token")
        else:
            result = database_helper.data_by_email(email)
            user = {'email': result[0], 'firstname': result[1], 'familyname': result[2], 'gender': result[3], 'city': result[4], 'country': result[5]}
            return jsonify(success=True, message="Fetched data", data=user)
    else:
        return jsonify(success=False, message="Cant find active user with that token")



#This one is for when we browse a user and acquire the data to show at their ove"home page"
@app.route('/browseuser/', methods = ['GET'])
def find_by_email():
    email = request.args.get('email')
    userToken = request.headers.get('token')

    if database_helper.find_active_user(userToken):
        if email is None:
            return jsonify(success=False, message="Cant find email with that token")
        else:
            result = database_helper.data_by_email(email)
            user = {'email': result[0], 'firstname': result[1], 'familyname': result[2], 'gender': result[3], 'city': result[4], 'country': result[5]}
            return jsonify(success=True, message="Fetched data", data=user)
    else:
        return jsonify(success=False, message="User not logged in")


#This one is for when we browse a user and acquire messages for that browsed email and the signed in users token
@app.route('/browse/', methods = ['GET'])
def messagebyemail():
    email = request.args.get('email')
    userToken = request.headers.get('token')

    if database_helper.find_active_user(userToken):
        if email is None:
            return jsonify(success=False, message="Cant find email")
        else:
            #email = email[0]
            result = database_helper.message_by_email(email)
            return jsonify(success=True, message="successfully found messages", messages=result)
    else:
        return jsonify(success=False, message="User not logged in")

@app.route('/data/', methods = ['GET'])
def getdata():
    totalusers = database_helper.get_nr_users()
    userToken = request.headers.get('token')   # Got THROUGH request.header() instead
    email = database_helper.get_email_by_token(userToken)

    if email is None:
        return jsonify(success=False, message="Cant find email with that token")
    else:
        result = database_helper.message_by_email(email)

    nrofmessages = (len(result))
    users = (len(logged_in_users.keys()))
    #print(logged_in_users.keys())
    users = database_helper.get_nr_online_users()
    totsent = database_helper.get_nr_send_posts(email)
    print(totsent)
    return jsonify(success=True, message="i have no clue", messagenr=nrofmessages, onlineusers=users, total=totalusers, sent=totsent)



#To get messages through the signed in users token
@app.route('/messagetoken', methods = ['GET'])
def messagebytoken():
    userToken = request.headers.get('token')   # Got THROUGH request.header() instead
    email = database_helper.get_email_by_token(userToken)

    if email is None:
        return jsonify(success=False, message="Cant find email with that token")
    else:

        result = database_helper.message_by_email(email)
        return jsonify(success=True, message="Fetched messages", messages=result)

def validatePW(password):
    if (len(password) <= 3):
        return False
    return True

def validateData(data):
    for key,value in data.items():
        if(len(value) == 0):
            return False
    return True

#-------------------------------------------------------------------------------

#-------------------------- API SHIT -------------------------------------------

@sockets.route("/api")
def ws_email(ws):
  if request.environ.get('wsgi.websocket'):
    ws = request.environ['wsgi.websocket']
    obj = ws.receive()      # tokens
    email = database_helper.get_email_by_token(obj)
    if email is not None:

        if email in logged_in_users:        #logged in users is the dictionary
            if not logged_in_users[email] == ws:
                old_user = logged_in_users[email]
                try:
                    print(old_user)
                    old_user.send("logout")
                except:
                    print("test")
                del logged_in_users[email]

        logged_in_users[email] = ws

        while True:
            try:
                ws.receive()
            except:
                return ""

    return "asd"



if __name__ == '__main__':
    http_server = WSGIServer(('',5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
