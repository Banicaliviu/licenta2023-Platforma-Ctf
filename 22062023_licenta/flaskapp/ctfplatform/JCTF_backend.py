from ctfplatform.kubernetes_interactions import kube_interaction_inst
from ctfplatform.utils import (
    append_new_line,
    deployment_template_path,
    service_template_path,
    namespace_template_path,
    secret_template_path,
    ready_manifests_folder_path,
)
from ctfplatform.db_actions import (
    get_userid_where_username,
    insert_jeopardyuserhistory,
    get_jeopardyexercises_list,
    update_single_pod_status_to_Running,
    update_single_pod_status_to_notRunning,
    update_all_status_to_notRunning,
    insert_release,
    insert_kube_manifests,
    insert_jeopardyexercise,
    get_jeopardy_id_where_name,
    get_releaseid_where_releasename,
    insert_jeopardytorelease,
    delete_release_where_releaseId_cascade,
    get_jeopardyId_where_releaseId,
    delete_jeopardy_where_jeopardyId,
    get_jeopardyexercise_where_id,
)
from ctfplatform.classes import ReleaseObj, ImageObj

import tarfile
import yaml
import subprocess
import requests
import re
import os
import shutil
from urllib.parse import urlparse

def add_JeopardyExercise_to_user(jctf_id, username):
    try:
        user_id = get_userid_where_username(username)
        juserhistory = {}
        juserhistory["id_user"] = user_id
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


############ Working with Dockerfile
def parse_dockerfile(Dockerfile):
    try:
        with open(Dockerfile, "r") as file:
            dockerfile_content = file.read()

        # Search for EXPOSE <port> or --port <port> patterns
        expose_pattern = r"EXPOSE\s+(\d+)"
        port_pattern = r"--port\s+(\d+)"

        expose_match = re.search(expose_pattern, dockerfile_content)
        port_match = re.search(port_pattern, dockerfile_content)

        if expose_match:
            port = expose_match.group(1)
        elif port_match:
            port = port_match.group(1)
        else:
            port = None

        return port
    except Exception as e:
        append_new_line("logs.txt", "Error parsing Dockerfile: {}".format(e))
        raise e


def create_kube_manifests(name, port, image, username):
    try:
        ##create manifest files(deployment, service, namespace)
        custom_namespace = f"{name}-{username}"
        namespace_file_path = create_namespace_from_template(
            namespace_template_path, custom_namespace
        )
        secret_file_path = create_secret_from_template(
            secret_template_path, custom_namespace
        )
        deployment_file_path = create_deployment_from_template(
            deployment_template_path, custom_namespace, image, port
        )
        service_file_path = create_service_from_template(
            service_template_path, custom_namespace, port
        )
        custom_name_folder = get_ctf_folder(
            ready_manifests_folder_path, custom_namespace
        )
        ##apply manifes files

        res = kube_interaction_inst.kube_apply_directory(custom_name_folder)
        if res == True:
            deployments_info = kube_interaction_inst.kube_list_deployments(
                name=name, namespace=custom_namespace
            )
            services_info = kube_interaction_inst.kube_list_services(
                name=name, namespace=custom_namespace
            )

            status = []
            replicas = []
            for deployment_info in deployments_info:
                status.append(deployment_info["status"])
                replicas.append(deployment_info["replicas"])

            nodePort = []
            for service_info in services_info:
                nodePort.append(service_info["nodePort"])

            nodeIp = kube_interaction_inst.kube_get_node_ip()
            external_ip = f"{nodeIp}:{nodePort[0]}"

            insert_kube_manifests(
                name,
                image,
                deployment_file_path,
                service_file_path,
                namespace_file_path,
                replicas[0],
                status[0],
                nodePort[0],
                external_ip,
            )
        else:
            raise Exception(f"Couldn't apply {custom_name_folder}")
        ##insert manifests
        return True
    except Exception as e:
        append_new_line("logs.txt", f"{e}")
        return False


def add_image(ctf_name, flag, score, imageName, digest, fullUrl):
    # Call insert image from db_actions
    return False


def is_image_in_repository(imageName_tag):
    imageTag = get_image_tag(imageName_tag)
    imageName = get_image_name(imageName_tag)
    registry_url = kube_interaction_inst.kube_get_docker_registry()

    manifest_url = f"http://{registry_url}/v2/{imageName}/manifests/{imageTag}"
    append_new_line("logs.txt", f"{manifest_url}")
    headers = {"Accept": "application/vnd.docker.distribution.manifest.v2+json"}

    try:
        response = requests.head(manifest_url, headers=headers)
        append_new_line("logs.txt", f"{response}")
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception:
        return False


