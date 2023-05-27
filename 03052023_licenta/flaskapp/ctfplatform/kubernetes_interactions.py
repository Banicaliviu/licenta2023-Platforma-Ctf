from kubernetes import client, config, utils
from ctfplatform.utils import append_new_line, get_sa_token
import os
import psycopg2

class kubernetes_interaction:
    def __init__(self):
          pass
      
    def __init__(self, token):
        # config = client.Configuration()
        # config.host = "https://192.168.49.2:8443"
        
        # config.api_key = {"authorization": "Bearer " + token}  
        config.load_incluster_config()  
        config.verify_ssl = False 
        #self.apiClient = client.ApiClient(config)
        self.apiClient = client.ApiClient()
        
    def kube_list_pods(self, namespace='default'):
        apiInstance = client.CoreV1Api(self.apiClient)
        append_new_line("kube-logs.txt", "Listing pods in ctfspace namespace...")
        pods = apiInstance.list_namespaced_pod(namespace="ctfspace", watch=False)
        for pod in pods.items:
            append_new_line("kube-logs.txt", "{}----{}----{}".format(pod.status.pod_ip, pod.metadata.namespace, pod.metadata.name))
        append_new_line("kube-logs.txt", "Pods listed !\n")
        #statusul podului poate fi accesat prin pod.status.phase si poate fii : Running sau Error
        return pods
    
    def kube_list_pods(self, namespace):
        apiInstance = client.CoreV1Api(self.apiClient)
        append_new_line("kube-logs.txt", "Listing pods in {} namespace...".format(namespace))
        pods = apiInstance.list_namespaced_pod(namespace=namespace, watch=False)
        for pod in pods.items:
            append_new_line("kube-logs.txt", "{}----{}----{}".format(pod.status.pod_ip, pod.metadata.namespace, pod.metadata.name))
        append_new_line("kube-logs.txt", "Pods listed !\n")
        #statusul podului poate fi accesat prin pod.status.phase si poate fii : Running sau Error
        return pods
    
    def kube_list_namespaces(self):
        api_instance = client.CoreV1Api(self.apiClient)
        append_new_line("kube-logs.txt", "Listing namespaces...")
        namespaces = api_instance.list_namespace()
        namespace_list = [ns.metadata.name for ns in namespaces.items if not ns.metadata.name.startswith("kube-")]
        append_new_line("kube-logs.txt", "Namespaces listed !\n")
        return namespace_list

    
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
