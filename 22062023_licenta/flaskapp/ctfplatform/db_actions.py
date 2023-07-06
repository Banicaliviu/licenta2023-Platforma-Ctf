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

def insert_solution(exerciseName, exerciseScore, username):
    try: 
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
            INSERT INTO scoreboardtable (exercise_name, user_name, score)
            VALUES (%s, %s, %s)
         """
        
        cur.execute(query, (exerciseName, username, exerciseScore,))
        conn.commit()

        if cur.rowcount > 0:
            append_new_line("logs.txt", f"Scoreboard updated!")
            return 1
        else:
            append_new_line("logs.txt", f"Couldn't update scoreboard")
            return 0
    except Exception as e:
        append_new_line("logs.txt", "Error updating scoreboard: {}".format(e))
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
            return True
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
def insert_jeopardyexercise(name, flag, score, status, fullUrl, description, namespace):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO jeopardystable (name, flag, score, status, fullUrl, description, namespace)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (
                name,
                flag,
                score,
                status,
                fullUrl,
                description,
                namespace,
            ),
        )
        conn.commit()
        append_new_line(
            "logs.txt", "Exercise added: {} in {} namespace".format(name, namespace)
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

def insert_jeopardytorelease(id_jeopardy, id_release, jeopardyName, releaseName):
    try: 
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
            INSERT INTO jeopardytoreleasetable (id_jeopardy, id_release)
            VALUES (%s, %s)
         """
        
        cur.execute(query, (id_jeopardy, id_release,))
        conn.commit()

        if cur.rowcount > 0:
            append_new_line("logs.txt", f"Jeopardy {jeopardyName} exercise is based on {releaseName} release")
            return 1
        else:
            append_new_line("logs.txt", f"Couldn't connect {jeopardyName} to {releaseName}")
            return 0
    except Exception as e:
        append_new_line("logs.txt", "Error connecting exercise to release: {}".format(e))
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

def get_jeopardyId_where_releaseId(id_release):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        query = """
            SELECT id_jeopardy FROM jeopardytoreleasetable WHERE id_release=%s
        """
        cur.execute(query, (id_release,))
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
    
def list_permissions_for(username):
    perm_list = []
    j_names = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        append_new_line("logs.txt", f"Fetching releases available to {username}")
        user_id = get_userid_where_username(username)
        query = """
            SELECT id_release FROM releasestousertable WHERE id_user=%s
        """
        cur.execute(query, (user_id,))
        release_id_list = cur.fetchall()

        append_new_line("logs.txt", f"Correlating them to jeopardys {release_id_list}")
        for row in release_id_list:
            query = """
                SELECT id_jeopardy FROM jeopardytoreleasetable WHERE id_release=%s
            """
            cur.execute(query, (row[0],))
            res = cur.fetchone()
            if res:
                perm_list.append(res[0])

        append_new_line("logs.txt", f"Succes: {perm_list}")    
        for id_jeopardy in perm_list:
            query = """
                SELECT name FROM jeopardystable WHERE id=%s
            """
            cur.execute(query, (id_jeopardy,))
            res = cur.fetchone()
            if res: 
                j_names.append(res[0])
        append_new_line("logs.txt", f"Succes: {j_names}")          
        return perm_list
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
    
def select_all_scoreboard():
    scoreboard_list = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM scoreboardtable")
        scoreboard_listdb = cur.fetchall()
        for row in scoreboard_listdb:
            scoreboard_list.append(
                {
                    "exercise_name": row[1],
                    "user_name": row[2],
                    "score": row[3],
                    "solvedAt": row[4]
                }
            )
        return scoreboard_list
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
        if exercises:
            for exercise in exercises:
                jeopardy_list.append(
                    {
                        "id": exercise[0],
                        "name": exercise[1],
                        "score": exercise[3],
                        "status": exercise[4],
                        "fullUrl": exercise[5],
                        "description": exercise[6],
                        "is_authorized": "False",
                    }
                )
        else:
            return []
        
    except Exception as e:
        append_new_line("logs.txt", "Error retrieving jeopardy exercise: {}".format(e))
        return []
    return jeopardy_list

def get_release_where_jeopardyid(id_jeopardy):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        append_new_line("logs.txt", "Getting release based on jeopardy exercise id {}".format(id_jeopardy))
        cur.execute(
            "SELECT id_release FROM jeopardytoreleasetable WHERE id_jeopardy=%s",
            (id_jeopardy,),
        )
        row = cur.fetchone()
        
        id_release = row[0]

        row = get_release_where_releaseId(id_release)

        conn.commit()

        releaseDict = []
        releaseDict.append(
            {
                "name":row[0],
                "version":row[1],
            }
        )
        return releaseDict
    except Exception as e: 
        append_new_line("logs.txt", "Error getting release based on id of exercise")
        raise e

def get_release_where_releaseId(id_release):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT name, version FROM releasestable WHERE id=%s",
            (id_release,),
        )
        row = cur.fetchone()
        conn.commit()
        return row
    except Exception as e:
        append_new_line("logs.txt", "Error getting release based on id of release")
        raise e
    
