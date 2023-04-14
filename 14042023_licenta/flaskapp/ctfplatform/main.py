import re
from ctfplatform import app
from flask import Blueprint, flash, redirect, render_template, session, url_for

from ctfplatform.utils import append_new_line
from ctfplatform.kubernetes_interactions import get_db_connection

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    try:
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

@main_bp.route('/jeopardy')
def jeopardy():
    exercises = [
        {
            'id': 1,
            'title': 'My first ctf',
            'description': 'This is a ctf exercise model box. It has been made for management of ctf exercises.',
            'difficulty': '1/5'
        },
        {
            'id': 2,
            'title': 'My second ctf',
            'description': 'This is a second ctf exercise model box.',
            'difficulty': '2/5'
        },
        {
            'id': 3,
            'title': 'My third ctf',
            'description': 'This is a third ctf exercise model box.',
            'difficulty': '3/5'
        }
    ]
    return render_template('jeopardy.html', exercises=exercises)

@main_bp.route('/jeopardy/<int:id>/play')
def play_jeopardy(id):
    # Retrieve the exercise with the given ID from the database
    # exercise = Exercise.query.get_or_404(id)

    # Render the play exercise page with the exercise data
    # return render_template('play_jeopardy.html', exercise=exercise)
    return render_template('play_jeopardy.html')