import re
from ctfplatform import app
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from ctfplatform.utils import append_new_line, get_db_connection

auth_bp = Blueprint('auth', __name__)
    
@auth_bp.route('/register', methods = ['GET', 'POST'])
def register():
    append_new_line("logs.txt", "Register Start")
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        role = 'admin'

        _hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            append_new_line("logs.txt", "connection to Postgresql successfully established !")
            cur = conn.cursor()
            append_new_line("logs.txt", "cursor successfully created !")
         
            cur.execute('SELECT * from usertable WHERE email = %s', (email,))
            account_chkbyEmail = cur.fetchone()
            
            cur.execute('SELECT * from usertable WHERE username = %s', (username,))
            account_chkbyUsername = cur.fetchone()

            if account_chkbyEmail:
                append_new_line("logs.txt", "Email {} is used by other account.".format(username, email))
                flash('Account using this email already exists !')
            elif account_chkbyUsername:
                append_new_line("logs.txt", "Username {} is used by other account.".format(username, email))
                flash('Account with this username already exists !')
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                append_new_line("logs.txt", "Invalid email !")
                flash('Invalid email address !')
            elif not re.match(r'[A-Za-z0-9]+', username):
                append_new_line("logs.txt", "Invalid username !")
                flash('Username must contain only characters and numbers !')
            elif not username or not password or not email:
                append_new_line("logs.txt", "Not all fields were completed")
                flash('Please fill out the form !')
            else:
                cur.execute('INSERT INTO usertable (email, password, username, role)'
                'VALUES (%s, %s, %s, %s)',
                (email,
                _hashed_password,
                username,
                role)
                )
                conn.commit()
                append_new_line("logs.txt", "User {} was successfully registered !".format(username))
                flash('You have successfully registered !')
                return redirect(url_for('auth.login'))
        except Exception as e:
            append_new_line("logs.txt", "Error : {}".format(e)) 
    elif request.method == 'POST':
        flash('Please fill out the form!')
    
    try:
        if conn:
            cur.close()
            conn.close()
            append_new_line("logs.txt", "PostgreSQL connection is closed")
    except Exception as e:
        append_new_line("logs.txt", "Error : {}".format(e))
    append_new_line("logs.txt", "Register End\n")
    return render_template('register.html')
    
@auth_bp.route('/login', methods = ['GET', 'POST'])
def login():
    append_new_line("logs.txt", "Login Start")
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        try:
            conn = get_db_connection()
            append_new_line("logs.txt", "connection to Postgresql successfully established !")
            cur = conn.cursor()
            append_new_line("logs.txt", "cursor successfully created !")

            cur.execute('SELECT * from usertable WHERE email = %s', (email,))
            account = cur.fetchone()
            
            if account:
                passwd_hs = account[2]
                if check_password_hash(passwd_hs, password):
                    #account['id'] intoarce string, cred ca pe aici e problema
                    #Error : tuple indices must be integers or slices, not str

                    session['loggedin'] = True
                    session['id'] = int(account[0])
                    session['username'] = account[3] 
                    
                    append_new_line("logs.txt", "User {} was successfully logged in !".format(session['username']))
                    append_new_line("logs.txt", "Session information: {}".format(session))
                    append_new_line("logs.txt", "Login End\n")
                    return redirect(url_for('main.index'))
                else:
                    append_new_line("logs.txt", "Invalid password !")
                    flash("Invalid email/password !")
            else:
                append_new_line("logs.txt", "Invalid email !") 
                flash("Invalid email/password !")
        except Exception as e:
            append_new_line("logs.txt", "Error : {}".format(e))
       
    append_new_line("logs.txt", "Login End\n")
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    username = session['username']
    session.pop('username', None)
    session['loggedin'] = False
    append_new_line("logs.txt", "User {} disconnected !\n".format(username))
    flash('You have been logged out')
    return redirect(url_for('main.index'))