def get_image_digest(imageName_tag):
    imageTag = get_image_tag(imageName_tag)
    imageName = get_image_name(imageName_tag)
    registry_url = kube_interaction_inst.kube_get_docker_registry()

    manifest_url = f"http://{registry_url}/v2/{imageName}/manifests/{imageTag}"
    headers = {"Accept": "application/vnd.docker.distribution.manifest.v2+json"}

    try:
        response = requests.head(manifest_url, headers=headers)
        append_new_line("logs.txt", f"{response}")
        if "Docker-Content-Digest" in response.headers:
            append_new_line("logs.txt", f"{response.headers}")
            digest_header = response.headers["Docker-Content-Digest"]
            digest_value = digest_header.split("sha256:")[-1]
            append_new_line("logs.txt", f"{digest_value}")
            return digest_value
        else:
            return None
    except Exception:
        return None


def get_image_tag(imageName_tag):
    try:
        tag = imageName_tag.split(":")[1]
        return tag
    except IndexError:
        return None


def get_image_name(imageName_tag):
    try:
        name = imageName_tag.split(":")[0]
        return name
    except IndexError:
        return None


def get_ctf_folder(ready_manifests_folder_path, name):
    try:
        if not os.path.exists(ready_manifests_folder_path):
            append_new_line("logs.txt", f"Creating manifest folder...")
            os.makedirs(ready_manifests_folder_path)

        ctf_folder = os.path.join(ready_manifests_folder_path, name)

        if not os.path.exists(ctf_folder):
            append_new_line("logs.txt", f"Creating {name} folder {ctf_folder}...")
            os.makedirs(ctf_folder)

        return ctf_folder
    except Exception as e:
        append_new_line("logs.txt", f"Error creating manifest folder for {name}")
        raise e


def create_secret_from_template(secret_template_path, name):
    try:
        ctf_folder = get_ctf_folder(ready_manifests_folder_path, name)

        secret_file_path = os.path.join(ctf_folder, f"{name}-secret.yaml")

        if not os.path.exists(secret_file_path):
            append_new_line("logs.txt", f"Creating {name}-secret.yaml ...")

            shutil.copy(secret_template_path, secret_file_path)

            with open(secret_file_path, "r") as file:
                secret_content = file.read()

            secret_content = secret_content.replace("<TBD_NAME>", name)

            with open(secret_file_path, "w") as file:
                file.write(secret_content)

            append_new_line("logs.txt", f"{name}-secret.yaml successfully created ")
        else:
            append_new_line("logs.txt", f"{name}-secret.yaml already exists")

        return secret_file_path
    except Exception as e:
        append_new_line("logs.txt", f"Error creating secret from template: {e}")
        raise e


def create_namespace_from_template(namespace_template_path, name):
    try:
        ctf_folder = get_ctf_folder(ready_manifests_folder_path, name)

        namespace_file_path = os.path.join(ctf_folder, f"{name}-namespace.yaml")

        if not os.path.exists(namespace_file_path):
            append_new_line("logs.txt", f"Creating {name}-namespace.yaml ...")

            shutil.copy(namespace_template_path, namespace_file_path)

            with open(namespace_file_path, "r") as file:
                namespace_content = file.read()

            namespace_content = namespace_content.replace("<TBD_NAME>", name)

            with open(namespace_file_path, "w") as file:
                file.write(namespace_content)

            append_new_line("logs.txt", f"{name}-namespace.yaml successfully created ")
        else:
            append_new_line("logs.txt", f"{name}-namespace.yaml already exists")

        return namespace_file_path
    except Exception as e:
        append_new_line("logs.txt", f"Error creating namespace from template: {e}")
        raise e


