from typing import List, Callable
from k8s.client import get_kube_client
from k8s.models import Pod


def get_pods(namespace: str) -> List[Pod]:
    """List pods in a namespace."""
    kube = get_kube_client()
    pods = kube.core.list_namespaced_pod(namespace)

    return [
        Pod(
            name=p.metadata.name,
            namespace=p.metadata.namespace,
            status=p.status.phase,
            node=p.spec.node_name,
            restart_count=sum(
                c.restart_count for c in (p.status.container_statuses or [])
            ),
        )
        for p in pods.items
    ]


tools: List[Callable] = [
    get_pods
]


def register_tools(mcp):
    for tool in tools:
        mcp.tool()(tool)