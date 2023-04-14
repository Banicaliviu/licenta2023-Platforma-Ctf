import re
from ctfplatform import app
from flask import Blueprint, flash, redirect, render_template, session, url_for

from ctfplatform.utils import append_new_line, get_db_connection, get_kube_SAtoken
from ctfplatform.kubernetes_interactions import *
main_bp = Blueprint('main', __name__)

kube_interaction = kubernetes_interaction(get_kube_SAtoken())

@main_bp.route('/')
def index():
    try:
        
        kube_interaction.kube_list_pods()
        conn = get_db_connection()
        append_new_line("logs.txt", "connection to Postgresql successfully established !")
        cur = conn.cursor()
        append_new_line("logs.txt", "cursor successfully created !")
        
        #cur.execute('DROP TABLE IF EXISTS UserTable;')

        cur.execute('CREATE TABLE usertable ('
                    'id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,'
                    'email VARCHAR(150) NOT NULL,'
                    'password VARCHAR(150) NOT NULL,'
                    'username VARCHAR(150) NOT NULL,'
                    'role VARCHAR(150),'
                    'date_added DATE DEFAULT CURRENT_TIMESTAMP'
                ');'
        )        
        
        conn.commit()
        append_new_line("logs.txt", "UserTable table successfully created !")
        cur.close()
        conn.close()
        
    except(Exception) as e:
        append_new_line("logs.txt", "Error : {}".format(e))
    finally:
        return render_template('index.html')

@main_bp.route('/profile')
def profile():
    if session['loggedin']:
        username = session['username']
        append_new_line("logs.txt", "User {} accessed profile page !".format(username))
        return render_template('profile.html', name=username)
    else:
        flash("Please login to access your profile !")
        return redirect(url_for('auth.login'))