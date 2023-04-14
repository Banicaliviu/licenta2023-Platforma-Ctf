from kubernetes import client, config, utils
from ctfplatform.utils import append_new_line, get_sa_token
import os
import psycopg2

class kubernetes_interaction:
    def __init__(self):
          pass
      
    def __init__(self, token):
        config = client.Configuration()
        config.host = "https://192.168.49.2:8443"
        config.verify_ssl = False
        config.api_key = {"authorization": "Bearer " + token}     
        self.apiClient = client.ApiClient(config)
        
    def kube_list_pods(self):
        apiInstance = client.CoreV1Api(self.apiClient)
        append_new_line("kube-logs.txt", "Listing pods...")
        pods = apiInstance.list_pod_for_all_namespaces(watch=False)
        for pod in pods.items:
            append_new_line("kube-logs.txt", "{}----{}----{}".format(pod.status.pod_ip, pod.metadata.namespace, pod.metadata.name))
        append_new_line("kube-logs.txt", "Pods listed !\n")

    def kube_get_db(self):
        api_instance = client.CoreV1Api(self.apiClient)
        append_new_line("kube-logs.txt", "Requesting database ip...")
        label_selector = "app=postgres"
        namespace_selector = "ctfspace"

        pods = api_instance.list_namespaced_pod(namespace=namespace_selector, label_selector=label_selector)
        if not pods.items:
            append_new_line("kube-logs.txt", "No PostgreSQL pods found in ctfspace namespace.")
            return

        pod = pods.items[0]
        db_ip = pod.status.pod_ip
        append_new_line("kube-logs.txt", "Database IP is: {}".format(db_ip))
        append_new_line("kube-logs.txt", "Database IP retrieved!\n")
        return db_ip

kube_interaction_inst = kubernetes_interaction(get_sa_token())

def get_db_connection():
    conn = psycopg2.connect(
        host=kube_interaction_inst.kube_get_db(),
        port=5432,
        database=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"])

    return conn
