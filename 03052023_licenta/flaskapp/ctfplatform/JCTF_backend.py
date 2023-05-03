from ctfplatform.kubernetes_interactions import kube_interaction_inst, get_db_connection
from ctfplatform.utils import append_new_line
import os
import re

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
# Returns the local path of the ctf exercise. Needed for other details of the ctf, like description, difficulty, title.
def generate_localpaths():
    try:
        paths = []
        pods = kube_interaction_inst.kube_list_pods()
        for pod in pods.items:
            if 'ctf-' in pod.metadata.name:
                path = {}
                append_new_line('logs.txt', 'Retrieving ctf pod status!')
                if pod.status.phase == 'Running':
                    path['pod_status'] = pod.status.phase
                else:
                    path['pod_status'] = 'Not Running'
                append_new_line('logs.txt', 'CTF Pod status retrieved : {}'.format(pod.status.phase))
    
                append_new_line('logs.txt', 'Retrieving paths!')            
                split_pod_name = pod.metadata.name.split('-')
                ctftitle = split_pod_name[2]
                ctfcategorydirectory = split_pod_name[1]
                path['category'] = ctfcategorydirectory
                append_new_line('logs.txt', 'Printing ctf title: {}'.format(ctftitle))
                
                # Search for CTF directory
                ctf_dir = None
                for root, dirs, files in os.walk(os.getcwd()):
                    if 'CTFRepo-inshack' in dirs:
                        ctf_dir = os.path.join(root, 'CTFRepo-inshack')
                        break
                if ctf_dir is None:
                    raise Exception('CTF directory not found')
                append_new_line('logs.txt', 'Printing ctf local repository: {}'.format(ctf_dir))
                
                # Search for ctf category directory
                category_dir_path = None
                for root, dirs, files in os.walk(ctf_dir):
                    if ctfcategorydirectory in dirs:
                        category_dir_path = os.path.join(root, ctfcategorydirectory)
                        break
                if category_dir_path is None:
                    raise Exception('{} category directory not found'.format(ctfcategorydirectory))
                append_new_line('logs.txt', 'Printing this ctf exercise category path: {}'.format(category_dir_path))

                try:
                    conn = get_db_connection()
                    cur = conn.cursor()
                
                    cur.execute('INSERT INTO jeopardycategorytable (category)'
                    'VALUES (%s)',
                    (ctfcategorydirectory,
                    )
                    )
                    conn.commit()
                    append_new_line('logs.txt', 'Category {} was successfully added!'.format(ctfcategorydirectory))
                except Exception as e:
                    append_new_line('logs.txt', 'Error adding category {} to db : {}'.format(ctfcategorydirectory, e)) 
                
                # Search for ctftitle directory
                ctf_path = None
                for root, dirs, files in os.walk(category_dir_path):
                    if ctftitle in dirs:
                        ctf_path = os.path.join(root, ctftitle)
                        append_new_line('logs.txt', 'New path found: {}'.format(ctf_path))
                        path['path'] = ctf_path
                        break
                if ctf_path is None:
                    raise Exception('CTF path not found')
                paths.append(path)
                append_new_line('logs.txt', 'Paths retrieved successfully!\n')

        return paths     
    except Exception as e:
        append_new_line('logs.txt', 'Error generating local path: {}'.format(e))

