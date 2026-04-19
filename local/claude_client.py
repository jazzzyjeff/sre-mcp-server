"""Claude client for local SRE MCP testing."""

import asyncio
from anthropic import AsyncAnthropic
from anthropic.types import MessageParam, ToolParam, ToolResultBlockParam
from fastmcp import Client
from local.config import settings

SYSTEM_PROMPT = """
You are an SRE assistant.

STRICT RULES:
- Return only the data requested, no commentary.
- Do not ask follow-up questions.
- Do not explain or summarise.
- If no results: return exactly "No data"
- Always use tools when data is required, never guess.
"""

anthropic = AsyncAnthropic(api_key=settings.anthropic_api_key)


async def run_query(query: str):
    """Claude client entry point."""
    async with Client("main.py") as mcp_client:
        mcp_tools = await mcp_client.list_tools()
        anthropic_tools: list[ToolParam] = [
            {
                "name": t.name,
                "description": t.description or "",
                "input_schema": t.inputSchema,
            }
            for t in mcp_tools
        ]

        messages: list[MessageParam] = [{"role": "user", "content": query}]

        while True:
            response = await anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=anthropic_tools,
                messages=messages,
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text"):
                        print(block.text)
                break

            if response.stop_reason == "tool_use":
                tool_results: list[ToolResultBlockParam] = []
                for block in response.content:
                    if block.type != "tool_use":
                        continue

                    print(f"[tool] {block.name}({block.input})")
                    result = await mcp_client.call_tool(block.name, block.input)
                    content = result.content[0].text if result.content else "No data"
                    tool_results.append(
                        ToolResultBlockParam(
                            type="tool_result",
                            tool_use_id=block.id,
                            content=content,
                        )
                    )

                messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    asyncio.run(run_query("What pods do I have in the default namespace?"))
