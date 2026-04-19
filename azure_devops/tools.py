"""Azure DevOps MCP tool definitions."""

from typing import Optional, List, Callable
from azure.devops.v7_1.work_item_tracking.models import Wiql
from azure_devops.client import get_client
from azure_devops.models import (
    Project,
    Build,
    Pipeline,
    WorkItem,
    FailedStep,
    Repository,
    Environment,
    Deployment,
)


def get_projects() -> List[Project]:
    """List all Azure DevOps projects in the organisation."""
    core_client = get_client().clients.get_core_client()
    projects = core_client.get_projects()
    return [Project(id=p.id, name=p.name, state=p.state) for p in projects]


def get_work_items(
    project: str,
    work_item_type: str = "Bug",
    state: str = "Active",
    limit: int = 20,
) -> List[WorkItem]:
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
        WorkItem(
            id=item.id,
            title=item.fields.get("System.Title"),
            state=item.fields.get("System.State"),
            assigned_to=item.fields.get("System.AssignedTo", {}).get("displayName"),
            url=item.url,
        )
        for item in items
    ]


def get_pipelines(project: str) -> List[Pipeline]:
    """List build pipelines for a project."""
    build_client = get_client().clients.get_build_client()
    pipelines = build_client.get_definitions(project=project)
    return [Pipeline(id=p.id, name=p.name, path=p.path) for p in pipelines]


def get_recent_builds(
    project: str, pipeline_id: Optional[int] = None, limit: int = 10
) -> List[Build]:
    """Get recent build runs, optionally filtered by pipeline."""
    build_client = get_client().clients.get_build_client()
    builds = build_client.get_builds(
        project=project,
        definitions=[pipeline_id] if pipeline_id else None,
        top=limit,
    )

    return [
        Build(
            id=b.id,
            pipeline=b.definition.name,
            status=b.status,
            result=b.result,
            requested_by=b.requested_by.display_name,
            start_time=str(b.start_time),
            finish_time=str(b.finish_time),
        )
        for b in builds
    ]


def get_build(project: str, build_id: str) -> Build:
    """Gets a build for a project."""
    build_client = get_client().clients.get_build_client()
    b = build_client.get_build(project, build_id)

    return Build(
        id=b.id,
        pipeline=b.definition.name,
        status=b.status,
        result=b.result,
        requested_by=b.requested_by.display_name,
    )


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


def get_failed_steps(project: str, build_id: int) -> List[FailedStep]:
    """Get failed steps from a build."""
    build_client = get_client().clients.get_build_client()
    timeline = build_client.get_build_timeline(project, build_id)

    failed = []
    for record in timeline.records:
        if record.result == "failed":
            failed.append(
                FailedStep(
                    id=record.id,
                    name=record.name,
                    type=record.type,
                    log_id=record.log.id if record.log else None,
                )
            )

    return failed


def get_log_by_id(project: str, build_id: int, log_id: int) -> str:
    """Get specific log by ID."""
    build_client = get_client().clients.get_build_client()
    stream = build_client.get_build_log(project, build_id, log_id)
    content = b"".join(stream).decode("utf-8", errors="ignore")
    return content[:5000]


def get_repositories(project: str) -> List[Repository]:
    """Get all git repositories within a project."""
    git_client = get_client().clients.get_git_client()
    repos = git_client.get_repositories(project)

    return [
        Repository(
            id=r.id,
            name=r.name,
            default_branch=r.default_branch,
        )
        for r in repos
    ]


def get_environments(project: str) -> List[Environment]:
    """Get all environments within a project."""
    task_client = get_client().clients.get_task_agent_client()
    envs = task_client.get_environments(project=project)

    return [
        Environment(
            id=e.id,
            name=e.name,
        )
        for e in envs
    ]


def get_deployments(
    project: str, environment_id: int, limit: int = 20
) -> List[Deployment]:
    """Get all deployments made within environment."""
    task_client = get_client().clients.get_task_agent_client()
    records = task_client.get_environment_deployment_execution_records(
        project=project, environment_id=environment_id, top=limit
    )

    seen = set()
    deployments = []

    for r in records:
        if r.owner.id in seen:
            continue
        seen.add(r.owner.id)
        deployments.append(
            Deployment(
                pipeline=r.definition.name,
                run_id=r.owner.id,
                run_name=r.owner.name,
                result=r.result,
            )
        )

    return sorted(deployments, key=lambda x: x.run_id, reverse=True)


tools: List[Callable] = [
    get_projects,
    get_work_items,
    get_pipelines,
    get_recent_builds,
    get_build,
    get_build_logs,
    get_failed_steps,
    get_log_by_id,
    get_repositories,
    get_environments,
    get_deployments,
]


def register_tools(mcp):
    """Register all k8s tools with the MCP server."""
    for tool in tools:
        mcp.tool()(tool)
