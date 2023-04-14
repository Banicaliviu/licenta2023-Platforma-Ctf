from kubernetes import client, config, utils
from ctfplatform.utils import append_new_line

class kubernetes_interaction:
    def __init__(self):
          #config.load_incluster_config()
          pass

#da token pe None daca nu-ti trebuie    
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

    

