import asyncio
import json
from fastmcp import Client
from azure_devops.config import settings

async def main():
    async with Client("main.py") as client:
        # tools = await client.list_tools()
        # print("TOOLS:", tools)

        failed_steps = await client.call_tool(
            "get_failed_steps",
            { 
                "project": settings.azure_devops_project, 
                "build_id": 504 
            }
        )

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
                    "build_id": 504,
                    "log_id": log_id
                }
            )

            logs = logs.content[0].text
            print(logs)

if __name__ == "__main__":
    asyncio.run(main())