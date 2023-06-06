import re
import os
from ctfplatform import app
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    session,
    url_for,
    request,
    jsonify,
    send_file,
)
from ctfplatform.utils import append_new_line, allowed_file
from ctfplatform.JCTF_actions import (
    create_JeopardyExercise_helmchart,
    get_helm_releases,
    update_userhistory,
    update_jctfs_status, 
    authorize_users,
    rollout_release,
    apply_release,
    delete_release,
    uninstall_release,
    get_jctf_id
)
from ctfplatform.main_actions import init, update_profile
from werkzeug.utils import secure_filename

main_bp = Blueprint("main", __name__)

UPLOAD_FOLDER = "uploads"


@main_bp.route("/")
def index():
    init()
    return render_template("index.html")


@main_bp.route("/profile")
def profile():
    username = session["username"]
    profile = update_profile(username)
    append_new_line("logs.txt", "Profile up to date!")
    return render_template(
        "profile.html", username=username, score=profile["score"], ctfs=profile["jctfs"]
    )


@main_bp.route("/jeopardy")
def jeopardy():
    return render_template("jeopardy.html", role=session["role"])


@main_bp.route("/jeopardy/<int:id>/play", methods=["GET", "POST"])
def play_jeopardy(id):
    exercise = []
    exercise = get_jctf_id(id=id)

    if request.method == "POST":
        flag = request.form["flag"]
        append_new_line("logs.txt", "Flag submited is {}".format(flag))
        if flag == exercise["flag"]:
            flash("Flag is correct")
            append_new_line("logs.txt", "Updating profile...")
            update_userhistory(exercise["id"], session["username"])
        else:
            flash("Flag is incorrect")
        return render_template(
            "play_jeopardy.html",
            jeopardyTitle=exercise["title"],
            jeopardyDescription=exercise["description"],
            jeopardyDifficulty=exercise["difficulty"],
        )
    return render_template(
        "play_jeopardy.html",
        jeopardyTitle=exercise["title"],
        jeopardyDescription=exercise["description"],
        jeopardyDifficulty=exercise["difficulty"],
    )


#######Only admins can access
@main_bp.route("/add_jeopardy_exercise", methods=["GET", "POST"])
def add_jeopardy_exercise():
    if request.method == "POST":
        ctf_name = request.form.get("ctf-name")
        uploaded_file = request.files["helm-package"]
        flag = request.form.get("flag")
        #To do: 
        #install the chart too 
        #insert the neccessaries to db 
        #this way you can update the button
        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            uploaded_file.save(file_path)

            create_JeopardyExercise_helmchart(ctf_name, flag, file_path)
            flash(
                "Helm chart pushed successfully."
            )
        else:
            flash("Invalid file. Please provide a valid .tgz Helm package.")

        return render_template("add_jeopardy.html")

    return render_template("add_jeopardy.html")


@main_bp.route("/releases", methods=["GET", "POST"])
def releases():
    if request.method == "POST":
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = request.get_json()
            release_name = data.get("release-name")
            release_version = data.get("release-version")
            action = data.get("action")
        else:
            release_name = request.form.get("release-name")
            release_version = request.form.get("release-version")
            action = request.form.get("action")

        if release_name:
            if action == "authorize_users":
                return redirect(url_for("main.authorize_users"))

            elif action == "delete_release":
                form_release_name = request.form.get("release-name")
                form_release_version = request.form.get("release-version")
                result = delete_release(form_release_name, form_release_version)
                if result == 0:
                    flash(f"Release '{release_name}' has been deleted.", "success")
                    releases = get_helm_releases()
                    return render_template("releases.html", releases=releases)
                else:
                    flash(f"Failed to delete release '{release_name}'.", "error")

            elif action == "rollout":
                result = rollout_release(release_name)
                if result:
                    flash(f"Rollout initiated for release '{release_name}'.", "success")
                else:
                    flash(
                        f"Failed to initiate rollout for release '{release_name}'.",
                        "error",
                    )
            
            elif action == "apply_release":
                result = apply_release(release_name, release_version)
                if result == 0:
                    flash(
                        f"Release '{release_name}' installed successfully.", "success"
                    )
                    return jsonify(success=True)
                else:
                    flash(f"Failed to install release '{release_name}'.", "error")

                    return jsonify(success=False)

            elif action == "uninstall_release":
                result = uninstall_release(release_name, release_version)
                if result:
                    flash(
                        f"Release '{release_name}' uninstalled successfully.", "success"
                    )

                    return jsonify(success=True)
                else:
                    flash(f"Failed to uninstall release '{release_name}'.", "error")

                    return jsonify(success=False)

            else:
                flash("Invalid action selected.", "error")

        else:
            flash("No release selected.", "error")

        return redirect(url_for("main.releases"))

    else:
        releases = get_helm_releases()
        return render_template("releases.html", releases=releases)


@main_bp.route("/authorize_users", methods=["GET", "POST"])
def authorize_users():
    if request.method == "POST":
        # Perform authorization logic here
        flash("Users authorized.", "success")
        return redirect(url_for("main.authorize_users"))

    # Fetch users from the database or any other data source
    users = [
        {"email": "user1@example.com", "username": "user1", "group": "Group A"},
        {"email": "user2@example.com", "username": "user2", "group": "Group B"},
        {"email": "user3@example.com", "username": "user3", "group": "Group A"},
        {"email": "user4@example.com", "username": "user4", "group": "Group C"},
    ]

    return render_template("authorize_users.html", users=users)
