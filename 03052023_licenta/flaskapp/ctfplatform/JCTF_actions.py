from ctfplatform.JCTF_backend import generate_localpaths, add_JeopardyExercise_context, get_jeopardyexercises_list, get_jeopardyexercise_where_id, add_JeopardyExercise_to_user, update_existing_jctfs_status
from ctfplatform.utils import append_new_line
# validate flag, return score for future processing
def process_flag():
    return 0

# get jeopardy exercise description
def init():
    paths = {}
    paths = generate_localpaths()
    for path in paths:
        add_JeopardyExercise_context(path=path)

def get_jctf_list():
    return get_jeopardyexercises_list()

def get_jctf_id(id):
    return get_jeopardyexercise_where_id(id=id)

def update_userhistory(jctf_id, username):
    add_JeopardyExercise_to_user(jctf_id, username)

def update_jctfs_status():
    update_existing_jctfs_status()

# For admins only.

# Adds the ctf pod to the cluster. The pod name template is : ctf-<category>-<title>-deployment.
# Returns True if the pod was created successfully.
def create_JeopardyExercise_deployment():
    deployment = ""
    is_created = False
    return is_created
   
# Adds the ctf service of pod to the cluster. The service name template is : ctf-<category>-<title>-service.
# Parameters: app field needed for selecting the pod, ~~~
# note to think later: strings like : "web", "crypto", "for" etc for creating the right service
# For example: a web based ctf will need NodePort kind of service so the user can access the vulnerable webpage, meanwhile a crypto ctf will need ssh connetion inside the pod therefore a ClusterIP kind of service.
#~~~
# Returns True if the service was created successfully.
def create_JeopardyExercise_service():
    service = ""
    is_created = False
    return is_created
   
