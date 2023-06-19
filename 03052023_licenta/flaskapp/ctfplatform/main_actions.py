from ctfplatform.main_backend import get_juserhistory, check_for_same_groupname, add_group
from ctfplatform.utils import append_new_line
from ctfplatform.kubernetes_interactions import kube_interaction_inst


def init():
    append_new_line("logs.txt", "Configuring ctfplatform-chartmuseum repository...")
    cm_ip = kube_interaction_inst.kube_get_chartmuseum()
    kube_interaction_inst.kube_add_chartmuseum_repository(cm_ip)
    return 0


def update_profile(username):
    append_new_line("logs.txt", "Updating profile!")
    return get_juserhistory(username)

def new_group(groupname):
    try:
        append_new_line("logs.txt", f"Creating new group with name {groupname}")
        if check_for_same_groupname(groupname) == False:
            res = add_group(groupname)
        else:
            res = "samename"
        return res
    except Exception as e:
        append_new_line("logs.txt", f"Error creating new group: {e}")
        return False
