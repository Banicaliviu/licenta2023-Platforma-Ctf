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
    rollout_release,
    apply_release,
    delete_release,
    uninstall_release,
    get_jctf_id,
    verify_image,
)
from ctfplatform.main_actions import init, update_profile, new_group
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
    exercises = get_jctf_list()
    return render_template(
        "jeopardy.html", role=session["role"], jeopardy_exercises=exercises
    )


@main_bp.route("/jeopardy/<int:id>/play", methods=["GET", "POST"])
def play_jeopardy(id):
    exercise = []
    exercise = get_jctf_id(id=id)

    if request.method == "POST":
        flag = request.form["flag"]
        append_new_line("logs.txt", "Flag submited is {}".format(flag))
        if flag == exercise["flag"]:
            flash("Flag is correct", "success")
            append_new_line("logs.txt", "Updating profile...")
            update_userhistory(exercise["id"], session["username"])
        else:
            flash("Flag is incorrect", "error")
        return render_template(
            "play_jeopardy.html",
            jeopardyName=exercise["name"],
            jeopardyDescription=exercise["description"],
            jeopardyStatus=exercise["status"],
        )
    return render_template(
        "play_jeopardy.html",
        jeopardyName=exercise["name"],
        jeopardyDescription=exercise["description"],
        jeopardyStatus=exercise["status"],
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
        # To do:
        # install the chart too
        # insert the neccessaries to db
        # this way you can update the button
        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            uploaded_file.save(file_path)

            create_JeopardyExercise_helmchart(ctf_name, flag, score, file_path)
            flash("CTF created successfully")
        else:
            flash("Invalid file. Please provide a valid .tgz Helm package.", "error")

        return render_template("add_jeopardy_via_helm_chart.html")

    return render_template("add_jeopardy_via_helm_chart.html")


@main_bp.route("/releases", methods=["GET", "POST"])
def releases():
    if request.method == "POST":
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
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


####Utility
@main_bp.route("/get_users", methods=["GET"])
def get_users():
    users = [
        {"email": "user1@example.com", "username": "user1", "group": "Group A"},
        {"email": "user2@example.com", "username": "user2", "group": "Group B"},
        {"email": "user3@example.com", "username": "user3", "group": "Group A"},
        {"email": "user4@example.com", "username": "user4", "group": "Group C"},
    ]

    return jsonify(users)


@main_bp.route("/get_groups", methods=["GET"])
def get_groups():
    groups = [
        {"name": "group1", "members": "1"},
        {"name": "C114A", "members": "2"},
        {"name": "ueFrog", "members": "3"},
    ]

    return jsonify(groups)
