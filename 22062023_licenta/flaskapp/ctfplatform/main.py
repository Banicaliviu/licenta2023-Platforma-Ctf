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
    create_JeopardyExercise_dockerfile,
    get_helm_releases,
    update_userhistory,
    get_jctf_list,
    update_jctfs_status,
    authorize_users,
    apply_release,
    delete_release,
    uninstall_release,
    get_jctf_id,
    verify_image,
    mark_chart,
    create_env,
    update_scoreboard,
    get_scoreboard,
)
from ctfplatform.main_actions import init, update_profile, new_group, set_permission_user, get_users
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

@main_bp.route("/scoreboard")
def scoreboard():
    scoreboardDict = get_scoreboard()
    return render_template(
        "scoreboard.html", scoreboard=scoreboardDict
    )

@main_bp.route("/jeopardy", methods=["GET", "POST"])
def jeopardy():
    if request.method == "POST":
        action = request.form["action"]
        if action == "start_attempt":
            exercise_id = request.form["exercise-id"]
            exercises = get_jctf_list(session["role"], session["username"])
            res = create_env(session["username"], exercise_id)
            if res == True: 
                return redirect(url_for("main.play_jeopardy", id=exercise_id))
            else:
                flash("Cannot create safe environment", "error")
                exercises = get_jctf_list(session["role"], session["username"])
                return render_template(
                    "jeopardy.html", role=session["role"], jeopardy_exercises=exercises
                )

    exercises = get_jctf_list(session["role"], session["username"])
    
    
    return render_template(
        "jeopardy.html", role=session["role"], jeopardy_exercises=exercises
    )


@main_bp.route("/jeopardy/<int:id>/play", methods=["GET", "POST"])
def play_jeopardy(id):
    exercise = []
    exerciseDict = get_jctf_id(session["username"], id)
    exercise = exerciseDict[0]

    if request.method == "POST":
        flag = request.form["flag"]
        append_new_line("logs.txt", "Flag submited is {}".format(flag))
        if flag == exercise["flag"]:
            flash("Flag is correct", "success")
            append_new_line("logs.txt", "Updating scoreboard...")
            res = update_scoreboard(exercise["name"], exercise["score"], session["username"])
            if res == 1:
                append_new_line("logs.txt", "Scoreboard updated")
        else:
            flash("Flag is incorrect", "error")
        return render_template(
            "play_jeopardy.html",
            jeopardyName=exercise["name"],
            jeopardyDescription=exercise["description"],
            jeopardyStatus=exercise["status"],
            jeopardyScore=exercise["score"],
            jeopardyURL=exercise["fullUrl"],
        )
    return render_template(
        "play_jeopardy.html",
        jeopardyName=exercise["name"],
        jeopardyDescription=exercise["description"],
        jeopardyStatus=exercise["status"],
        jeopardyScore=exercise["score"],
        jeopardyURL=exercise["fullUrl"],
    )


