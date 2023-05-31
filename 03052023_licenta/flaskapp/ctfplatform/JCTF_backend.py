from ctfplatform.kubernetes_interactions import kube_interaction_inst, get_db_connection
from ctfplatform.utils import append_new_line
import os
import re
import tarfile
import yaml
import subprocess
import json

EASY_JCTF_1STARRATED = 'basic'
EASY_JCTF_2STARRATED = 'in luck'
INTERMEDIATE_JCTF_3STARRATED = 'a bit tricky'
ADVANCED_JCTF_4STARRATED = 'out of the box'
ADVANCED_JCTF_5STARRATED = 'brilliant people only'

###########Inserts
def insert_jeopardyexecise(jctf_description):
    try:
            conn = get_db_connection()
            cur = conn.cursor()
        
            cur.execute('SELECT id FROM jeopardycategorytable WHERE category = %s', (jctf_description['category'],))
            result = cur.fetchone()
            if result:
                category_id = result[0]
            else:
                cur.execute('INSERT INTO jeopardycategorytable (category) VALUES (%s)', (jctf_description['category'],))
                category_id = cur.lastrowid

            # Insert jeopardy ctf
            cur.execute('SELECT id FROM jeopardyexercisetable WHERE title = %s', (jctf_description['ctftitle'],))
            result = cur.fetchone()
            if result:
                append_new_line('logs.txt', 'Exercise already in db: {}'.format(jctf_description['ctftitle']))
                conn.close()
            else:
                cur.execute('INSERT INTO jeopardyexercisetable (title, description, difficulty, id_category, score_if_completed, flag, pod_status)'
                            'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                            (
                                jctf_description['ctftitle'],
                                jctf_description['ctfcontext'],
                                jctf_description['ctfrating'],
                                category_id,
                                jctf_description['ctfrating'],
                                jctf_description['flag'],
                                jctf_description['pod_status']
                            )
                        )
                conn.commit()
                append_new_line('logs.txt', 'Exercise added: {}'.format(jctf_description['ctftitle']))
                conn.close()
    except Exception as e:
        append_new_line('logs.txt', 'Error inserting jeopardy exercise: {}'.format(e))
        raise e   
    

def insert_jeopardyuserhistory(juserhistory):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        exercise = get_jeopardyexercise_where_id(juserhistory['id_jeopardyexercise'])
        # Insert jeopardy ctf completion to user
        ##bug aici "can't adapt dict type"
        cur.execute('SELECT date_completed FROM jeopardyuserhistorytable WHERE id_jepardyexercise = %s AND id_user = %s ',
                    (juserhistory['id_jeopardyexercise'], juserhistory['id_user'],))
        result = cur.fetchone()
        if result:
            date_completed = result[0]
            append_new_line('logs.txt', 'User already solved {} at {}, skipping profile update...'.format(exercise['title'], date_completed))
        else:
            cur.execute('INSERT INTO jeopardyuserhistorytable (id_jepardyexercise, id_user) VALUES (%s, %s)',
                            (
                                juserhistory['id_jeopardyexercise'],
                                juserhistory['id_user']
                            )
                        )
            conn.commit()
            append_new_line('logs.txt', 'Profile updated !')
        conn.close()
    except Exception as e:
        append_new_line('logs.txt', 'Error updating profile: {}'.format(e))
        raise e   
    
##########Selects
def get_jeopardyhistory_where_userid_list(id):
    userhistory_list = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM jeopardyuserhistorytable WHERE id_user = %s', (id,))
        userhistory_listdb = cur.fetchall()
        for row in userhistory_listdb:
            userhistory_list.append({
                'id_jeopardyexercise': row[1],
                'id_user': row[2],
                'date_completed': row[3]
            })
    except Exception as e:
        append_new_line("logs.txt", "Error retrieving user history: {}".format(e))
    return userhistory_list

