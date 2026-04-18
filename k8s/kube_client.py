from kubernetes import client, config
from functools import lru_cache
import os


class KubeClient:
    def __init__(self):
        if os.getenv("KUBERNETES_SERVICE_HOST"):
            config.load_incluster_config()
        else:
            config.load_kube_config()

        self.core = client.CoreV1Api()
        self.apps = client.AppsV1Api()


@lru_cache(maxsize=1)
def get_kube_client() -> KubeClient:
    """Singleton Kubernetes client."""
    return KubeClient()
