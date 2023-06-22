import datetime

ALLOWED_EXTENSIONS = {"tgz"}

token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IkFudm12WWVmN1g0YV94Z1lwUFZTMFN2a2ozU3BIUGR0QU9peHcyVUNGZ3MifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJjdGZzcGFjZSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJjdGZwbGF0Zm9ybS1zZWNyZXQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiY3RmcGxhdGZvcm1zYSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjkwNzQzZWYyLTJlNzktNDJhZC1hMDEzLWRmMjU1ZjU2YTQ1ZCIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpjdGZzcGFjZTpjdGZwbGF0Zm9ybXNhIn0.pBY8em8EZv1_I28j6dGtFNtuiLwYkg6LqrhQ87CqmmBUgWrxwcCIx_fGvqwTQL-jvWH912dtRGVa4bjApUiPCK3v0mSHZCSBcK6gBBqaHyCK0-E54aDdMbnozozbqXty7roHrtHxBrthtOUmIWBLF1ZVcbcUbmUdqIAo-9WpMIXxjID5cQ30ajHLmd5kRcsmJ1kdbUrTDzecQJWMRKvNhwr_Q8o-c2fXtz8uojE_FBq1txesPe5IxXpR_OVeutr0EgeJoxKzYiMseKnGSZU7RvnLcHNFxLhcD5ccZ6kMpP9ec58dFphHnZP41xNHdbRwOZymRDqUJikReeyI3Xvdbg"
deployment_template_path = "ctfplatform/manifest_templates/deployment_template.yaml"
service_template_path = "ctfplatform/manifest_templates/service_template.yaml"
namespace_template_path = "ctfplatform/manifest_templates/namespace_template.yaml"
secret_template_path = "ctfplatform/manifest_templates/secret_template.yaml"
ready_manifests_folder_path = "ctfplatform/manifest_templates/manifests/"


def append_new_line(file_name, text_to_append):
    with open(file_name, "a+") as file_object:
        file_object.seek(0)
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        file_object.write(text_to_append)


def get_sa_token():
    return token


def format_timestamp():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%H:%M %d-%m-%Y")
    return formatted_time


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
