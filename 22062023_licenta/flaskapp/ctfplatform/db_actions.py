from ctfplatform.kubernetes_interactions import kube_interaction_inst, get_db_connection
from ctfplatform.utils import append_new_line, format_timestamp
from ctfplatform.classes import ReleaseObj
from psycopg2 import OperationalError, errorcodes, errors

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
    
def insert_releasestousertable(username, releasename):
    try: 
        conn = get_db_connection()
        cur = conn.cursor()

        id_release = get_releaseid_where_releasename(releasename)
        id_user = get_userid_where_username(username)

        query = """
            INSERT INTO releasestousertable (id_release, id_user)
            VALUES (%s, %s)
         """
        
        cur.execute(query, (id_release, id_user,))
        conn.commit()

        if cur.rowcount > 0:
            append_new_line("logs.txt", f"Permission granted for {username} to {releasename}")
            return 1
        else:
            append_new_line("logs.txt", f"Couldn't grant permission for {username} to {releasename}")
            return 0
    except Exception as e:
        append_new_line("logs.txt", "Error inserting release to user entry into db: {}".format(e))
        raise e

###############RELEASES

def is_chart_installed(releaseName):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT installed FROM releasestable WHERE name = %s",
            (releaseName,),
        )
        result = cur.fetchone()
        if result is not None:
            if "True" in result: 
                return "True"
            elif "False" in result:
                return "False"
        else:
            append_new_line('logs.txt', "Something happend while checking status of release.")
        return "False"
    except Exception as e:
        Exception("Error while verifying whether release is installed")
        raise e
    
def update_chartInstallationStatus(releaseName, newState):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """UPDATE releasestable
            SET installed = %s WHERE name = %s""",
            (newState, releaseName,),
        )
        
        if cur.rowcount > 0:
            conn.commit()
            return True
        else:
            raise Exception(f"No rows updated for release: {releaseName}")
            
    except Exception as e:
        Exception(f"Error updating release install state: {e}")
        append_new_line('logs.txt', f"Error updating release install state: {e}")
        raise e 
    
def insert_release(releaseInfo):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            "SELECT id FROM releasestable WHERE name = %s",
            (releaseInfo.get_name(),),
        )

        result = cur.fetchone()
        if result:
            conn.close()
            raise Exception(
                "warn","Cannot insert two releases with same name: {}".format(releaseInfo.get_name()),
            )
        else:
            cur.execute(
                "INSERT INTO releasestable (name, version, description, apiVersion, appVersion, type, installed)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    releaseInfo.get_name(),
                    releaseInfo.get_version(),
                    releaseInfo.get_description(),
                    releaseInfo.get_api_version(),
                    releaseInfo.get_app_version(),
                    releaseInfo.get_type(),
                    releaseInfo.is_installed(),
                ),
            )
            conn.commit()
            append_new_line(
                "logs.txt",
                "Release added:\nName:{}\nImage name:{}\nInstalled:{}".format(
                    releaseInfo.get_name(), releaseInfo.get_image_name(), releaseInfo.is_installed()
                )
            )
            conn.close()
    except Exception as e:
        append_new_line("logs.txt", "Error inserting release: {}".format(e))
        raise e
    


###############MANIFESTS
def insert_kube_manifests(
    name,
    imageName,
    deployment_fp,
    service_fp,
    namespace_fp,
    replicas,
    status,
    nodePort,
    fullUrl,
):
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
            raise Exception(
                "Cannot insert two manifests with same name: {}".format(name)
            )
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
                    fullUrl,
                ),
            )
            conn.commit()
            append_new_line(
                "logs.txt",
                "Manifest added:\nName:{}\nImage name:{}\nstatus:".format(
                    name, imageName, status
                ),
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


#####################Selects
def get_releaseid_where_releasename(releasename):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        query = """
            SELECT id FROM releasestable WHERE name=%s
        """
        cur.execute(query, (releasename,))
        res = cur.fetchone()
        if res[0]:
            append_new_line("logs.txt", f"Succes getting release info")
        else:
            append_new_line("logs.txt", f"Fail to get release info")
        return res[0]
    except Exception as e:
        append_new_line("logs.txt", f"Error getting releaseid with {releasename}: {e}")
        raise e
    
def get_group_usertogroup(username):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        user_id = get_userid_where_username(username)
        query = """
            SELECT grouptable.name
            FROM grouptable
            JOIN usertogrouptable ON grouptable.id= usertogrouptable.id_group
            WHERE usertogrouptable.id_user = %s
        """
        cur.execute(query, (user_id,))
        groupname = cur.fetchone()

        if groupname: 
            append_new_line("logs.txt", "User {} is part of {}".format(username, groupname))
            return groupname
        else:
            append_new_line("logs.txt", "User {} is not part of any group".format(username))
            return "None"
    except Exception as e:
        append_new_line("logs.txt", "Error retrieving group of {}: {}".format(username,e))
        raise e

def get_permission_releasestouser(username):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        user_id = get_userid_where_username(username)
        query = """
            SELECT id_release FROM releasestousertable WHERE id_user=%s
        """
        cur.execute(query, (user_id,))
        release_id = cur.fetchone()

        if release_id: 
            append_new_line("logs.txt", "User {} is authorized".format(username))
            return "True"
        else:
            append_new_line("logs.txt", "User {} is not authorized".format(username))
            return "False"
    except Exception as e:
        append_new_line("logs.txt", "Error retrieving permission to release {}: {}".format(username,e))
        raise e
    
def select_all_from_usertable():
    users_list = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        role = "normal"
        cur.execute("SELECT email,username FROM usertable WHERE role=%s", (role,))
        users_listdb = cur.fetchall()
        for row in users_listdb:
            users_list.append(
                {
                    "email": row[0],
                    "username": row[1],
                }
            )
        return users_list
    except Exception as e:
        append_new_line("logs.txt", "Error retrieving user history: {}".format(e))
        raise e

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
                    "score": exercise[6],
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
            group_list.append({"id": group[0], "name": group[1]})
        return group_list
    except Exception as e:
        append_new_line("logs.txt", "Error retrieving group: {}".format(e))
        return None


######################Updates
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

#######################DELETES
def delete_releasestousertable(username, releasename):
    try: 
        conn = get_db_connection()
        cur = conn.cursor()

        id_release = get_releaseid_where_releasename(releasename)
        id_user = get_userid_where_username(username)

        query = """
            DELETE FROM releasestousertable
            WHERE id_release = %s AND id_user = %s
         """
        
        cur.execute(query, (id_release, id_user))
        conn.commit()
        if conn.commit() is None:
            append_new_line("logs.txt", f"Permission deleted for {username} to {releasename} ")
        else:
            append_new_line("logs.txt", f"Couldn't delete permission for {username} to {releasename} ")
            return 0
        return 1
    except Exception as e:
        append_new_line("logs.txt", "Error deleting release to user entry from db: {}".format(e))
        raise e
    