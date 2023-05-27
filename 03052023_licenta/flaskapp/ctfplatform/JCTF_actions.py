from ctfplatform.JCTF_backend import get_jeopardyexercises_list, get_jeopardyexercise_where_id, add_JeopardyExercise_to_user, update_existing_jctfs_status, get_helm_chart_info, helm_install ,helm_list, helm_delete_release
from ctfplatform.utils import append_new_line
from ctfplatform.kubernetes_interactions import kube_interaction_inst
# validate flag, return score for future processing
def process_flag():
    return 0

# get jeopardy exercise description
def init():
    return 1

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


def create_JeopardyExercise_helmchart(ctf_name, flag, helm_package_path):
    chart_info = get_helm_chart_info(helm_package_path)
    
    append_new_line("logs.txt", "Installing helm chart with name: {}".format(chart_info["deployment_name"]))

    is_created = helm_install(ctf_name, helm_package_path)
    #update_existing_jctfs_status(chart_info["namespace"])
    return is_created


def authorize_users(release_name):
    append_new_line("logs.txt", "Authorize users")

    # Logic to authorize users for the specified release
    # Return True for now
    return True


def delete_release(release_name, namespace='default'):
    append_new_line("logs.txt", f"Deleting release '{release_name}'...")
    success = helm_delete_release(release_name, namespace)
    if success:
        append_new_line("logs.txt", f"Release '{release_name}' has been deleted.")
    else:
        append_new_line("logs.txt", f"Failed to delete release '{release_name}'.")
    return success

def rollout_release(release_name):
    append_new_line("logs.txt", "Rollout release")
    # Logic to initiate rollout for the specified release
    # Return True for now
    return True


def download_release(release_name):
    append_new_line("logs.txt", "Download release")
    # Logic to download the specified release
    # Return True for now
    return True

def get_helm_releases():
    append_new_line("logs.txt", "Listing all Helm releases...")
    
    # Retrieve the list of namespaces
    namespaces = kube_interaction_inst.kube_list_namespaces()

    releases = []
    for namespace in namespaces:
        namespace_releases = helm_list(namespace)
        releases.extend(namespace_releases)
    
    return releases
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
   
