from ctfplatform.kubernetes_interactions import kube_interaction_inst
from ctfplatform.utils import append_new_line
from ctfplatform.db_actions import (
    get_userid_where_username,
    insert_jeopardyuserhistory,
    get_jeopardyexercises_list,
    update_single_pod_status_to_Running,
    update_single_pod_status_to_notRunning,
    update_all_status_to_notRunning,
    insert_release
)
from ctfplatform.classes import ReleaseObj, ImageObj
import tarfile
import yaml
import subprocess
import requests

EASY_JCTF_1STARRATED = "basic"
EASY_JCTF_2STARRATED = "in luck"
INTERMEDIATE_JCTF_3STARRATED = "a bit tricky"
ADVANCED_JCTF_4STARRATED = "out of the box"
ADVANCED_JCTF_5STARRATED = "brilliant people only"


def add_JeopardyExercise_to_user(jctf_id, username):
    try:
        user_id = get_userid_where_username(username)
        juserhistory = {}
        juserhistory["id_user"] = user_id["id"]
        juserhistory["id_jeopardyexercise"] = jctf_id
        append_new_line("logs.txt", "Updating user profile...")
        insert_jeopardyuserhistory(juserhistory=juserhistory)
    except Exception as e:
        append_new_line(
            "logs.txt", "Error adding jeopardy exercise to user: {}".format(e)
        )
        raise e


def update_existing_jctfs_status():
    try:
        pods = kube_interaction_inst.kube_list_pods()
        jctfs = get_jeopardyexercises_list()
        for pod in pods.items:
            if "ctf-" in pod.metadata.name:
                if pod.status.phase == "Running":
                    split_pod_name = pod.metadata.name.split("-")
                    ctftitle = split_pod_name[2]
                    for jctf in jctfs:
                        if (
                            ctftitle == jctf["title"]
                            and jctf["pod_status"] == "Not Running"
                        ):
                            update_single_pod_status_to_Running(ctftitle)
                            break
                else:
                    split_pod_name = pod.metadata.name.split("-")
                    ctftitle = split_pod_name[2]
                    for jctf in jctfs:
                        if (
                            ctftitle == jctf["title"]
                            and jctf["pod_status"] == "Running"
                        ):
                            update_single_pod_status_to_notRunning(ctftitle)
                            break
            else:
                update_all_status_to_notRunning()
                return 1
        return 0
    except Exception as e:
        append_new_line("logs.txt", "Error updating existing pods status: {}".format(e))
        raise e


def update_existing_jctfs_status(namespace):
    try:
        pods = kube_interaction_inst.kube_list_pods(namespace=namespace)
        jctfs = get_jeopardyexercises_list()
        for pod in pods.items:
            if "ctf-" in pod.metadata.name:
                if pod.status.phase == "Running":
                    split_pod_name = pod.metadata.name.split("-")
                    ctftitle = split_pod_name[2]
                    for jctf in jctfs:
                        if (
                            ctftitle == jctf["title"]
                            and jctf["pod_status"] == "Not Running"
                        ):
                            update_single_pod_status_to_Running(ctftitle)
                            break
                else:
                    split_pod_name = pod.metadata.name.split("-")
                    ctftitle = split_pod_name[2]
                    for jctf in jctfs:
                        if (
                            ctftitle == jctf["title"]
                            and jctf["pod_status"] == "Running"
                        ):
                            update_single_pod_status_to_notRunning(ctftitle)
                            break
            else:
                update_all_status_to_notRunning()
                return 1
        return 0
    except Exception as e:
        append_new_line("logs.txt", "Error updating existing pods status: {}".format(e))
        raise e


# Working with helm


def get_JeopardyExercise_solution():
    solution = ""
    return solution


def helm_push(helm_package_path):
    try:
        add_image_and_release(helm_package_path)
        cm_url = kube_interaction_inst.kube_get_chartmuseum()
        if cm_url is not None:
            result = subprocess.run(["helm", "cm-push", helm_package_path, f"{cm_url}"])
            if result.returncode == 0:
                append_new_line("logs.txt", "Package pushed to ctfplatform-chartmuseum")
                return 0
            else:
                return 1
    except Exception as e:
        append_new_line("logs.txt", "Package push failed: {}".format(e))
        raise e


