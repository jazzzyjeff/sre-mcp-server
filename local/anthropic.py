import asyncio
from local.anthropic import AsyncAnthropic
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

client = AsyncAnthropic(
    api_key=settings.anthropic_api_key,
)


async def run_query(query: str):
    async with Client("server.py") as mcp_client:

        mcp_tools = await mcp_client.list_tools()
        anthropic_tools = [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.inputSchema,
            }
            for t in mcp_tools
        ]

        messages = [{"role": "user", "content": query}]

        while True:
            response = await client.messages.create(
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
                tool_results = []

                for block in response.content:
                    if block.type != "tool_use":
                        continue

                    print(f"[tool] {block.name}({block.input})")

                    result = await mcp_client.call_tool(block.name, block.input)
                    content = result.content[0].text if result.content else "No data"

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": content,
                        }
                    )

                messages.append({"role": "user", "content": tool_results})


async def main():
    await run_query("What pods do I have in the default namespace?")


if __name__ == "__main__":
    asyncio.run(main())
