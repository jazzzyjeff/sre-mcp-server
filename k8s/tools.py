from typing import List, Callable
from k8s.kube_client import get_kube_client
from k8s.models import Pod, Deployment, Event


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


def get_deployments(namespace: str) -> List[Deployment]:
    """List deployments and their rollout status in a namespace."""
    kube = get_kube_client()
    deployments = kube.apps.list_namespaced_deployment(namespace)
    return [
        Deployment(
            name=d.metadata.name,
            namespace=d.metadata.namespace,
            desired=d.spec.replicas or 0,
            ready=d.status.ready_replicas or 0,
            available=d.status.available_replicas or 0,
            image=d.spec.template.spec.containers[0].image,
        )
        for d in deployments.items
    ]


def get_unhealthy_pods(namespace: str) -> List[Pod]:
    """List pods that are not in Running or Succeeded state."""
    pods = get_pods(namespace)
    return [p for p in pods if p.status not in ("Running", "Succeeded")]


def get_events(namespace: str, warning_only: bool = True) -> List[Event]:
    """Get events for a namespace, optionally filtered to warnings only."""
    kube = get_kube_client()
    events = kube.core.list_namespaced_event(namespace)
    return [
        Event(
            namespace=e.metadata.namespace,
            name=e.involved_object.name,
            reason=e.reason,
            message=e.message,
            count=e.count or 0,
            first_time=str(e.first_timestamp) if e.first_timestamp else None,
            last_time=str(e.last_timestamp) if e.last_timestamp else None,
        )
        for e in events.items
        if not warning_only or e.type == "Warning"
    ]


def get_pod_logs(namespace: str, pod_name: str, tail: int = 100) -> str:
    """Get the last N lines of logs from a pod."""
    kube = get_kube_client()
    return kube.core.read_namespaced_pod_log(
        name=pod_name, namespace=namespace, tail_lines=tail
    )


tools: List[Callable] = [
    get_pods,
    get_deployments,
    get_unhealthy_pods,
    get_events,
    get_pod_logs,
]


def register_tools(mcp):
    for tool in tools:
        mcp.tool()(tool)
