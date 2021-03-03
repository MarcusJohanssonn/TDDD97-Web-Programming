from flask import Flask, request, jsonify
import database_helper
import json
import random
import secrets

app = Flask(__name__)
app.debug = True

@app.teardown_request
def after_request(exception):
    database_helper.disconnect_db()

@app.route('/signup', methods = ['POST'])
def sign_up():
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
                return json.dumps({"msg" : "User saved!"}), 200
            else:
                return json.dumps({"msg" : "Something went wrong!"}), 500
        else:
            return 'Password is too short', 400
    else:
        return 'One or more fields are empty, retry!', 400


@app.route('/signin', methods = ['POST'])
def sign_in():
    data = request.get_json()

    if (database_helper.find_user(data['email'], data['password'])):     #verify with database password,
        userToken = secrets.token_hex(12)       #CREATE TOKEN
        if database_helper.login_user(data['email'], userToken):
             return jsonify(success="true", message="Login checks out B)", token=userToken) #SAVE TOKEN
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

@app.route('/changePW', methods = ['POST'])
def changePW():
    data = request.get_json()   #have to send in token as json string for now
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
    email = email[0]

    if database_helper.find_user(email, oldPW):
        if database_helper.change_user_PW(email, newPW):
            return jsonify(success=True, message="successfully changed pw")
        else:
            return jsonify(success=False, message="Couldnt change pw")
    else:
        return jsonify(success=False, message="Password is wrong for that email")

@app.route('/sendmessage', methods = ['POST'])
def sendmessage():
    data = request.get_json()   #have to send in token as json string for now
    senderToken = request.headers.get('token')   # Got THROUGH request.header() instead
    reciever = data['reciever']
    message = data['message']

    emailSender = database_helper.get_email_by_token(senderToken)
    if emailSender is None:
        return jsonify(success=False, message="Cant find email with that token")

    emailSender = emailSender[0]
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
            result = database_helper.data_by_email(email[0])
            user = {'email': result[0], 'firstname': result[1], 'familyname': result[2], 'gender': result[3], 'city': result[4], 'country': result[5]}
            return jsonify(success=True, message="Fetched data", data=user)
    else:
        return jsonify(success=False, message="Cant find active user with that token")



#This one is for when we browse a user and acquire the data to show at their "home page"
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


#To get messages through the signed in users token
@app.route('/messagetoken', methods = ['GET'])
def messagebytoken():
    userToken = request.headers.get('token')   # Got THROUGH request.header() instead
    email = database_helper.get_email_by_token(userToken)

    if email is None:
        return jsonify(success=False, message="Cant find email with that token")
    else:
        email = email[0]
        result = database_helper.message_by_email(email)
        return jsonify(result)

def validatePW(password):
    if (len(password) <= 3):
        return False
    return True

def validateData(data):
    for key,value in data.items():
        if(len(value) == 0):
            return False
    return True


if __name__ == '__main__':
    app.run()
