from ctfplatform.main_backend import get_juserhistory
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