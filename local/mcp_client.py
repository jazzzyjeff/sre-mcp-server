import asyncio
import json
from fastmcp import Client
from azure_devops.config import settings


async def main():
    async with Client("main.py") as client:
        # tools = await client.list_tools()
        # print("TOOLS:", tools)

        get_repositories = await client.call_tool(
            "get_repositories",
            {"project": settings.azure_devops_project},
        )
        print(get_repositories)

        get_environments = await client.call_tool(
            "get_environments",
            {"project": settings.azure_devops_project},
        )

        for env in json.loads(get_environments.content[0].text):
            deployments = await client.call_tool(
                "get_deployments",
                {
                    "project": settings.azure_devops_project,
                    "environment_id": env["id"],
                    "limit": 1,
                },
            )
            print(deployments)

        get_pipelines = await client.call_tool(
            "get_pipelines",
            {"project": settings.azure_devops_project},
        )

        for service in json.loads(get_pipelines.content[0].text):
            get_recent_builds = await client.call_tool(
                "get_recent_builds",
                {
                    "project": settings.azure_devops_project,
                    "pipeline_id": service["id"],
                    "limit": 1,
                },
            )

            for build in json.loads(get_recent_builds.content[0].text):
                failed_steps = await client.call_tool(
                    "get_failed_steps",
                    {"project": settings.azure_devops_project, "build_id": build["id"]},
                )

                if failed_steps.content:
                    raw_text = failed_steps.content[0].text
                    failed_steps = json.loads(raw_text)
                    for step in failed_steps:
                        log_id = step.get("log_id")
                        if not log_id:
                            continue

                        logs = await client.call_tool(
                            "get_log_by_id",
                            {
                                "project": settings.azure_devops_project,
                                "build_id": build["id"],
                                "log_id": log_id,
                            },
                        )

                        logs = logs.content[0].text
                        print(logs)


if __name__ == "__main__":
    asyncio.run(main())
