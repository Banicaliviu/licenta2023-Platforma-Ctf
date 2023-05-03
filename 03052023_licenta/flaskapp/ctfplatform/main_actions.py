from ctfplatform.main_backend import get_juserhistory
from ctfplatform.utils import append_new_line

def update_profile(username):
    append_new_line("logs.txt", "Updating profile!")
    return get_juserhistory(username)