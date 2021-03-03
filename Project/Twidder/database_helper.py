import sqlite3
from flask import g
DATABASE = 'database.db'

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(DATABASE)
    return db

def disconnect_db():
    db = getattr(g, 'db', None)
    if db is not None:
        g.db.close()
        g.db = None

def save_user(email, password, firstname, familyname, gender, city, country):
    try:
        get_db().execute("INSERT INTO user VALUES(?,?,?,?,?,?,?);", [email, password, firstname, familyname, gender, city, country])
        get_db().commit()
        return True
    except:
        return False

def get_nr_users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(email) FROM user")
    data = cursor.fetchone()
    cursor.close()
    return data

def get_nr_online_users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(email) FROM active_users")
    data = cursor.fetchone()
    cursor.close()
    return data

def get_nr_send_posts(email):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(sender) FROM messages WHERE sender=?", [email])
    data = cursor.fetchone()
    cursor.close()
    return data

def find_user(email, password):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT * FROM user WHERE email=? AND password=?', [email, password])
    data = cursor.fetchone()
    cursor.close()
    if(data == None):
        return False
    else:
        return True

def find_email(email):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM user WHERE email=?', [email,])
    data = cursor.fetchone()
    cursor.close()
    if(data == None):
        return False
    else:
        return True

def find_active_user(userToken):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT * FROM active_users WHERE token=?', [userToken])
    data = cursor.fetchone()
    cursor.close()
    if(data == None):
        return False
    else:
        return True

def find_active_user_email(email):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT token FROM active_users WHERE email=?', [email])
    data = cursor.fetchone()
    cursor.close()
    if(data == None):
        return False
    else:
        return data

def clear_active():
    db = get_db()
    db.execute('DELETE FROM active_users')
    db.commit()


def login_user(email, token):
    db = get_db()
    try:
        db.execute('INSERT OR REPLACE INTO active_users VALUES(?,?)', [email, token])
        db.commit()
        return True
    except:
        return False

def signout_user(userToken):
    db = get_db()
    try:
        db.execute("DELETE FROM active_users WHERE token = '" + userToken + "'")
        db.commit()
        return True
    except:
        return False

def change_user_PW(email, newPW):
    db = get_db()
    try:
        db.execute('UPDATE user SET password = ? WHERE email = ?', [newPW, email])
        db.commit()
        return True
    except:
        return False


def get_email_by_token(userToken):
    try:
        cursor = get_db().execute('SELECT email FROM active_users WHERE token LIKE ?', (userToken,))
        email = cursor.fetchone()
        return email[0]
    except:
        return False


def data_by_email(email):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('SELECT email, firstname, familyname, gender, city, country FROM user WHERE email LIKE ?', (email,))
        data = cursor.fetchone()
        return data
    except:
        return None


def post_message(message, reciever, sender):
    db = get_db()
    try:
        db.execute('INSERT INTO messages (message, sender, reciever) VALUES(?,?,?);', [message,sender,reciever])
        db.commit()
        return True
    except:
        return False


def message_by_email(email):
        cursor = get_db().execute('SELECT message, sender FROM messages WHERE reciever LIKE ?', [email])
        rows = cursor.fetchall()
        cursor.close()
        result = []
        for index in range(len(rows)):
            result.append(rows[index])
        return result


#WE DO NOT USE THIS ONE IS IT RIGHT???
def message_by_token(token):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT message, sender FROM messages WHERE reciever IN LIKE ?', [email])
        data = cursor.fetchone()
        return data

        cursor = get_db().execute('SELECT message FROM messages WHERE reciever LIKE ?', [email])
        rows = cursor.fetchall()
        cursor.close()
        result = []
        for index in range(len(rows)):
            result.append({'Messages': rows[index]})
        return result

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('SELECT message, sender FROM messages WHERE reciever IN LIKE ?', [email])
            data = cursor.fetchall()
            return data
        except:
            return None


#if we need password in data
def get_user_by_email(email):
    cursor = get_db().execute('SELECT * FROM user WHERE email LIKE ?', [email])
    rows = cursor.fetchall()
    cursor.close()
    result = []
    #can use fetchone
    for index in range(len(rows)):
        result.append({'data': rows[index]})
    return result