# Returns the description, including: context of the ctf, title, difficulty. Since not every ctf has a difficulty attached by the author
# the platform will rate the exercise based on some words/expressions from the writeup file.
# It searches for every file in the respective ctf exercise path with the name equals with : descrition.txt/md and writeup.md/txt or solution.md/txt
# It searches for flag.txt file in ctf's directory, make sure it is created and the flag is in there!
def add_JeopardyExercise_context(path):
    try:
        append_new_line('logs.txt', 'Retrieving description')
        description_file = None
        writeup_file = None
        solution_file = None
        flag_file = None
        flag_txt = None
        
        for root, dirs, files in os.walk(path['path']):
            for file in files:
                filename, file_extension = os.path.splitext(file)
                if file_extension.lower() in ['.txt', '.md']:
                    if filename.lower() == 'description':
                        description_file = os.path.join(root, file)
                    elif filename.lower() == 'writeup':
                        writeup_file = os.path.join(root, file)
                    elif filename.lower() == 'solution':
                        solution_file = os.path.join(root, file)
                    elif filename.lower() == 'flag':
                        flag_file = os.path.join(root, file)
        jctf_description = {}
        append_new_line('logs.txt', 'Relevant files retrieved successfully!')
        jctf_description['pod_status'] = path['pod_status']
        jctf_description['category'] = path['category']
        if description_file:
             with open(description_file, 'r') as f:
                lines = f.readlines()
                jctf_description['ctftitle'] = lines[0].strip('#').strip()
                append_new_line('logs.txt', 'CTF Title: {}'.format(jctf_description['ctftitle']))
                context_lines = [line.strip() for line in lines[2:]]
                context = ' '.join(context_lines).split('Hint:')[0].strip()
                jctf_description['ctfcontext'] = re.sub('<[^<]+?>', '', context)
                append_new_line('logs.txt', 'CTF Context: {}'.format(jctf_description['ctfcontext']))
                jctf_description['ctfhint'] = re.sub('<[^<]+?>', '', lines[-1]).strip()
                append_new_line('logs.txt', 'CTF hint by author: {}'.format(jctf_description['ctfhint']))
        if writeup_file:
            with open(writeup_file, 'r') as f:
                writeup_text = f.read()
                ctfrating = ''
                if EASY_JCTF_1STARRATED in writeup_text:
                    ctfrating = '1/5'
                elif EASY_JCTF_2STARRATED in writeup_text:
                    ctfrating = '2/5'
                elif INTERMEDIATE_JCTF_3STARRATED in writeup_text:
                    ctfrating = '3/5'
                elif ADVANCED_JCTF_4STARRATED in writeup_text:
                    ctfrating = '4/5'
                elif ADVANCED_JCTF_5STARRATED in writeup_text:
                    ctfrating = '5/5'
                if ctfrating:
                    jctf_description['ctfrating'] = ctfrating
                    append_new_line('logs.txt', 'Rating added for --{}-- scenario:  {}'.format(jctf_description['ctftitle'], ctfrating))
        elif solution_file:
            with open(solution_file, 'r') as f:
                solution_file = f.read()
                ctfrating = ''
                if EASY_JCTF_1STARRATED in solution_file:
                    ctfrating = '1/5'
                elif EASY_JCTF_2STARRATED in solution_file:
                    ctfrating = '2/5'
                elif INTERMEDIATE_JCTF_3STARRATED in solution_file:
                    ctfrating = '3/5'
                elif ADVANCED_JCTF_4STARRATED in solution_file:
                    ctfrating = '4/5'
                elif ADVANCED_JCTF_5STARRATED in solution_file:
                    ctfrating = '5/5'
                if ctfrating:
                    jctf_description['ctfrating'] = ctfrating
        if flag_file:
            with open(flag_file, 'r') as f:
                flag_txt = f.read().strip()
                jctf_description['flag'] = flag_txt
                
        if not jctf_description:
            raise Exception('Could not find description file or writeup file')
        append_new_line('logs.txt', 'Description retrieved successfully!\n ')
        
        #Insert exercise
        insert_jeopardyexecise(jctf_description=jctf_description)
    except Exception as e:
        append_new_line('logs.txt', 'Error generating description: {}'.format(e))
        raise e
    
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
    
# The Dockerfile found in It searches for every file in the respective ctf exercise path with the name equals with : Dockerfile
# def get_JeopardyExercise_dockerfiles():
#     try:
#         path = get_JeopardyExercise_path()
#         for root, files in os.walk(path):
#             if 'Dockerfile' in files:
#                 dockerfile_path = os.path.join(root, 'Dockerfile')
#                 return dockerfile_path
#         raise Exception('Couldn't find Dockerfile')
#     except Exception as e:
#         append_new_line('logs.txt', 'Error getting Dockerfile path: {}'.format(e))

# Returns the solution.It searches for every file in the respective ctf exercise path with the name equals with : writeup.txt/md, solution.txt/md, answer.txt/md
def get_JeopardyExercise_solution():
    solution = ''
    return solution