def helm_install(helm_release_name):
    try:
        cm_url = kube_interaction_inst.kube_get_chartmuseum()
        if cm_url is not None:
            result = subprocess.run(
                [
                    "helm",
                    "install",
                    helm_release_name,
                    f"ctfplatform-chartmuseum/{helm_release_name}",
                ]
            )
            if result.returncode == 0:
                append_new_line("logs.txt", "Installation Success")
            return result.returncode
    except Exception as e:
        append_new_line("logs.txt", f"Installation failed: {str(e)}")
        raise e


def helm_uninstall(helm_release_name):
    try:
        cm_url = kube_interaction_inst.kube_get_chartmuseum()
        if cm_url is not None:
            result = subprocess.run(
                [
                    "helm",
                    "uninstall",
                    helm_release_name,
                    f"{helm_release_name}",
                ]
            )
            # k delete namespace (ctfspace)
            if result.returncode == 0:
                append_new_line("logs.txt", "Release uninstalled successfully")
            return result.returncode
    except Exception as e:
        append_new_line(
            "logs.txt", f"Failed to uninstall release {helm_release_name} : {str(e)}"
        )
        raise e


def helm_list_chartmuseum():
    try:
        cm_url = kube_interaction_inst.kube_get_chartmuseum()

        if cm_url is not None:
            # result = subprocess.run(['curl', f'{cm_url}/api/charts'], capture_output=True, text=True)
            response = requests.get(f"{cm_url}/api/charts")
            response.raise_for_status()
            result = response.json()
            if result:
                return result
            else:
                return []

    except requests.exceptions.RequestException as e:
        append_new_line("logs.txt", f"Failed to retrieve charts: {e}")
        return []


def helm_delete(release_name, version):
    try:
        cm_url = kube_interaction_inst.kube_get_chartmuseum()

        if cm_url is not None:
            # result = subprocess.run(['curl -X DELETE', f'{cm_url}/api/charts/{release_name}/{version}'])
            response = requests.delete(f"{cm_url}/api/charts/{release_name}/{version}")
            response.raise_for_status()
            append_new_line(
                "logs.txt",
                f"Deleting '{release_name}/{version}'-->final url:'{cm_url}/api/charts/{release_name}/{version}'.",
            )
            append_new_line(
                "logs.txt", f"Chart package '{release_name}' deleted successfully."
            )
            return 0
    except requests.exceptions.RequestException as e:
        append_new_line(
            "logs.txt", f"Faile to delete chart package '{release_name}': {e}."
        )
        return 1


def add_image_and_release(helm_package_path):
    deployment_name = None
    port = None
    namespace = None
    version = None
    ok = 0
    installed = "False"
    imageName = None
    chart_name = None
    chart_version = None
    chart_description = None
    chart_apiVersion = None
    chart_appVersion = None
    chart_type = None
    with tarfile.open(helm_package_path, "r:gz") as tar:
        chart_files = [member for member in tar.getmembers() if member.isfile()]
        for chart_file in chart_files:
            if chart_file.name.endswith("chart.yaml"):
                chart_info = tar.extractfile(chart_file).read().decode("utf-8")
                chart_data = yaml.safe_load(chart_info)
                
                chart_name  = chart_data.get("name")
                chart_version = chart_data.get("version")
                chart_description = chart_data.get("description")
                chart_apiVersion =  chart_data.get("apiVersion")
                chart_appVersion = chart_data.get("appVersion")
                chart_type = chart_data.get("type")
                ok = ok + 1

            if chart_file.name.endswith("values.yaml"):
                values_info = tar.extractfile(chart_file).read().decode("utf-8")
                values_data = yaml.safe_load(values_info)
                namespace = values_data.get("namespace", namespace)
                deployment_info = values_data.get("deployment", {})
                service_info = values_data.get("service", {})

                deployment_name = deployment_info.get("name", deployment_name)
                imageName = deployment_info.get("imageName", imageName)
                port = service_info.get("port", port)
                #updateImageTag(imageName) and then release_inst will get as imageName the modified image name with the tag of ctfplatform's image registry repository
                #updateChart_deployment_imageName(helm_package_path, imageName) will update the imageName from Values.yaml so the Chart uses the recently pushed image to ctfplatform's image registry repository
                #removeTGZ_file()
                add_image(imageName)
                ok = ok + 1
            if ok == 2:
                release_inst = ReleaseObj(chart_name, chart_version, imageName, chart_description, chart_apiVersion, chart_appVersion, chart_type, installed)
                insert_release(release_inst)

##to implement
def add_image(imageName):
    append_new_line(
        "logs.txt", f"Adding image '{imageName} to ctfplatform's image registry repository..."
    )
    return True
    
