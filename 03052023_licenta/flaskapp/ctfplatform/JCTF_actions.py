from ctfplatform.JCTF_backend import (
    add_JeopardyExercise_to_user,
    update_existing_jctfs_status,
    helm_install,
    helm_push,
    helm_list_chartmuseum,
    helm_delete,
    helm_uninstall,
    parse_dockerfile,
    create_kube_manifests,
    add_image,
    is_image_in_repository,
    get_image_digest
    #add_kaniko_context_to_template,
    #start_kaniko
)
from ctfplatform.db_actions import (
    get_jeopardyexercise_where_id,
    get_jeopardyexercises_list
)
from ctfplatform.utils import append_new_line, format_timestamp
import datetime

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


def get_relevant_info(releases):
    relevant_info = []
    for chart in releases.values():
        for entry in chart:
            name = entry["name"]
            version = entry["version"]

            relevant_info.append(
                {"name": name, "version": version, "created": format_timestamp()}
            )

    return relevant_info
def verify_image(imageName_tag, digest):
    try:
        if is_image_in_repository(imageName_tag):
            append_new_line(
                    "logs.txt",
                    f"Image {imageName_tag} found in ctfplatform's private registry repository"
                )
            image_digest_from_repository = get_image_digest(imageName_tag)
            append_new_line(
                    "logs.txt",
                    f"Comparing to {digest}..."
                )
            if digest == image_digest_from_repository:
                append_new_line(
                    "logs.txt",
                    f"Image's {imageName_tag} content successfully verified."
                )
                return True
            else:
                raise Exception("Digest values differ")
        else:
            raise Exception(f"Image {imageName_tag} not found in private repository")
    except Exception as e:
        append_new_line(
                    "logs.txt",
                    f"{e}"
                )
        return False
def create_JeopardyExercise_dockerfile(ctf_name, flag, score, dockerfile_path, imageName_tag, digest, username):
    fullUrl = None
    try:
        append_new_line(
            "logs.txt",
            f"Parsing Dockerfile..."
        )
        targetPort = parse_dockerfile(dockerfile_path)
        if targetPort != None:
            append_new_line(
            "logs.txt",
            f"Port exposed by Dockerfile is {targetPort}"
        )
            res = create_kube_manifests(ctf_name, targetPort, imageName_tag, username)
            if res == True: 
                append_new_line(
                "logs.txt",
                f"Manifests created successfully"
                )
            else:
                append_new_line(
                "logs.txt",
                f"Error creating manifests from templates"
                )
                return False
        else: 
            append_new_line(
            "logs.txt",
            f"Cannot find EXPOSE <portValue> or --port <portValue> inside Dockerfile provided.Cannot create manifest files."
            )
            return False

        res = add_image(ctf_name, flag, score, imageName_tag, digest, fullUrl)
        return res
    except Exception as e:
        return False


def create_JeopardyExercise_helmchart(ctf_name, flag, score, helm_package_path):
    try:
        
        append_new_line(
            "logs.txt",
            "Pushing helm chart with name: {}".format(helm_package_path),
        )

        res = helm_push(helm_package_path)
        if res != 0:
            append_new_line(
                "logs.txt",
                f"Failed to push release '{helm_package_path}'."
            )
        else:
            append_new_line(
                "logs.txt",
                f"Release '{helm_package_path}' has been pushed to chartmuseum.",
            )
        return res
    except Exception as e:
        append_new_line("logs.txt", "Error at pushing helm chart: {}".format(e))


def authorize_users(release_name):
    append_new_line("logs.txt", "Authorize users")

    # Logic to authorize users for the specified release
    # Return True for now
    return True


def apply_release(release_name, release_version):
    try:
        append_new_line(
            "logs.txt", "Installing release with name: {}".format(release_name)
        )

        res = helm_install(release_name)
        if res != 0:
            append_new_line("logs.txt", f"Failed to install release '{release_name}'.")
        else:
            append_new_line("logs.txt", f"Release '{release_name}' has been installed.")
        return res
    except Exception as e:
        append_new_line("logs.txt", "Error installing helm chart: {}".format(e))


def uninstall_release(release_name, release_version):
    try:
        append_new_line(
            "logs.txt", "Uninstalling release with name: {}".format(release_name)
        )

        res = helm_uninstall(release_name)
        if res != 0:
            append_new_line(
                "logs.txt", f"Failed to uninstall release '{release_name}'."
            )
        else:
            append_new_line(
                "logs.txt", f"Release '{release_name}' has been uninstalled."
            )
        return res
    except Exception as e:
        append_new_line("logs.txt", "Error installing helm chart: {}".format(e))


def delete_release(release_name, release_version):
    append_new_line("logs.txt", f"Deleting release '{release_name}'...")

    res = helm_delete(release_name, release_version)
    if res != 0:
        append_new_line("logs.txt", f"Failed to delete release '{release_name}'.")
    else:
        append_new_line("logs.txt", f"Release '{release_name}' has been deleted.")
    return res


def rollout_release(release_name):
    append_new_line("logs.txt", "Rollout release")
    # Logic to initiate rollout for the specified release
    # Return True for now
    return True


def get_helm_releases():
    append_new_line("logs.txt", "Listing all Helm releases...")
    releases_json = helm_list_chartmuseum()
    if releases_json:
        releases_relinfo = get_relevant_info(releases_json)
    else:
        return []

    return releases_relinfo


# Adds the ctf service of pod to the cluster. The service name template is : ctf-<category>-<title>-service.
# Parameters: app field needed for selecting the pod, ~~~
# note to think later: strings like : "web", "crypto", "for" etc for creating the right service
# For example: a web based ctf will need NodePort kind of service so the user can access the vulnerable webpage, meanwhile a crypto ctf will need ssh connetion inside the pod therefore a ClusterIP kind of service.
# ~~~
# Returns True if the service was created successfully.
def create_JeopardyExercise_service():
    service = ""
    is_created = False
    return is_created

def get_releaseInst():
    if(release_inst):
        return release_inst
    else:
        return None
