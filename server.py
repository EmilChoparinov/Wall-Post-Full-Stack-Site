from flask import Flask, render_template, session, redirect, flash, request
from mysqlconnection import MySQLConnector
import os, binascii, md5, re

server = Flask(__name__)
mysql = MySQLConnector(server, 'the_wall')
server.secret_key = "a secret key"

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX =re.compile(r'^[a-zA-Z]+$')

# MAIN ROUTE
@server.route('/')
def index():
    if 'first_name' in session:
        if 'id' in session:
            return redirect('/the_wall')
        else:
            return redirect('/login')
    else:
        return redirect('/register')


# TO LOGIN
@server.route('/login')
def login():
    return render_template('login.html')

# TO PROCESS LOGIN
@server.route('/login_process', methods=['POST'])
def login_process():
    query = "SELECT * FROM users WHERE users.email = :email LIMIT 1"
    querySet = mysql.query_db(query, {'email': request.form['email']})
    print querySet
    if loginValid(querySet, request.form['password']):
        session['id'] = querySet[0]['id']
        session['first_name'] = querySet[0]['first_name']
        print querySet[0]['id']
        return redirect('/the_wall')
    return redirect('/login')

# TO CHECK LOGIN IS CORRECT
def loginValid(querySet, passwordAttempt):
    if len(querySet) != 0:
        hsh_passwordAttempt = md5.new(passwordAttempt + querySet[0]['salt']).hexdigest()
        if querySet[0]['password'] == hsh_passwordAttempt:
            return True
        else:
            flash('Invalid Password!')
    else:
        flash('Invalid Email!')
    return False


# TO REGISTER
@server.route('/register')
def register():
    return render_template('register.html')

# TO PROCESS REGISTER
@server.route('/register_process', methods=['POST'])
def register_process():
    if registerValid(request):
        salt = binascii.b2a_hex(os.urandom(15))
        hsh_pw = md5.new(request.form['password'] + salt).hexdigest()
        query = "INSERT INTO users (users.first_name, users.last_name, users.email, users.password, users.salt, users.created_at, users.updated_at) VALUES (:first_name, :last_name, :email, :password, :salt, NOW(), NOW())"
        data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'password': hsh_pw,
            'salt': salt
        }
        mysql.query_db(query, data=data)
        session['first_name'] = request.form['first_name']
        flash('Please log in here')
        return redirect('/login')
    return redirect('/register')

# TO CHECK REGISTER IS CORRECT
def registerValid(data):
    print data
    valid = True
    if len(data.form['first_name']) < 1:
        flash('First name was not entered!')
        valid = False
    if len(data.form['last_name']) < 1:
        flash('Last name was not entered!')
        valid = False
    if len(data.form['email']) < 1:
        flash('Email was not entered!')
        valid = False
    elif not EMAIL_REGEX.match(data.form['email']):
        flash('Email entered was invalid!')
        valid = False
    query = "SELECT * FROM users WHERE users.email = :email"
    querySet = mysql.query_db(query, {'email': data.form['email']})
    if len(querySet) > 0:
        flash('This email is already registered')
        valid = False
    if len(data.form['password']) < 1:
        flash('Password was not entered!')
        valid = False
    elif data.form['password'] != data.form['confirm_password']:
        flash('Passwords do not match!')
        valid = False
    return valid

# TO WALL
@server.route('/the_wall')
def the_wall():
    query = "SELECT messages.id AS message_id, messages.message, messages.created_at, messages.updated_at, messages.users_id, users.first_name, users.last_name, users.email, comments.comment, comments.users_id AS comment_from_user_id, comments.updated_at AS comment_updated_at FROM users JOIN messages ON messages.users_id = users.id LEFT JOIN comments ON comments.messages_id = messages.id"

    get_messages_query = "SELECT messages.id AS message_id, messages.users_id, messages.message, messages.updated_at, users.first_name, users.last_name FROM messages JOIN users ON messages.users_id = users.id ORDER BY message_id DESC"

    get_comments_query = "SELECT comments.messages_id AS comments_message_id, comments.id AS comments_id, comments.comment, comments.updated_at, users.id AS users_id, users.first_name, users.last_name FROM comments JOIN users ON users.id = comments.users_id ORDER BY comments_message_id DESC"

    get_messages = mysql.query_db(get_messages_query)
    get_comments = mysql.query_db(get_comments_query)

    bigObj = {}
    for mRow in get_messages:
        bigObj[mRow['message_id']] = {
            'id' : mRow['message_id'],
            'comments': []
            }
        bigObj[mRow['message_id']]['first_name'] = mRow['first_name']
        bigObj[mRow['message_id']]['last_name'] = mRow['last_name']
        bigObj[mRow['message_id']]['message'] = mRow['message']
        bigObj[mRow['message_id']]['updated_at'] = mRow['updated_at']
        for cRow in get_comments:
            if bigObj[mRow['message_id']]['id'] == cRow['comments_message_id']:
                bigObj[mRow['message_id']]['comments'].append({
                    'comment': cRow['comment'],
                    'updated_at': cRow['updated_at'],
                    'first_name': cRow['first_name'],
                    'last_name': cRow['last_name'],
                    'message_id': cRow['comments_message_id']
                })

        for i in bigObj:
            if bigObj[i]['comments']:
                print bigObj[i]['comments'][0]['message_id']
#<input type="hidden" name="message_id" value="{{posts_[i]['comments'][0]['message_id']}}">
    return render_template('the_wall.html', name=session['first_name'], posts_=bigObj)

# LOGS OFF USER
@server.route('/logoff')
def logoff():
    session.pop('id', None)
    return redirect('/')

# TO PROCESS A POST
@server.route('/process_post_post', methods=['POST'])
def process_post_post():
    query = "INSERT INTO messages (messages.message, messages.created_at, messages.updated_at, messages.users_id) VALUES (:message, NOW(), NOW(), :user_id)"
    data = {
        'message': request.form['post'],
        'user_id': session['id']
    }
    mysql.query_db(query, data=data)
    return redirect('/')

# TO PROCESS A COMMENT
@server.route('/process_post_comment', methods=['POST'])
def process_post_comment():
    # print request.form['poster_id']
    query = "INSERT INTO comments (comments.comment, comments.created_at, comments.updated_at, comments.messages_id, comments.users_id) VALUES (:comment, NOW(), NOW(), :messages_id, :users_id)"

    print request.form['comment_text']
    data = {
        "comment": request.form['comment_text'],
        "messages_id": request.form['message_id'],
        "users_id": session['id']

    }
    mysql.query_db(query, data=data)
    return redirect('/')
server.run(debug=True)