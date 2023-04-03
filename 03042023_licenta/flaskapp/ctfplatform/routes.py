import re
from ctfplatform import app
from flask import flash, redirect, render_template, request, url_for
import os
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

#TO DO 3
#import kubernetes

def append_new_line(file_name, text_to_append):
    with open(file_name, "a+") as file_object:
        file_object.seek(0)
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        file_object.write(text_to_append)

def get_db_connection():
    conn = psycopg2.connect(
        host="172.17.0.8",
        port=5432,
        database=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"])

    return conn

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        append_new_line("logs.txt", "connection to Postgresql successfully established !")
        cur = conn.cursor()
        append_new_line("logs.txt", "cursor successfully created !")
        cur.execute('CREATE TABLE UserTable (id serial PRIMARY KEY,'
                                        'email varchar (150) NOT NULL,'
                                        'password varchar (150) NOT NULL,'
                                        'username varchar (150) NOT NULL,'
                                        'role varchar (150),'
                                        'date_added date DEFAULT CURRENT_TIMESTAMP);'
                                        )

        conn.commit()
        append_new_line("logs.txt", "UserTable table successfully created !")
        cur.close()
        conn.close()
        
    except(Exception):
        #print("Error while connecting to PostgreSQL", error)
        append_new_line("logs.txt", "Error while connecting to PostgreSQL")
    finally:
        return render_template('index.html')

    # cur.execute('SELECT * FROM ctfexercise;')
    # ctfexercises = cur.fetchall()
    
@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        role = 'admin'

        _hashed_password = generate_password_hash(password)

        try:
            con = get_db_connection()
            append_new_line("logs.txt", "connection to Postgresql successfully established !")
            cur = con.cursor()
            append_new_line("logs.txt", "cursor successfully created !")
            ok = 0
            # cur.execute('SELECT * FROM users where email=%s;', (email,))
            # users = cur.fetchone()
            # print(users)
            
            #TO DO :
            # Flash-urile(probabil e problema la html)
            # Redirect pe pagina login daca inreg a avut loc cu success
            

            cur.execute('SELECT * from UserTable WHERE username = %s', (username,))
            append_new_line("logs.txt", "select successfully executed !")
            account = cur.fetchone()
            if account:
                append_new_line("logs.txt", "user {} is already registered.".format(username))
                flash('Account already exists!')
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                append_new_line("logs.txt", "Email {} is invalid.".format(email))
                flash('Invalid email address!')
            elif not re.match(r'[A-Za-z0-9]+', username):
                append_new_line("logs.txt", "Username {} is invalid.".format(username))
                flash('Username must contain only characters and numbers!')
            elif not username or not password or not email:
                append_new_line("logs.txt", "Registration failed.Not all fields were completed")
                flash('All fields are mandatory!')
            else:
                cur.execute('INSERT INTO UserTable (email, password, username, role)'
                'VALUES (%s, %s, %s, %s)',
                (email,
                _hashed_password,
                username,
                role)
                )
                con.commit()
                append_new_line("logs.txt", "user {} with {} rights was successfully registered".format(username, role))
                flash('You have successfully registered !')
                ok = 1
        except(Exception, psycopg2.Error) as error:
            #print("Error while verifying uniqueness of user", error)
            append_new_line("logs.txt", "Error while registering user")  
        finally:
            if con:
                cur.close()
                con.close()
                #print("PostgreSQL connection is closed")
                append_new_line("logs.txt", "PostgreSQL connection is closed")
            if ok == 1:
                return redirect(url_for('login'))
    elif request.method == 'POST':
        flash('Please fill out the form!')
    return render_template('register.html')
    
            
    
@app.route('/login', methods = ['GET', 'POST'])
def login():

    #TO DO 2

    # if request.method == 'POST' and 'password' in request.form and 'email' in request.form:
    #     email = request.form['email']
    #     password = request.form['password']

    #     print(email)
    #     print(password)
    append_new_line("logs.txt", "accessed login page")
    return render_template('login.html')