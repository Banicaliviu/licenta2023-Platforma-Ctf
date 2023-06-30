from ctfplatform.main_backend import (
    get_juserhistory,
    check_for_same_groupname,
    add_group
)
from ctfplatform.db_actions import (
    get_group_usertogroup,
    get_permission_releasestouser,
    select_all_from_usertable,
    insert_releasestousertable,
    delete_releasestousertable
)
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

def set_permission_user(username, releasename, permission):
    try:
        if(permission == "True"):
            res = insert_releasestousertable(username, releasename)
            if res == 1: 
                append_new_line("logs.txt", f"Permission set to {permission} for {username} to {releasename}")
            return res
        else:
            res = delete_releasestousertable(username, releasename)
            if res == 1:
                append_new_line("logs.txt", f"Permission set to {permission} for {username} to {releasename}")
            return res
    except Exception as e:
        append_new_line("logs.txt", f"Error retrieving users: {e}")
        return 0

def get_users():
    try:
        users = []
        res_query = []
        res_query = select_all_from_usertable()
        if res_query:
            for user in res_query: 
                permission = get_permission_releasestouser(user["username"])
                group = get_group_usertogroup(user["username"])
                users.append(
                    {
                        "username": user["username"],
                        "email": user["email"],
                        "group": group,
                        "is_authorized": permission,
                    }
                )
        else:
            append_new_line("logs.txt", f"Failed to get users: {users}")
            return []   
        append_new_line("logs.txt", f"Succes: {users}")
        return users
    except Exception as e:
        append_new_line("logs.txt", f"Error retrieving users: {e}")
        return []