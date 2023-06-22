from ctfplatform.utils import append_new_line
from ctfplatform.JCTF_backend import (
    get_userid_where_username,
)
from ctfplatform.db_actions import (
    get_jeopardyhistory_where_userid_list,
    get_jeopardyexercise_where_id,
    get_groups,
    insert_group,
)


#########Inserts
def add_group(groupname):
    try:
        append_new_line("logs.txt", "Adding group... ")
        res = insert_group(groupname)
        if res == True:
            append_new_line("logs.txt", f"Successfully added group {groupname}")

        return res
    except Exception as e:
        append_new_line("logs.txt", "Error getting groups: {}".format(e))
        raise e


#########Selects
def check_for_same_groupname(groupname):
    try:
        append_new_line("logs.txt", "Selecting group names... ")
        group_list = get_groups()
        if group_list == None:
            append_new_line("logs.txt", "No groups found ")
            return False

        for group in group_list:
            if groupname == group["name"]:
                return True

        return False
    except Exception as e:
        append_new_line("logs.txt", "Error getting groups: {}".format(e))
        raise e


##########Utility
def get_juserhistory(username):
    try:
        append_new_line("logs.txt", "Updating profile ... ")
        profile_score = 0
        user_id = get_userid_where_username(username)
        completed_jctfs_list = []
        userhistory_list = get_jeopardyhistory_where_userid_list(user_id)
        if userhistory_list:
            completed_jctfs_list = []
            for row in userhistory_list:
                completed_jctfs_list.append(
                    get_jeopardyexercise_where_id(row["id_jeopardyexercise"])
                )
            for jctf in completed_jctfs_list:
                score = jctf["score_if_completed"].split("/")
                profile_score += int(score[0])
            return {"score": profile_score, "jctfs": completed_jctfs_list}
        else:
            append_new_line("logs.txt", "No history found for user {}".format(username))
            return {"score": 0, "jctfs": completed_jctfs_list}
    except Exception as e:
        append_new_line("logs.txt", "Error updating profile: {}".format(e))
        raise e
