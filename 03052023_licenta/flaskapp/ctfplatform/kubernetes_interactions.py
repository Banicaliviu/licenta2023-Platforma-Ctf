from kubernetes import client, config, utils
from ctfplatform.utils import append_new_line, get_sa_token
import os
import psycopg2
import subprocess
import json


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

    def kube_list_pods(self, namespace="default"):
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
            append_new_line(
                "kube-logs.txt", "Unable to retrieve the port number for Chartmuseum."
            )
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
