import re
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from ctfplatform.utils import append_new_line
from ctfplatform.kubernetes_interactions import get_db_connection
from ctfplatform.db_actions import get_userid_where_username, get_groups

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    append_new_line("logs.txt", "Register Start")
    group_list = get_groups()
    groupname_list = []
    for db_group in group_list:
        groupname_list.append(db_group["name"])
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
        and "email" in request.form
        and "role" in request.form
    ):
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        group = request.form["group"]

        _hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("SELECT * from usertable WHERE email = %s", (email,))
            account_chkbyEmail = cur.fetchone()

            cur.execute("SELECT * from usertable WHERE username = %s", (username,))
            account_chkbyUsername = cur.fetchone()

            if account_chkbyEmail:
                append_new_line(
                    "logs.txt",
                    "Email {} is used by other account.".format(username, email),
                )
                flash("Account using this email already exists !")
            elif account_chkbyUsername:
                append_new_line(
                    "logs.txt",
                    "Username {} is used by other account.".format(username, email),
                )
                flash("Account with this username already exists !")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                append_new_line("logs.txt", "Invalid email !")
                flash("Invalid email address !")
            elif not re.match(r"[A-Za-z0-9]+", username):
                append_new_line("logs.txt", "Invalid username !")
                flash("Username must contain only characters and numbers !")
            elif not username or not password or not email:
                append_new_line("logs.txt", "Not all fields were completed")
                flash("Please fill out the form !")
            else:
                cur.execute(
                    "INSERT INTO usertable (email, password, username, role)"
                    "VALUES (%s, %s, %s, %s)",
                    (email, _hashed_password, username, role),
                )
                conn.commit()
                append_new_line(
                    "logs.txt", "User {} was successfully registered !".format(username)
                )
                group_id = None
                if group and group != "None":
                    for db_group in group_list:
                        if group == db_group["name"]:
                            group_id = db_group["id"]
                            break
                    user_id = get_userid_where_username(username)
                    append_new_line(
                        "logs.txt",
                        "User {} is being added to group {}--{} !".format(
                            username, group_id, group
                        ),
                    )
                    if group_id != 0 and user_id != 0:
                        cur.execute(
                            "INSERT INTO usertogrouptable (id_user, id_group)"
                            "VALUES (%s, %s)",
                            (user_id, group_id),
                        )
                        conn.commit()
                    append_new_line(
                        "logs.txt",
                        "User {} successfully added to group {} !".format(
                            username, group
                        ),
                    )
                else:
                    append_new_line("logs.txt", "No group seleted!")
                return redirect(url_for("auth.register"))
        except Exception as e:
            append_new_line("logs.txt", "Error : {}".format(e))
    elif request.method == "POST":
        flash("Please fill out the form!")

    try:
        if conn:
            cur.close()
            conn.close()
            append_new_line("logs.txt", "PostgreSQL connection is closed")
    except Exception as e:
        append_new_line("logs.txt", "Error : {}".format(e))
    append_new_line("logs.txt", "Register End\n")
    return render_template("register.html", groups=groupname_list)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    append_new_line("logs.txt", "Login Start")
    if (
        request.method == "POST"
        and "email" in request.form
        and "password" in request.form
    ):
        email = request.form["email"]
        password = request.form["password"]

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT * from usertable WHERE email = %s", (email,))
            account = cur.fetchone()

            if account:
                passwd_hs = account[2]
                # Adming user with admin password inserted to db. Temporar workaround. Password has to be hashed inside db.
                if check_password_hash(passwd_hs, password) or password == account[2]:
                    session["loggedin"] = True
                    session["id"] = int(account[0])
                    session["username"] = account[3]
                    session["role"] = account[4]

                    append_new_line(
                        "logs.txt",
                        "User {} was successfully logged in !".format(
                            session["username"]
                        ),
                    )
                    append_new_line(
                        "logs.txt", "Session information: {}".format(session)
                    )
                    append_new_line("logs.txt", "Login End\n")
                    return redirect(url_for("main.index"))
                else:
                    append_new_line("logs.txt", "Invalid password !")
                    flash("Invalid email/password !")
            else:
                append_new_line("logs.txt", "Invalid email !")
                flash("Invalid email/password !")
        except Exception as e:
            append_new_line("logs.txt", "Error : {}".format(e))

    append_new_line("logs.txt", "Login End\n")
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    username = session["username"]
    session.pop("username", None)
    session["loggedin"] = False
    append_new_line("logs.txt", "User {} disconnected !\n".format(username))
    flash("You have been logged out")
    return redirect(url_for("main.index"))