def create_deployment_from_template(deployment_template_path, name, image, port):
    try:
        ctf_folder = get_ctf_folder(ready_manifests_folder_path, name)

        deployment_file_path = os.path.join(ctf_folder, f"{name}-deployment.yaml")

        if not os.path.exists(deployment_file_path):
            append_new_line("logs.txt", f"Creating {deployment_file_path}.yaml... ")

            shutil.copy(deployment_template_path, deployment_file_path)

            with open(deployment_file_path, "r") as file:
                deployment_content = file.read()

            registry_url = kube_interaction_inst.kube_get_docker_registry()
            manifest_url = f"{registry_url}/{image}"
            # manifest_url = f"registryrepository.192.168.49.2.nip.io/{image}"
            append_new_line("logs.txt", f"Updating {name}-deployment.yaml...")
            deployment_content = deployment_content.replace("<TBD_NAME>", name)
            deployment_content = deployment_content.replace("<TBD_IMAGE>", manifest_url)
            deployment_content = deployment_content.replace("<TBD_PORT>", str(port))

            append_new_line("logs.txt", f"Saving {name}-deployment.yaml...")
            with open(deployment_file_path, "w") as file:
                file.write(deployment_content)

            append_new_line("logs.txt", f"{name}-deployment.yaml successfully created ")
        else:
            append_new_line("logs.txt", f"{name}-deployment.yaml already exists")
            with open(deployment_file_path, "r") as file:
                deployment_content = file.read()

            # registry_url = kube_interaction_inst.kube_get_docker_registry()
            # manifest_url = f"{registry_url}/{image}"
            manifest_url = f"registryrepository.192.168.49.2.nip.io/{image}"
            append_new_line("logs.txt", f"Updating {name}-deployment.yaml...")
            deployment_content = deployment_content.replace("<TBD_IMAGE>", manifest_url)
            append_new_line(
                "logs.txt",
                f"{name}-deployment.yaml already exists: image updated with {manifest_url} ",
            )
        return deployment_file_path
    except Exception as e:
        append_new_line("logs.txt", f"Error creating deployment from template: {e}")
        raise e


def create_service_from_template(service_template_path, name, port):
    try:
        ctf_folder = get_ctf_folder(ready_manifests_folder_path, name)

        service_file_path = os.path.join(ctf_folder, f"{name}-service.yaml")

        if not os.path.exists(service_file_path):
            append_new_line("logs.txt", f"Creating {name}-service.yaml ...")

            shutil.copy(service_template_path, service_file_path)

            with open(service_file_path, "r") as file:
                service_content = file.read()

            append_new_line("logs.txt", f"Updating {name}-service.yaml...")
            service_content = service_content.replace("<TBD_NAME>", name)
            service_content = service_content.replace("<TBD_PORT>", str(port))

            append_new_line("logs.txt", f"Saving {name}-service.yaml...")
            with open(service_file_path, "w") as file:
                file.write(service_content)

            append_new_line("logs.txt", f"{name}-service.yaml successfully created ")
        else:
            append_new_line("logs.txt", f"{name}-service.yaml already exists ")
        return service_file_path
    except Exception as e:
        append_new_line("logs.txt", f"Error creating service from template: {e}")
        raise e

def create_namespace(username, id_jeopardy):
    try:
        exercise_jeopardy = get_jeopardyexercise_where_id(id_jeopardy)
        nsName = kube_interaction_inst.kube_create_custom_ns(username, exercise_jeopardy["name"])
        append_new_line('logs.txt', 'namespace created')
        return nsName
    except Exception as e:
        append_new_line("logs.txt", "Error creating namespace: {}".format(e))
        raise e

####### Working with helm charts 
def helm_push(helm_package_path):
    try:
        cm_url = kube_interaction_inst.kube_get_chartmuseum()
        if cm_url is not None:
            result = subprocess.run(["helm", "cm-push", helm_package_path, f"{cm_url}"])
            if result.returncode == 0:
                append_new_line("logs.txt", "Package pushed to ctfplatform-chartmuseum")
                append_new_line("logs.txt", "Removing package from local storage...")
                result = subprocess.run(["rm", helm_package_path])
                if result.returncode == 0:
                    append_new_line("logs.txt", "Package removed from local storage.")
                else: 
                    error_message = result.stderr.strip()
                    raise Exception(f"Couldn't remove package: {error_message}")
            return result.returncode
    except Exception as e:
        append_new_line("logs.txt", "Package push failed: {}".format(e))
        raise e


