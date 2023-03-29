from ctfplatform import app
from flask import render_template, request
import os
import psycopg2


def get_db_connection():
    conn = psycopg2.connect(
        host="172.17.0.5",
        port=5432,
        database=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"])

    return conn

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS users (id serial PRIMARY KEY,'
                                        'email varchar (150) NOT NULL,'
                                        'password varchar (150) NOT NULL,'
                                        'username varchar (150) NOT NULL,'
                                        'role varchar (150) DEFAULT "normal",'
                                        'date_added date DEFAULT CURRENT_TIMESTAMP);'
                                        )

        conn.commit()
        print("Users table created succesfully")
    except(Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)

    # cur.execute('SELECT * FROM ctfexercise;')
    # ctfexercises = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    
    if request.method == 'GET':
        return render_template('register.html')
    
    if request.method == 'POST' and 'password' in request.form and 'email' in request.form and 'username' in request.form:
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        try:
            con = get_db_connection()
            cur = con.cursor()

            # cur.execute('SELECT * FROM users where email=%s;', (email,))
            # users = cur.fetchone()
            # print(users)

            cur.execute('INSERT INTO users (email, password, username, role)'
                'VALUES (%s, %s, %s, %s)',
                (email,
                password,
                username,
                'admin')
                )
            con.commit()

        except(Exception, psycopg2.Error) as error:
            print("Error while verifying uniqueness of user", error)
        finally:
            if con:
                cur.close()
                con.close()
                print("PostgreSQL connection is closed")
            return render_template('register.html')
            
    
@app.route('/login', methods = ['GET', 'POST'])
def login():
    # if request.method == 'POST' and 'password' in request.form and 'email' in request.form:
    #     email = request.form['email']
    #     password = request.form['password']

    #     print(email)
    #     print(password)
    return render_template('login.html')