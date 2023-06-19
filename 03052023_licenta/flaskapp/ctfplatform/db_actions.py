from ctfplatform.kubernetes_interactions import kube_interaction_inst, get_db_connection
from ctfplatform.utils import append_new_line, format_timestamp


###########################################Inserts
###############GROUPS
def insert_group(groupname):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO grouptable (name) VALUES (%s)",
            (groupname,),
        )
        conn.commit()

        return True
    except Exception as e:
        append_new_line(
                        "logs.txt",
                        "Cannot insert group to database: {}".format(groupname),
                    )        
        raise e
###############RELEASES

def insert_release(releaseInfo):
    append_new_line(
                "logs.txt",
                f"Release information retrieved: {releaseInfo.name}, {releaseInfo.version}, {releaseInfo.description}",
    )
    return True

###############MANIFESTS
def insert_kube_manifests(name, imageName, deployment_fp, service_fp, namespace_fp, replicas, status, nodePort, fullUrl):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id_manifest FROM manifeststable WHERE name = %s",
            (name,),
        )
        result = cur.fetchone()
        if result:
            append_new_line(
                "logs.txt",
                "Cannot insert two manifests with same name: {}".format(name),
            )
            conn.close()
            raise Exception("Cannot insert two manifests with same name: {}".format(name))
        else: 
            cur.execute(
                    "INSERT INTO manifeststable (name, imageName, deployment_file_path, service_file_path, namespace_file_path, replicas, status, nodePort, fullUrl)" 
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        name,
                        imageName,
                        deployment_fp,
                        service_fp,
                        namespace_fp, 
                        replicas,
                        status,
                        nodePort,
                        fullUrl
                    ),
                )
            conn.commit()
            append_new_line(
                "logs.txt", "Manifest added:\nName:{}\nImage name:{}\nstatus:".format(name, imageName, status)
            )
            conn.close()
    except Exception as e: 
        append_new_line("logs.txt", "Error inserting manifests: {}".format(e))
        raise e

###############IMAGES
# todo
def insert_jeopardyexecise(jctf_description):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id FROM jeopardycategorytable WHERE category = %s",
            (jctf_description["category"],),
        )
        result = cur.fetchone()
        if result:
            category_id = result[0]
        else:
            cur.execute(
                "INSERT INTO jeopardycategorytable (category) VALUES (%s)",
                (jctf_description["category"],),
            )
            category_id = cur.lastrowid

        # Insert jeopardy ctf
        cur.execute(
            "SELECT id FROM jeopardyexercisetable WHERE title = %s",
            (jctf_description["ctftitle"],),
        )
        result = cur.fetchone()
        if result:
            append_new_line(
                "logs.txt",
                "Exercise already in db: {}".format(jctf_description["ctftitle"]),
            )
            conn.close()
        else:
            cur.execute(
                "INSERT INTO jeopardyexercisetable (title, description, difficulty, id_category, score_if_completed, flag, pod_status)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    jctf_description["ctftitle"],
                    jctf_description["ctfcontext"],
                    jctf_description["ctfrating"],
                    category_id,
                    jctf_description["ctfrating"],
                    jctf_description["flag"],
                    jctf_description["pod_status"],
                ),
            )
            conn.commit()
            append_new_line(
                "logs.txt", "Exercise added: {}".format(jctf_description["ctftitle"])
            )
            conn.close()
    except Exception as e:
        append_new_line("logs.txt", "Error inserting jeopardy exercise: {}".format(e))
        raise e


def insert_jeopardyuserhistory(juserhistory):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        exercise = get_jeopardyexercise_where_id(juserhistory["id_jeopardyexercise"])
        # Insert jeopardy ctf completion to user
        ##bug aici "can't adapt dict type"
        cur.execute(
            "SELECT date_completed FROM jeopardyuserhistorytable WHERE id_jepardyexercise = %s AND id_user = %s ",
            (
                juserhistory["id_jeopardyexercise"],
                juserhistory["id_user"],
            ),
        )
        result = cur.fetchone()
        if result:
            date_completed = result[0]
            append_new_line(
                "logs.txt",
                "User already solved {} at {}, skipping profile update...".format(
                    exercise["title"], date_completed
                ),
            )
        else:
            cur.execute(
                "INSERT INTO jeopardyuserhistorytable (id_jepardyexercise, id_user) VALUES (%s, %s)",
                (juserhistory["id_jeopardyexercise"], juserhistory["id_user"]),
            )
            conn.commit()
            append_new_line("logs.txt", "Profile updated !")
        conn.close()
    except Exception as e:
        append_new_line("logs.txt", "Error updating profile: {}".format(e))
        raise e


##########Selects
def get_jeopardyhistory_where_userid_list(id):
    userhistory_list = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM jeopardyuserhistorytable WHERE id_user = %s", (id,))
        userhistory_listdb = cur.fetchall()
        for row in userhistory_listdb:
            userhistory_list.append(
                {
                    "id_jeopardyexercise": row[1],
                    "id_user": row[2],
                    "date_completed": row[3],
                }
            )
    except Exception as e:
        append_new_line("logs.txt", "Error retrieving user history: {}".format(e))
    return userhistory_list


def get_jeopardyexercises_list():
    jeopardy_list = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM jeopardystable")
        exercises = cur.fetchall()
        for exercise in exercises:
            jeopardy_list.append(
                {
                    "id": exercise[0],
                    "name": exercise[1],
                    "description": exercise[2],
                    "status": exercise[3],
                    "fullUrl": exercise[4],
                    "score": exercise[6]
                }
            )
    except Exception as e:
        append_new_line("logs.txt", "Error retrieving jeopardy exercise: {}".format(e))
    return jeopardy_list


def get_jeopardyexercise_where_id(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM jeopardyexercisetable WHERE id=%s", (id,))
        exercise = cur.fetchone()
        if exercise:
            return {
                "id": exercise[0],
                "title": exercise[1],
                "description": exercise[2],
                "difficulty": exercise[3],
                "score_if_completed": exercise[5],
                "flag": exercise[6],
                "pod_status": exercise[7],
            }
    except Exception as e:
        append_new_line("logs.txt", "Error retrieving jeopardy exercise: {}".format(e))
    return None


def get_userid_where_username(username):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usertable WHERE username=%s", (username,))
        user = cur.fetchone()
        if user:
            return user[0]
    except Exception as e:
        append_new_line("logs.txt", "Error retrieving user: {}".format(e))
    return None

def get_groups():
    group_list = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM grouptable")
        groups = cur.fetchall()
        for group in groups:
            group_list.append(
                {
                    "id": group[0],
                    "name": group[1]
                }
            )
        return group_list
    except Exception as e:
        append_new_line("logs.txt", "Error retrieving group: {}".format(e))
        return None

###########Updates
def update_all_status_to_notRunning():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE jeopardyexercisetable SET pod_status = 'Not Running' WHERE pod_status = 'Running'"
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error updating pod status: {}".format(e))
        raise e


def update_single_pod_status_to_notRunning(name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE jeopardyexercisetable SET pod_status = 'Running' WHERE pod_status = 'Not Running' AND title = %s",
            (name,),
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error updating pod status: {}".format(e))
        raise e


def update_single_pod_status_to_Running(name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE jeopardyexercisetable SET pod_status = 'Running' WHERE pod_status = 'Not Running' AND title = %s",
            (name,),
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error updating pod status: {}".format(e))
        raise e