def helm_install(helm_release_name, helm_release_version):
    try:
        cm_url = kube_interaction_inst.kube_get_chartmuseum()
        if cm_url is not None:
            result = subprocess.run([
                "helm",
                "pull",
                f"{cm_url}/charts/{helm_release_name}-{helm_release_version}.tgz"
            ])
            result.check_returncode()
            append_new_line("logs.txt", "Chart pulled successfully")
            result = subprocess.check_call([
                    "helm",
                    "install",
                    helm_release_name,
                    f"./{helm_release_name}-{helm_release_version}.tgz",
                ])
            if result == 0:
                append_new_line("logs.txt", "Proceding with installation...")
            else: 
                append_new_line("logs.txt", "Cannot proceed with installation reason: FAIL")
                raise Exception("Cannot proceed with installation reason: FAIL") 
            
            subprocess.run(
                [
                    "helm",
                    "install",
                    helm_release_name,
                    f"./{helm_release_name}-{helm_release_version}.tgz",
                ]
            )
            
            append_new_line("logs.txt", "Removing package from local storage...")
            result = subprocess.check_call([
                    "rm",
                    f"{helm_release_name}-{helm_release_version}.tgz",
                ])
            if result == 0:
                append_new_line("logs.txt", "Cleaning up...")
            else: 
                append_new_line("logs.txt", "Cannot clean up resources reason: FAIL")
                raise Exception("Cannot clean up resources reason: FAIL")
            
            result = subprocess.run(["rm", f"{helm_release_name}-{helm_release_version}.tgz"])
            
            append_new_line("logs.txt", "Package removed from local storage.")
            return 0
    except Exception as e:
        append_new_line("logs.txt", f"Installation failed: {str(e)}")
        raise e


def helm_uninstall(helm_release_name):
    try:
        result = subprocess.run(
            [
                "helm",
                "uninstall",
                helm_release_name,
            ]
        )
        result.check_returncode()
        append_new_line("logs.txt", "Release uninstalled successfully")
        return True
    except Exception as e:
        append_new_line(
            "logs.txt", f"Failed to uninstall release {helm_release_name} : {str(e)}"
        )
        raise e

def helm_install_custom(nsName, helm_package_path):
    try:
        result = subprocess.run(
            [
                "helm",
                "install",
                nsName,
                f"./{helm_package_path}",
            ]
        )
        result.check_returncode()
        append_new_line("logs.txt", f"Installation success: {helm_package_path}")
        return True
    except Exception as e:
        append_new_line("logs.txt", f"Installation failed: {str(e)}")
        raise e

def helm_rm_custom(helm_package_path):
    try:
        append_new_line("logs.txt", "Removing package from local storage...")

        result = subprocess.run(
            [
               "rm",
                f"./{helm_package_path}",
            ]
        )
        result.check_returncode()
        append_new_line("logs.txt", f"Cleaning up success: {helm_package_path}")
        return True
    except Exception as e:
        append_new_line("logs.txt", f"Cleaning up failed: {str(e)}")
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
            "logs.txt", f"Failed to delete chart package '{release_name}': {e}."
        )
        return 1

def helm_pull(releaseName, releaseVersion):
    try:
        cm_url = kube_interaction_inst.kube_get_chartmuseum()
        if cm_url is not None:
            result = subprocess.run([
                "helm",
                "pull",
                f"{cm_url}/charts/{releaseName}-{releaseVersion}.tgz"
            ])
            result.check_returncode()
            append_new_line("logs.txt", "Chart pulled successfully")
            return True
    except Exception as e:
        append_new_line("logs.txt", f"Error pulling release {e}")
        raise e
    
def delete_entries(releaseName):
    try: 
        id_release = get_releaseid_where_releasename(releaseName)
        id_jeopardy = get_jeopardyId_where_releaseId(id_release)
        if id_release and id_jeopardy:
            res = delete_release_where_releaseId_cascade(id_release)
            if res == 0:
                return 1
            
            res = delete_jeopardy_where_jeopardyId(id_jeopardy)
            if res == 0:
                return 1
        return 0
    except Exception as e:
        append_new_line('logs.txt', f'Error: {e}')
        return 1

def get_node_ip():
    return kube_interaction_inst.kube_get_node_ip()

def parse_release(helm_package_path):
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
    append_new_line(
                    "logs.txt", f"Retrieving release data'."
    )
    try:
        with tarfile.open(helm_package_path, "r:gz") as tar:
            chart_files = [member for member in tar.getmembers() if member.isfile()]
            for chart_file in chart_files:
                if chart_file.name.endswith("Chart.yaml"):
                    chart_info = tar.extractfile(chart_file).read().decode("utf-8")
                    chart_data = yaml.safe_load(chart_info)

                    chart_name = chart_data.get("name")
                    chart_version = chart_data.get("version")
                    chart_description = chart_data.get("description")
                    chart_apiVersion = chart_data.get("apiVersion")
                    chart_appVersion = chart_data.get("appVersion")
                    chart_type = chart_data.get("type")
                    ok = ok + 1
                    append_new_line(
                        "logs.txt", f"{chart_file} data retrieved successfully'."
                    )
                if chart_file.name.endswith("values.yaml"):
                    values_info = tar.extractfile(chart_file).read().decode("utf-8")
                    values_data = yaml.safe_load(values_info)
                    namespace = values_data.get("namespace", namespace)
                    deployment_info = values_data.get("deployment", {})
                    service_info = values_data.get("service", {})

                    deployment_name = deployment_info.get("name", deployment_name)
                    imageName = deployment_info.get("imageName", imageName)
                    port = service_info.get("port", port)
                    append_new_line(
                        "logs.txt", f"All data retrieved successfully'."
                    )
                    ok = ok + 1
                if ok == 2:
                    release_inst = ReleaseObj(
                        chart_name,
                        chart_version,
                        imageName,
                        chart_description,
                        chart_apiVersion,
                        chart_appVersion,
                        chart_type,
                        installed,
                        port,
                        namespace
                    )
                    
                    return release_inst
    except Exception as e:
        exc_type, msg = e.args
        if exc_type == "warn":
            pass
        else:
            append_new_line("logs.txt", f"{msg}")
            raise e
        
def customize_release(pkg_path, releaseName, custom_port, ns_name):
    values_file_path = "values.yaml"
    new_pkg_path = f"{ns_name}.tgz"

    with tarfile.open(pkg_path, "r:gz") as tar:
        # Extract all files and folders from the package
        tar.extractall()

    # Update values.yaml
    values_yaml_path = os.path.join(releaseName, "values.yaml")
    with open(values_yaml_path, "r") as values_file:
        values_data = yaml.safe_load(values_file)

    values_data["namespace"] = ns_name

    deployment_info = values_data.get("deployment", {})
    deployment_info["name"] = f"{ns_name}-deployment"

    service_info = values_data.get("service", {})
    service_info["name"] = f"{ns_name}-service"
    service_info["port"] = custom_port
    service_info["selector"]["app"] = f"{ns_name}-deployment"

    values_data["deployment"] = deployment_info
    values_data["service"] = service_info

    with open(values_yaml_path, "w") as values_file:
        yaml.dump(values_data, values_file)
    
    chart_yaml_path = os.path.join(releaseName, "Chart.yaml")
    with open(chart_yaml_path, "r") as chart_file:
        chart_data = yaml.safe_load(chart_file)

    chart_data["namespace"] = ns_name

    with open(chart_yaml_path, "w") as chart_file:
        yaml.dump(chart_data, chart_file)
    # Create a new .tgz package with the updated values.yaml and other files

    with tarfile.open(new_pkg_path, "w:gz") as tar:
        tar.add(releaseName, arcname=os.path.basename(releaseName))


    # Remove the extracted files and folders
    shutil.rmtree(releaseName)

    return new_pkg_path

def add_release(releaseInst):
    try:
        append_new_line(
            "logs.txt", f"Inserting release data {releaseInst.get_name()}, {releaseInst.get_image_name()}, {releaseInst.is_installed()}'."
        )
        res = insert_release(releaseInst)
        append_new_line(
            "logs.txt", f"Release inserted successfully"
        )
        return res
    except Exception as e:
        raise e
    
def add_Jeopardy_exercise(name, flag, score, status, releaseInst):
    node_ip = kube_interaction_inst.kube_get_node_ip()
    port = releaseInst.get_port()
    fullUrl = f"{node_ip}:{port}"

    description = releaseInst.get_description()
    namespace = releaseInst.get_namespace()
    res = insert_jeopardyexercise(name, flag, score, status, fullUrl, description, namespace)
    return res

def add_Jeopardytorelease(ctfName, releaseName):
    try:
        id_jeopardy = get_jeopardy_id_where_name(ctfName)
        id_release = get_releaseid_where_releasename(releaseName)
        insert_jeopardytorelease(id_jeopardy, id_release, ctfName, releaseName)
        return True
    except Exception as e:
        append_new_line('logs.txt', f'Error: {e}')
        return False