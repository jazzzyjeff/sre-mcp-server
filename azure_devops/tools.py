from azure.devops.v7_1.work_item_tracking.models import Wiql
from azure_devops.client import get_client
from azure_devops.models import Project, Build, Pipeline, WorkItem
from typing import Optional, List, Callable


def get_projects() -> list[Project]:
    """List all Azure DevOps projects in the organisation."""
    core_client = get_client().clients.get_core_client()
    projects = core_client.get_projects()
    return [{"id": p.id, "name": p.name, "state": p.state} for p in projects]


def get_work_items(
    project: str,
    work_item_type: str = "Bug",
    state: str = "Active",
    limit: int = 20,
) -> list[WorkItem]:
    """Query work items from a project by type and state."""
    wit_client = get_client().clients.get_work_item_tracking_client()

    wiql = Wiql(query=f"""
        SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo]
        FROM WorkItems
        WHERE [System.TeamProject] = '{project}'
        AND [System.WorkItemType] = '{work_item_type}'
        AND [System.State] = '{state}'
        ORDER BY [System.ChangedDate] DESC
    """)

    result = wit_client.query_by_wiql(wiql, top=limit)
    if not result.work_items:
        return []

    ids = [item.id for item in result.work_items]
    items = wit_client.get_work_items(ids, error_policy="omit")

    return [
        {
            "id": item.id,
            "title": item.fields.get("System.Title"),
            "state": item.fields.get("System.State"),
            "assigned_to": item.fields.get("System.AssignedTo", {}).get("displayName"),
            "url": item.url,
        }
        for item in items
    ]


def get_pipelines(project: str) -> list[Pipeline]:
    """List build pipelines for a project."""
    build_client = get_client().clients.get_build_client()
    pipelines = build_client.get_definitions(project=project)
    return [{"id": p.id, "name": p.name, "path": p.path} for p in pipelines]


def get_recent_builds(
    project: str, pipeline_id: Optional[int] = None, limit: int = 10
) -> list[Build]:
    """Get recent build runs, optionally filtered by pipeline."""
    build_client = get_client().clients.get_build_client()
    builds = build_client.get_builds(
        project=project,
        definitions=[pipeline_id] if pipeline_id else None,
        top=limit,
    )
    return [
        {
            "id": b.id,
            "pipeline": b.definition.name,
            "status": b.status,
            "result": b.result,
            "requested_by": b.requested_by.display_name,
            "start_time": str(b.start_time),
            "finish_time": str(b.finish_time),
        }
        for b in builds
    ]


def get_build(project: str, build_id: str):
    build_client = get_client().clients.get_build_client()
    b = build_client.get_build(project, build_id)

    return {
        "id": b.id,
        "pipeline": b.definition.name,
        "status": b.status,
        "result": b.result,
    }


def get_build_logs(project: str, build_id: int) -> str:
    """Get logs for a build."""
    build_client = get_client().clients.get_build_client()
    logs = build_client.get_build_logs(project, build_id)

    output = []
    for log in logs:
        stream = build_client.get_build_log(project, build_id, log.id)
        content = b"".join(stream).decode("utf-8", errors="ignore")
        output.append(f"\n--- LOG {log.id} ---\n{content}")

    return "\n".join(output)


def get_failed_steps(project: str, build_id: int):
    """Get failed steps from a build."""
    build_client = get_client().clients.get_build_client()
    timeline = build_client.get_build_timeline(project, build_id)

    failed = []
    for record in timeline.records:
        if record.result == "failed":
            failed.append(
                {
                    "id": record.id,
                    "name": record.name,
                    "type": record.type,
                    "log_id": record.log.id if record.log else None,
                }
            )

    return failed


def get_log_by_id(project: str, build_id: int, log_id: int) -> str:
    """Get specific log by ID."""
    build_client = get_client().clients.get_build_client()
    stream = build_client.get_build_log(project, build_id, log_id)
    content = b"".join(stream).decode("utf-8", errors="ignore")
    return content[:5000]


tools: List[Callable] = [
    get_projects,
    get_work_items,
    get_pipelines,
    get_recent_builds,
    get_build,
    get_build_logs,
    get_failed_steps,
    get_log_by_id,
]


def register_tools(mcp):
    for tool in tools:
        mcp.tool()(tool)