def get_jeopardyexercise_where_id(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM jeopardystable WHERE id=%s", (id,))
        exercise = cur.fetchone()
        if exercise:
            return {
                "name": exercise[1],
                "score": exercise[3],
                "status": exercise[4],
                "description": exercise[6],
                "flag":exercise[2]
            }
    except Exception as e:
        append_new_line("logs.txt", "Error retrieving jeopardy exercise: {}".format(e))
    return None

def get_connection_conUrl_where_usernameidJeopardy(username, id_jeopardy):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        id_user = get_userid_where_username(username)
        cur.execute("SELECT conUrl FROM jeopardytousertable WHERE id_jeopardy=%s AND id_user=%s", (id_jeopardy, id_user,))
        res = cur.fetchone()
        if res:
           conUrl = res[0]
           append_new_line("logs.txt", "ConUrl is: {}".format(conUrl))
           return conUrl
    except Exception as e:
        append_new_line("logs.txt", "Error retrieving connection string for exercise: {}".format(e))
        

def add_connection(username, id_jeopardy, conUrl):
    try: 
        conn = get_db_connection()
        cur = conn.cursor()
        
        id_user = get_userid_where_username(username)

        query = """
            INSERT INTO jeopardytousertable (id_jeopardy, id_user, conUrl)
            VALUES (%s, %s, %s)
         """
        
        cur.execute(query, (id_jeopardy, id_user, conUrl,))
        conn.commit()

        if cur.rowcount > 0:
            append_new_line("logs.txt", f"{username} started an attempt. Connection string : {conUrl}!")
            return 1
        else:
            append_new_line("logs.txt", f"Couldn't add connection")
            return 0
    except Exception as e:
        append_new_line("logs.txt", "Error inserting jeopardy to user entry into db: {}".format(e))
        raise e
    
def get_connections():
    try: 
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
            SELECT COUNT(*) FROM jeopardytousertable
        """

        cur.execute(query)
        res = cur.fetchone()

        if res[0] > 0:
            append_new_line("logs.txt", f"There are {res[0]} connections")
        else:
            append_new_line("logs.txt", "There are no connections")

        return res[0]
    
    except Exception as e:
        append_new_line("logs.txt", "Error counting jeopardy to user entries in the database: {}".format(e))
        raise e
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

def get_jeopardy_id_where_name(name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM jeopardystable WHERE name=%s", (name,))
        id_jeopardy_res = cur.fetchone()
        if id_jeopardy_res:
            return id_jeopardy_res[0]
    except Exception as e:
        append_new_line("logs.txt", "Error retrieving jeopardy exercise: {}".format(e))

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

def set_status(jExercise):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id_release FROM jeopardytoreleasetable WHERE id_jeopardy=%s",
            (jExercise["id"],),
        )
        row = cur.fetchone()
        if row:
            id_release = row[0]
        else:
            append_new_line('logs.txt', 'No jeopardy to release row found')
            return False
            
        cur.execute(
            "SELECT name FROM releasestable WHERE id=%s",
            (id_release,),
        )
        row = cur.fetchone()

        releaseName = row[0]

        res = is_chart_installed(releaseName)

        if res == 'True':
            res = update_single_exercise_status(jExercise["id"], 'Running')
        elif res == 'False':
            res = update_single_exercise_status(jExercise["id"], 'Not Running')

        conn.commit()
        return res

    except Exception as e:
        append_new_line("logs.txt", "Error updating exercise status: {}".format(e))
        raise e
    

def update_single_exercise_status(id_jeopardy, desired_state):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE jeopardystable SET status=%s WHERE id=%s",
            (desired_state, id_jeopardy,),
        )
        if cur.rowcount > 0:
            conn.commit()
            return desired_state
        else:
            append_new_line("logs.txt", "No rows updated exercise status")
            return False
    except Exception as e:
        append_new_line("logs.txt", "Error updating exercise status: {}".format(e))
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
        
        cur.execute(query, (id_release, id_user,))
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
    
def delete_release_where_releaseId_cascade(id_release):
    try: 
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
            DELETE FROM releasestable
            WHERE id = %s
         """
        
        cur.execute(query, (id_release,))
        conn.commit()
        if conn.commit() is None:
            append_new_line("logs.txt", f"Successfully delete all entries from database of selected release")
        else:
            append_new_line("logs.txt", f"Couldn't delete all entries from database of selected release")
            return 0
        return 1
    except Exception as e:
        append_new_line("logs.txt", "Error deleting release entries from database: {}".format(e))
        raise e
    
def delete_jeopardy_where_jeopardyId(id_jeopardy):
    try: 
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
            DELETE FROM jeopardystable
            WHERE id = %s
         """
        
        cur.execute(query, (id_jeopardy,))
        conn.commit()
        if conn.commit() is None:
            append_new_line("logs.txt", f"Successfully deleted all ctfs related to selected release ")
        else:
            append_new_line("logs.txt", f"Couldn't deleted all ctfs related to selected release ")
            return 0
        return 1
    except Exception as e:
        append_new_line("logs.txt", "Error deleting jeopardy entry from database: {}".format(e))
        raise e
    