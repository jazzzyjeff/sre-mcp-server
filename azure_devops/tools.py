from azure.devops.v7_1.work_item_tracking.models import Wiql
from azure_devops.client import get_client
from azure_devops.models import Project, Build, Pipeline, WorkItem
from typing import Optional

def register_tools(mcp):
    @mcp.tool()
    def get_projects() -> list[Project]:
        """List all Azure DevOps projects in the organisation."""
        core_client = get_client().clients.get_core_client()
        projects = core_client.get_projects()
        return [{"id": p.id, "name": p.name, "state": p.state} for p in projects]

    @mcp.tool()
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
                "assigned_to": item.fields.get("System.AssignedTo", {}).get(
                    "displayName"
                ),
                "url": item.url,
            }
            for item in items
        ]

    @mcp.tool()
    def get_pipelines(project: str) -> list[Pipeline]:
        """List build pipelines for a project."""
        build_client = get_client().clients.get_build_client()
        pipelines = build_client.get_definitions(project=project)
        return [{"id": p.id, "name": p.name, "path": p.path} for p in pipelines]

    @mcp.tool()
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