def get_jeopardyexercises_list():
    jeopardy_list = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM jeopardyexercisetable')
        exercises = cur.fetchall()
        for exercise in exercises:
            jeopardy_list.append({
                'id': exercise[0],
                'title': exercise[1],
                'description': exercise[2],
                'difficulty': exercise[3],
                'pod_status': exercise[7]
            })
    except Exception as e:
        append_new_line("logs.txt", "Error retrieving jeopardy exercise: {}".format(e))
    return jeopardy_list

def get_jeopardyexercise_where_id(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM jeopardyexercisetable WHERE id=%s', (id,))
        exercise = cur.fetchone()
        if exercise:
            return {
                'id': exercise[0],
                'title': exercise[1],
                'description': exercise[2],
                'difficulty': exercise[3],
                'score_if_completed': exercise[5],
                'flag': exercise[6],
                'pod_status': exercise[7]
            }
    except Exception as e:
        append_new_line("logs.txt", "Error retrieving jeopardy exercise: {}".format(e))
    return None

def get_userid_where_username(username):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM usertable WHERE username=%s', (username,))
        user = cur.fetchone()
        if user:
            return {
                'id': user[0]
            }
    except Exception as e:
        append_new_line("logs.txt", "Error retrieving user: {}".format(e))
    return None
###########Updates 
def update_all_status_to_notRunning():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE jeopardyexercisetable SET pod_status = 'Not Running' WHERE pod_status = 'Running'")
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error updating pod status: {}".format(e))
        raise e

def update_single_pod_status_to_notRunning(name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE jeopardyexercisetable SET pod_status = 'Running' WHERE pod_status = 'Not Running' AND title = %s", (name,))
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error updating pod status: {}".format(e))
        raise e
    
def update_single_pod_status_to_Running(name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE jeopardyexercisetable SET pod_status = 'Running' WHERE pod_status = 'Not Running' AND title = %s", (name,))
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error updating pod status: {}".format(e))
        raise e


###########Utility

def add_JeopardyExercise_to_user(jctf_id, username):
    try:
        user_id = get_userid_where_username(username)
        juserhistory = {}
        juserhistory['id_user'] = user_id['id']
        juserhistory['id_jeopardyexercise'] = jctf_id
        append_new_line('logs.txt', 'Updating user profile...')
        insert_jeopardyuserhistory(juserhistory=juserhistory)
    except Exception as e: 
        append_new_line('logs.txt', 'Error adding jeopardy exercise to user: {}'.format(e))
        raise e

def update_existing_jctfs_status():
    try:
        pods = kube_interaction_inst.kube_list_pods()
        jctfs = get_jeopardyexercises_list()
        for pod in pods.items: 
            if 'ctf-' in pod.metadata.name:
                if pod.status.phase == 'Running':
                    split_pod_name = pod.metadata.name.split('-')
                    ctftitle = split_pod_name[2]
                    for jctf in jctfs:
                        if ctftitle == jctf['title'] and jctf['pod_status'] == 'Not Running':
                            update_single_pod_status_to_Running(ctftitle)
                            break
                else:
                    split_pod_name = pod.metadata.name.split('-')
                    ctftitle = split_pod_name[2]
                    for jctf in jctfs:
                        if ctftitle == jctf['title'] and jctf['pod_status'] == 'Running':
                            update_single_pod_status_to_notRunning(ctftitle)
                            break
            else:
                update_all_status_to_notRunning()
                return 1
        return 0
    except Exception as e:
        append_new_line("logs.txt", "Error updating existing pods status: {}".format(e))
        raise e
    
def update_existing_jctfs_status(namespace):
    try:
        pods = kube_interaction_inst.kube_list_pods(namespace=namespace)
        jctfs = get_jeopardyexercises_list()
        for pod in pods.items: 
            if 'ctf-' in pod.metadata.name:
                if pod.status.phase == 'Running':
                    split_pod_name = pod.metadata.name.split('-')
                    ctftitle = split_pod_name[2]
                    for jctf in jctfs:
                        if ctftitle == jctf['title'] and jctf['pod_status'] == 'Not Running':
                            update_single_pod_status_to_Running(ctftitle)
                            break
                else:
                    split_pod_name = pod.metadata.name.split('-')
                    ctftitle = split_pod_name[2]
                    for jctf in jctfs:
                        if ctftitle == jctf['title'] and jctf['pod_status'] == 'Running':
                            update_single_pod_status_to_notRunning(ctftitle)
                            break
            else:
                update_all_status_to_notRunning()
                return 1
        return 0
    except Exception as e:
        append_new_line("logs.txt", "Error updating existing pods status: {}".format(e))
        raise e
    
#Working with helm 

def get_JeopardyExercise_solution():
    solution = ''
    return solution

def helm_push(helm_package_path):
    try:
        cm_url = kube_interaction_inst.kube_get_chartmuseum()
        if cm_url is not None:
            result = subprocess.run(["helm", "cm-push", helm_package_path, f"{cm_url}"])
            if result.returncode == 0:
                append_new_line("logs.txt", "Package pushed to ctfplatform-chartmuseum")
                return 1 
    except Exception as e:
        append_new_line("logs.txt", "Package push failed: {}".format(e))
        raise e
  
def helm_install(helm_release_name):
    try:
        cm_url = kube_interaction_inst.kube_get_chartmuseum()
        if cm_url is not None:
            subprocess.run(["helm", "install", helm_release_name, helm_release_name])
            append_new_line("logs.txt", "Installation Success")
            return 1
    except Exception as e:
        append_new_line("logs.txt", f"Installation failed: {str(e)}")
        raise e
    
def helm_download(helm_release_name, version):
    try:
        cm_url = kube_interaction_inst.kube_get_chartmuseum()
        if cm_url is not None:
            output_tgz_file = f'{helm_release_name}.tgz'
            subprocess.run(["curl", f'{cm_url}/api/charts/{helm_release_name}/{version} --output {output_tgz_file}'])
            append_new_line("logs.txt", "Download Success")
        return output_tgz_file
    except Exception as e:
        append_new_line("logs.txt", f"Download failed: {e}")
        raise e

def helm_list():
    try:
        cm_url = kube_interaction_inst.kube_get_chartmuseum()

        if cm_url is not None:
            result = subprocess.run(['curl', f'{cm_url}/api/charts'], capture_output=True, text=True)
            if result.returncode == 0:
                releases = json.loads(result.stdout)
                return releases
            else:
                append_new_line("logs.txt", f"Failed to list charts: {result.stderr}")
                return []
    except Exception as e:
        append_new_line("logs.txt", f"Failed to retrieve charts: {str(e)}")
        return []

def helm_delete(release_name, version):
    try:
        cm_url = kube_interaction_inst.kube_get_chartmuseum()

        if cm_url is not None:
            result = subprocess.run(['curl', '-X DELETE', f'{cm_url}/api/charts/{release_name}/{version}'])
        if result.returncode == 0:
            append_new_line("logs.txt", f"Chart package '{release_name}' deleted successfully.")
        else:
            raise Exception(f"Failed to delete chart package '{release_name}'.")
    except Exception as e:
        raise e

def get_helm_chart_info(helm_package_path):
    deployment_name = None
    port = None
    namespace = None
    version = None

    with tarfile.open(helm_package_path, 'r:gz') as tar:
        chart_files = [member for member in tar.getmembers() if member.isfile()]
        for chart_file in chart_files:
            if chart_file.name.endswith('values.yaml'):
                values_info = tar.extractfile(chart_file).read().decode('utf-8')
                values_data = yaml.safe_load(values_info)
                namespace = values_data.get('namespace', namespace)
                deployment_info = values_data.get('deployment', {})
                service_info = values_data.get('service', {})
                
                deployment_name = deployment_info.get('name', deployment_name)
                port = service_info.get('port', port)
            
                break

    return {"deployment_name": deployment_name, "port": port, "namespace": namespace}