import re
from ctfplatform import app
from flask import Blueprint, flash, redirect, render_template, session, url_for, request
from ctfplatform.utils import append_new_line
from ctfplatform.JCTF_actions import get_jctf_list, init, get_jctf_id, update_userhistory, update_jctfs_status
from ctfplatform.main_actions  import update_profile

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/profile')
def profile():
    username = session['username']
    profile = update_profile(username)
    append_new_line("logs.txt", "Profile up to date!")
    return render_template('profile.html', username=username, score=profile['score'], ctfs=profile['jctfs'])

@main_bp.route('/jeopardy')
def jeopardy():
    init()
    exercises = []
    append_new_line("logs.txt", "Updating jeopardy ctfs container status...")
    update_jctfs_status()
    append_new_line("logs.txt", "Jeopardy ctfs container status is up to date!Rendering exercises...")
    exercises = get_jctf_list()
    return render_template('jeopardy.html', exercises=exercises, role=session['role'])

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

#######Only admins can access
@main_bp.route('/add_jeopardy_exercise', methods=['GET', 'POST'])
def add_jeopardy_exercise():
    return render_template('add_jeopardy.html')