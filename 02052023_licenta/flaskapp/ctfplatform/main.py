import re
from ctfplatform import app
from flask import Blueprint, flash, redirect, render_template, session, url_for, request
from ctfplatform.utils import append_new_line
from ctfplatform.JCTF_actions import get_jctf_list, init, get_jctf_id, update_userhistory

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/profile')
def profile():
    username = session['username']
    append_new_line("logs.txt", "User {} accessed profile page !".format(username))
    
    #profile = update_profile()
    return render_template('profile.html', username=username, score = '0', ctfs = None)
@main_bp.route('/jeopardy')
def jeopardy():
    init()
    exercises = []
    exercises = get_jctf_list()
    return render_template('jeopardy.html', exercises=exercises)

@main_bp.route('/jeopardy/<int:id>/play', methods=['GET', 'POST'])
def play_jeopardy(id):
    exercise = []
    exercise = get_jctf_id(id=id)
    
    if request.method == 'POST':
        flag = request.form['flag']
        append_new_line("logs.txt", "Flag submited is {}".format(flag))
        if(flag == exercise['flag']):
            flash("Flag is correct")
            append_new_line("logs.txt", "Updating profile...")
            update_userhistory(exercise['id'], session['username'])
        else:
            flash("Flag is incorrect")
        return render_template('play_jeopardy.html', 
                        jeopardyTitle=exercise['title'], 
                        jeopardyDescription=exercise['description'], 
                        jeopardyDifficulty=exercise['difficulty']
                        )
    return render_template('play_jeopardy.html', 
                        jeopardyTitle=exercise['title'], 
                        jeopardyDescription=exercise['description'], 
                        jeopardyDifficulty=exercise['difficulty']
                        )