#######Only admins can access
@main_bp.route("/add_jeopardy_exercise_dockerfile", methods=["GET", "POST"])
def add_jeopardy_exercise_dockerfile():
    if request.method == "POST":
        username = session["username"]
        ctf_name = request.form.get("ctf-name")
        flag = request.form.get("flag")
        score = request.form.get("score")
        dockerfile = request.files["dockerfile"]
        imageName_tag = request.form.get("imagename")
        digest = request.form.get("digest")

        if dockerfile.filename == "Dockerfile":
            filename = secure_filename(dockerfile.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            dockerfile.save(file_path)
        res = verify_image(imageName_tag, digest)
        if res == True:
            res = create_JeopardyExercise_dockerfile(
                ctf_name, flag, score, file_path, imageName_tag, digest, username
            )

        if res == True:
            flash("Image pushed successfully.", "success")
        else:
            flash("Image push failed.", "error")
        return render_template("add_jeopardy_via_dockerfile.html")
    return render_template("add_jeopardy_via_dockerfile.html")


@main_bp.route("/add_jeopardy_exercise_helm_chart", methods=["GET", "POST"])
def add_jeopardy_exercise_helm_chart():
    if request.method == "POST":
        ctf_name = request.form.get("ctf-name")
        uploaded_file = request.files["helm-package"]
        flag = request.form.get("flag")
        score = request.form.get("score")
        
        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            uploaded_file.save(file_path)

            create_JeopardyExercise_helmchart(ctf_name, flag, score, file_path)
            flash("CTF created successfully")
        else:
            flash("Invalid file. Please provide a valid .tgz or tar.gz Helm package.", "error")

        return render_template("add_jeopardy_via_helm_chart.html")

    return render_template("add_jeopardy_via_helm_chart.html")


@main_bp.route("/releases", methods=["GET", "POST"])
def releases():
    if request.method == "POST":
        release_name = request.form.get("release-name")
        release_version = request.form.get("release-version")
        action = request.form.get("action")

        if release_name:
            if action == "authorize_users":
                return redirect(url_for("main.authorize_users", release_name=release_name))
            
            if action == "authorize_group":
                return redirect(url_for("main.authorize_group", release_name))
            
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

            elif action == "apply_release":
                result = apply_release(release_name, release_version)
                if result == 0:
                    flash(
                        f"Release '{release_name}' installed successfully.", "success"
                    )
                    mark_chart(release_name, "True")
                    releases = get_helm_releases()
                    return render_template("releases.html", releases=releases)
                else:
                    flash(f"Failed to install release '{release_name}'.", "error")
                    releases = get_helm_releases()
                    return render_template("releases.html", releases=releases)

            elif action == "uninstall_release":
                result = uninstall_release(release_name, release_version)
                if result == True:
                    flash(
                        f"Release '{release_name}' uninstalled successfully.", "success"
                    )
                    mark_chart(release_name, "False")
                    releases = get_helm_releases()
                    return render_template("releases.html", releases=releases)
                else:
                    flash(
                        f"Couldn't uninstall '{release_name}'", "error"
                    )
                    releases = get_helm_releases()
                    return render_template("releases.html", releases=releases)

            else:
                flash("Invalid action selected.", "error")

        else:
            flash("No release selected.", "error")

        return redirect(url_for("main.releases"))

    else:
        releases = get_helm_releases()
        return render_template("releases.html", releases=releases)


@main_bp.route("/create_group", methods=["GET", "POST"])
def create_group():
    if request.method == "POST":
        group_name = request.form.get("groupname")
        res = new_group(group_name)
        if res == "samename":
            flash("Cannot create two groups with same name", "error")
            return redirect(url_for("main.create_group"))
        if res == True:
            flash("Group created successfully.", "success")
        else:
            flash("Error while creating group", "error")
        return redirect(url_for("main.create_group"))
    return render_template("register_group.html")


@main_bp.route("/authorize_users/<release_name>", methods=["GET", "POST"])
def authorize_users(release_name):
    if request.method == "POST":
        username = request.form.get("user-username")
        action = request.form.get("action")
        append_new_line("logs.txt", f"Changing user's authorization: {username} for {release_name}")

        if action == "auth":
            res = set_permission_user(username, release_name, "True")
            users = get_users()
            if res == 1:
                flash(f"User's {username} permissions changed for {release_name}.", "success") 
            else:
                flash(f"Couldn't authorize user. Internal error.", "error") 
            if users == []:
                return render_template("authorize_users.html", users=[], release_name=release_name)
            return render_template("authorize_users.html", users=users, release_name=release_name)
        
        if action == "deauth":
            res = set_permission_user(username, release_name, "False")
            users = get_users()
            if res == 1:
                flash(f"User's {username} permissions changed for {release_name}.", "success") 
            else:
                flash(f"Couldn't authorize group. Internal error.", "error")  
            if users == []:
                return render_template("authorize_users.html", users=[], release_name=release_name)
            return render_template("authorize_users.html", users=users, release_name=release_name)
        flash(f"Couldn't change permissions: {username} - {release_name}", "error")
        return redirect(url_for("main.authorize_users", release_name=release_name))
    else:
        users = get_users()
        if users == []:
            return render_template("authorize_users.html", users=[],release_name=release_name)
        return render_template("authorize_users.html", users=users, release_name=release_name)

@main_bp.route("/authorize_group", methods=["GET", "POST"])
def authorize_group():
    if request.method == "POST":
        # Perform authorization logic here
        flash("Group authorized.", "success")
        return render_template("authorize_group.html", groups=groups)

    # Fetch users from the database or any other data source
    groups = [
        {"name": "Group A", "members": "10", "is_authorized" : "False"},
        {"name": "Group B", "members": "11", "is_authorized" : "True"},
        {"name": "Group C", "members": "12", "is_authorized" : "False"},
    ]

    return render_template("authorize_group.html", groups=groups)
