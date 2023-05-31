import re
import os
from ctfplatform import app
from flask import Blueprint, flash, redirect, render_template, session, url_for, request, jsonify, send_file
from ctfplatform.utils import append_new_line
from ctfplatform.JCTF_actions import get_jctf_id, update_userhistory, update_jctfs_status, create_JeopardyExercise_helmchart, get_helm_releases, download_release, authorize_users, rollout_release, apply_release, delete_release
from ctfplatform.main_actions  import init,update_profile
from werkzeug.utils import secure_filename



DOWNLOAD_FOLDER = '/flaskapp/downloads'
main_bp = Blueprint('main', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'tgz'}

@main_bp.route('/')
def index():
    init()
    return render_template('index.html')

@main_bp.route('/profile')
def profile():
    username = session['username']
    profile = update_profile(username)
    append_new_line("logs.txt", "Profile up to date!")
    return render_template('profile.html', username=username, score=profile['score'], ctfs=profile['jctfs'])

@main_bp.route('/jeopardy')
def jeopardy():
    return render_template('jeopardy.html', role=session['role'])

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
    if request.method == 'POST':
        ctf_name = request.form.get('ctf-name')
        uploaded_file = request.files['helm-package']
        flag = request.form.get('flag')

        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            uploaded_file.save(file_path)

            create_JeopardyExercise_helmchart(ctf_name, flag, file_path)
            flash("Helm chart installed succesfully. You can see the release in Releases page")
        else:
            flash("Invalid file. Please provide a valid .tgz Helm package.")

        return render_template('add_jeopardy.html')

    return render_template('add_jeopardy.html')

#Everything works fine, its just you cannot list available charts
#Add that helm chart museum and list that
@main_bp.route('/releases', methods=['GET', 'POST'])
def releases():
    if request.method == 'POST':
        release_name = request.form.get('release-name')
        release_version = request.form.get('release-version')
        action = request.form.get('action')
        if release_name:
            if action == 'authorize_users':
                result = authorize_users(release_name)
                if result:
                    flash(f"Users authorized for release '{release_name}'.", "success")
                else:
                    flash(f"Failed to authorize users for release '{release_name}'.", "error")
            elif action == 'delete':
                result = delete_release(release_name, release_version)
                if result:
                    flash(f"Release '{release_name}' has been deleted.", "success")
                else:
                    flash(f"Failed to delete release '{release_name}'.", "error")
            elif action == 'rollout':
                result = rollout_release(release_name)
                if result:
                    flash(f"Rollout initiated for release '{release_name}'.", "success")
                else:
                    flash(f"Failed to initiate rollout for release '{release_name}'.", "error")
            elif action == 'download':
                redirect(url_for('main.download', release_name=release_name, release_version=release_version))
                if result:
                    flash(f"Release '{release_name}' downloaded successfully.", "success")
                else:
                    flash(f"Failed to download release '{release_name}'.", "error")
            elif action == 'apply_release':
                result = apply_release(release_name, release_version)
                if result:
                    flash(f"Release '{release_name}' applied successfully.", "success")
                else:
                    flash(f"Failed to apply release '{release_name}'.", "error")
            else:
                flash("Invalid action selected.", "error")
        else:
            flash("No release selected.", "error")
        return redirect(url_for('main.releases'))
    else:
        releases = get_helm_releases()
        return render_template('releases.html', releases=releases)
    
@main_bp.route('/download', methods=['POST'])
def download():
    release_name = request.form.get('release-name')
    folder_path = request.form.get('folder-path')

    if release_name and folder_path:
        tgz_file = download_release(release_name)
        if tgz_file:
            destination_path = os.path.join(DOWNLOAD_FOLDER, folder_path, f"{release_name}.tgz")
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            os.rename(tgz_file, destination_path)
            flash(f"Release '{release_name}' downloaded successfully.", "success")
        else:
            flash(f"Failed to download release '{release_name}'.", "error")
    else:
        flash("Please select a release and specify a folder path.", "error")
    
    return redirect(url_for('main.releases'))
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS