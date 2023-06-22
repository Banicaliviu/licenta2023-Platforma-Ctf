from kubernetes import client, config, utils
from ctfplatform.utils import append_new_line, get_sa_token
import os
import psycopg2
import subprocess
import json
import yaml


class kubernetes_interaction:
    def __init__(self):
        pass

    def __init__(self, token):
        # config = client.Configuration()
        # config.host = "https://192.168.49.2:8443"

        # config.api_key = {"authorization": "Bearer " + token}
        config.load_incluster_config()
        config.verify_ssl = False
        # self.apiClient = client.ApiClient(config)
        self.apiClient = client.ApiClient()

    def kube_apply_directory(self, directory):
        try:
            namespace_file = None
            other_files = []

            for filename in os.listdir(directory):
                if filename.endswith(".yaml") or filename.endswith(".yml"):
                    file_path = os.path.join(directory, filename)

                    if filename.lower().endswith("namespace.yaml"):
                        namespace_file = file_path
                    elif filename.lower().endswith("secret.yaml"):
                        secret_file = file_path
                    else:
                        other_files.append(file_path)

            if namespace_file:
                utils.create_from_yaml(self.apiClient, namespace_file)
                append_new_line(
                    "logs.txt",
                    f"Successfully applied file {namespace_file} to Kubernetes cluster",
                )
            if secret_file:
                utils.create_from_yaml(self.apiClient, secret_file)
                append_new_line(
                    "logs.txt",
                    f"Successfully applied file {secret_file} to Kubernetes cluster",
                )
            for file_path in other_files:
                utils.create_from_yaml(self.apiClient, file_path)
                append_new_line(
                    "logs.txt",
                    f"Successfully applied file {file_path} to Kubernetes cluster",
                )

            return True
        except Exception as e:
            append_new_line(
                "logs.txt",
                f"Error applying files in directory {directory} to Kubernetes cluster: {e}",
            )
            return False

    def kube_delete_file(self, file):
        try:
            k8s_client = self.apiClient()
            with open(file, "r") as f:
                body = yaml.safe_load(f)
                self.apiClient.delete_namespaced_pod(
                    body["metadata"]["name"], "ctfspace"
                )
            append_new_line(
                "logs.txt", f"Successfully deleted file {file} from Kubernetes cluster"
            )
            return True
        except Exception as e:
            append_new_line(
                "logs.txt", f"Error deleting file {file} from Kubernetes cluster: {e}"
            )
            return False

    def kube_list_pods(self):
        apiInstance = client.CoreV1Api(self.apiClient)
        append_new_line("kube-logs.txt", "Listing pods in ctfspace namespace...")
        pods = apiInstance.list_namespaced_pod(namespace="ctfspace", watch=False)
        for pod in pods.items:
            append_new_line(
                "kube-logs.txt",
                "{}----{}----{}".format(
                    pod.status.pod_ip, pod.metadata.namespace, pod.metadata.name
                ),
            )
        append_new_line("kube-logs.txt", "Pods listed !\n")
        # statusul podului poate fi accesat prin pod.status.phase si poate fii : Running sau Error
        return pods

    def kube_list_pods(self, namespace):
        apiInstance = client.CoreV1Api(self.apiClient)
        append_new_line(
            "kube-logs.txt", "Listing pods in {} namespace...".format(namespace)
        )
        pods = apiInstance.list_namespaced_pod(namespace=namespace, watch=False)
        for pod in pods.items:
            append_new_line(
                "kube-logs.txt",
                "{}----{}----{}".format(
                    pod.status.pod_ip, pod.metadata.namespace, pod.metadata.name
                ),
            )
        append_new_line("kube-logs.txt", "Pods listed !\n")
        # statusul podului poate fi accesat prin pod.status.phase si poate fii : Running sau Error
        return pods

    def kube_list_namespaces(self):
        api_instance = client.CoreV1Api(self.apiClient)
        append_new_line("kube-logs.txt", "Listing namespaces...")
        namespaces = api_instance.list_namespace()
        namespace_list = [
            ns.metadata.name
            for ns in namespaces.items
            if not ns.metadata.name.startswith("kube-")
        ]
        append_new_line("kube-logs.txt", "Namespaces listed !\n")
        return namespace_list

    def kube_list_deployments(self, name, namespace):
        try:
            api_instance = client.AppsV1Api(self.apiClient)
            append_new_line(
                "kube-logs.txt",
                f"Listing deployments in {namespace} namespace with name {name}...",
            )
            deployments = api_instance.list_namespaced_deployment(namespace=namespace)
            deployment_info = []

            for deployment in deployments.items:
                if deployment.metadata.name == name:
                    deployment_info.append(
                        {
                            "name": deployment.metadata.name,
                            "namespace": deployment.metadata.namespace,
                            "replicas": deployment.spec.replicas,
                            "status": deployment.status,
                        }
                    )

                append_new_line(
                    "kube-logs.txt",
                    "{}----{}----{}".format(
                        deployment.spec.replicas,
                        deployment.metadata.namespace,
                        deployment.metadata.name,
                    ),
                )

            append_new_line("kube-logs.txt", "Deployments listed!\n")

            return deployment_info
        except Exception as e:
            raise e

    def kube_list_services(self, name, namespace):
        try:
            api_instance = client.CoreV1Api(self.apiClient)
            append_new_line(
                "kube-logs.txt",
                f"Listing services in {namespace} namespace with name {name}...",
            )
            services = api_instance.list_namespaced_service(namespace=namespace)
            service_info = []

            for service in services.items:
                if service.metadata.name == name:
                    service_info.append(
                        {
                            "name": service.metadata.name,
                            "type": service.spec.type,
                            "port": service.spec.ports[0].port,
                            "nodePort": service.spec.ports[0].node_port,
                        }
                    )

                append_new_line(
                    "kube-logs.txt",
                    "{}----{}----{}----{}".format(
                        service.metadata.name,
                        service.spec.type,
                        service.spec.ports[0].port,
                        service.spec.ports[0].node_port,
                    ),
                )

            append_new_line("kube-logs.txt", "Services listed!\n")

            return service_info
        except Exception as e:
            raise e

    def kube_get_db(self):
        api_instance = client.CoreV1Api(self.apiClient)
        append_new_line("kube-logs.txt", "Requesting database ip...")
        label_selector = "app=postgres"
        namespace_selector = "ctfspace"

        pods = api_instance.list_namespaced_pod(
            namespace=namespace_selector, label_selector=label_selector
        )
        if not pods.items:
            append_new_line(
                "kube-logs.txt", "No PostgreSQL pods found in ctfspace namespace."
            )
            return

        pod = pods.items[0]
        db_ip = pod.status.pod_ip
        append_new_line("kube-logs.txt", "Database IP is: {}".format(db_ip))
        append_new_line("kube-logs.txt", "Database IP retrieved!\n")
        return db_ip

    def kube_get_node_ip(self):
        api_instance = client.CoreV1Api(self.apiClient)
        append_new_line("kube-logs.txt", "Requesting node IP...")
        node_info = api_instance.list_node()
        if not node_info.items:
            append_new_line("kube-logs.txt", "No nodes found in the cluster.")
            return

        node_ip = node_info.items[0].status.addresses[0].address
        append_new_line("kube-logs.txt", "Node IP is: {}".format(node_ip))
        append_new_line("kube-logs.txt", "Node IP retrieved!\n")
        return node_ip

    def kube_get_chartmuseum(self):
        api_instance = client.CoreV1Api(self.apiClient)
        append_new_line("kube-logs.txt", "Requesting chartmuseum ip...")
        label_selector = "app=chartmuseum"
        namespace_selector = "ctfspace"

        pods = api_instance.list_namespaced_pod(
            namespace=namespace_selector, label_selector=label_selector
        )
        if not pods.items:
            append_new_line(
                "kube-logs.txt", "No chartmuseum pods found in ctfspace namespace."
            )
            return

        pod = pods.items[0]
        cm_ip = pod.status.pod_ip

        port_number = None
        if pod.spec.containers:
            container_ports = pod.spec.containers[0].ports
            if container_ports:
                port_number = container_ports[0].container_port

        if port_number is None:
            append_new_line("kube-logs.txt", "Unable to retrieve port for Chartmuseum.")
            return

        cm_url = f"http://{cm_ip}:{port_number}"
        append_new_line("kube-logs.txt", "Chartmuseum URL is: {}".format(cm_url))
        append_new_line("kube-logs.txt", "Chartmuseum URL retrieved!\n")
        return cm_url

    def kube_add_chartmuseum_repository(self, cm_url):
        try:
            repo_name = "ctfplatform-chartmuseum"
            repo_command = ["helm", "repo", "list", "-o", "json"]
            result = subprocess.run(repo_command, capture_output=True, text=True)
            if result.returncode == 0:
                repo_list = json.loads(result.stdout)
                for repo in repo_list:
                    if repo["name"] == repo_name:
                        append_new_line(
                            "logs.txt", f"Repository '{repo_name}' already exists"
                        )
                        return True

            add_repo_command = ["helm", "repo", "add", repo_name, cm_url]
            subprocess.run(add_repo_command, check=True)
            append_new_line("logs.txt", f"Repository '{repo_name}' added successfully")
            return 1
        except subprocess.CalledProcessError as e:
            append_new_line(
                "logs.txt", f"Failed to add repository '{repo_name}': {e.stderr}"
            )
            return 0
        except Exception as e:
            append_new_line("logs.txt", f"Repository addition failed: {str(e)}")
            return 0

    def kube_get_docker_registry(self):
        api_instance = client.CoreV1Api(self.apiClient)
        append_new_line("kube-logs.txt", "Requesting docker registry ip...")
        label_selector = "app=docker-registry"
        namespace_selector = "ctfspace"

        pods = api_instance.list_namespaced_pod(
            namespace=namespace_selector, label_selector=label_selector
        )
        if not pods.items:
            append_new_line(
                "kube-logs.txt",
                f"No docker-registry pod found in {namespace_selector} namespace.",
            )
            return

        pod = pods.items[0]
        dr_ip = pod.status.pod_ip

        port_number = None
        if pod.spec.containers:
            container_ports = pod.spec.containers[0].ports
            if container_ports:
                port_number = container_ports[0].container_port

        if port_number is None:
            append_new_line(
                "kube-logs.txt", "Unable to retrieve port for docker-registry."
            )
            return

        dr_url = f"{dr_ip}:{port_number}"
        append_new_line("kube-logs.txt", "Docker-registry URL is: {}".format(dr_url))
        append_new_line("kube-logs.txt", "Docker-registry URL retrieved!\n")
        return dr_url


kube_interaction_inst = kubernetes_interaction(get_sa_token())


def get_db_connection():
    conn = psycopg2.connect(
        host=kube_interaction_inst.kube_get_db(),
        port=5432,
        database=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )

    return conn
