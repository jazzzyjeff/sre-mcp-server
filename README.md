- [sre-mcp-server](#sre-mcp-server)
  - [What it does](#what-it-does)
  - [Project structure](#project-structure)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
  - [Running the MCP server](#running-the-mcp-server)
  - [Connecting to Claude desktop](#connecting-to-claude-desktop)
  - [Inspecting with the MCP inspector](#inspecting-with-the-mcp-inspector)
  - [Local development](#local-development)
    - [Raw tool calls — no Claude, no token cost](#raw-tool-calls--no-claude-no-token-cost)
    - [Claude-driven — agentic loop with tool use](#claude-driven--agentic-loop-with-tool-use)
  - [Adding new tools](#adding-new-tools)
  - [Adding a new module (e.g. PagerDuty)](#adding-a-new-module-eg-pagerduty)
  - [Linting and type checking](#linting-and-type-checking)

# sre-mcp-server

An MCP (Model Context Protocol) server for SRE workflows, connecting Claude to Azure DevOps and Kubernetes so you can triage incidents, inspect pipelines, and query infrastructure through natural language.

Built with [FastMCP](https://github.com/jlowin/fastmcp), the [Azure DevOps Python SDK](https://github.com/microsoft/azure-devops-python-api), and the [Kubernetes Python client](https://github.com/kubernetes-client/python).

## What it does

Claude can call tools across your infrastructure directly from a conversation:

**Azure DevOps**
- List projects, repositories, and pipelines
- Get recent builds and failed steps
- Fetch build logs by ID
- List environments and deployments

**Kubernetes**
- List pods and their status in a namespace
- List deployments and rollout health
- Surface unhealthy pods
- Get warning events
- Tail pod logs

**Example workflows**
- *"What pods are unhealthy in the prod namespace?"* → `get_unhealthy_pods`
- *"Show me the last deployment to the prod environment"* → `get_environments` → `get_deployments`
- *"Which pipelines failed today and why?"* → `get_recent_builds` → `get_failed_steps` → `get_log_by_id`


## Project structure

```
sre-mcp-server/
├── server.py                   # MCP server entry point
├── pyproject.toml
├── .env                      # secrets (not committed)
├── .env.example
├── azure_devops/
│   ├── client.py             # Azure DevOps connection singleton
│   ├── config.py             # Pydantic settings
│   ├── models.py             # Pydantic models
│   └── tools.py              # MCP tool definitions
├── k8s/
│   ├── kube_client.py        # Kubernetes connection singleton
│   ├── models.py             # Pydantic models
│   └── tools.py              # MCP tool definitions
└── local/
    ├── claude_client.py      # Claude-driven agentic client (local testing)
    └── mcp_client.py         # Raw tool calls without Claude (local testing)
```

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Azure DevOps organisation with a Personal Access Token
- Kubernetes cluster with a valid kubeconfig (or in-cluster config)
- Anthropic API key (for local Claude testing only)


## Setup

**1. Clone the repo**
```bash
git clone https://github.com/jazzzyjeff/sre-mcp-server
cd sre-mcp-server
```

**2. Install dependencies**
```bash
uv sync
```

**3. Configure environment**
```bash
cp .env.example .env
```

Edit `.env`:
```env
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/your-org
AZURE_DEVOPS_PAT=your-personal-access-token
AZURE_DEVOPS_PROJECT=your-default-project
ANTHROPIC_API_KEY=sk-ant-...
```

## Running the MCP server

```bash
uv run server.py
```

## Connecting to Claude desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sre-mcp-server": {
      "command": "uv",
      "args": ["--directory", "/path/to/sre-mcp-server", "run", "server.py"]
    }
  }
}
```

Restart Claude desktop. You should see the tools available in the toolbar.


## Inspecting with the MCP inspector

```bash
npx @modelcontextprotocol/inspector uv run server.py
```

Opens a browser UI where you can list and call tools manually — useful for verifying tool registration before connecting to Claude.

## Local development

The `local/` folder contains two scripts for testing without Claude desktop.

### Raw tool calls — no Claude, no token cost

Use this when building or debugging a new tool:

```bash
uv run local/mcp_client.py
```

Calls tools directly against the MCP server and prints raw responses. Fast and deterministic.

### Claude-driven — agentic loop with tool use

Use this to test how Claude actually interprets and uses the tools:

```bash
uv run local/claude_client.py
```

Sends a query to Claude, which decides which tools to call, executes them via the MCP client, and returns a response. Prints each tool call so you can see what Claude is doing:

```
[tool] get_environments({'project': 'my-project'})
[tool] get_deployments({'project': 'my-project', 'environment_id': 2, 'limit': 1})
[tokens] input=1842 output=64 total=1906
```

To change the query, edit the last line of `local/claude_client.py`:

```python
asyncio.run(run_query("What pods do I have in the default namespace?"))
```

## Adding new tools

**1. Define the function in the relevant `tools.py`:**
```python
def get_something(project: str) -> list[MyModel]:
    """One line description — this becomes the tool description Claude sees."""
    client = get_client()
    ...
```

**2. Register it:**
```python
tools: list[Callable] = [
    get_something,
    # existing tools...
]
```

**3. Add a Pydantic model in `models.py` if needed:**
```python
class MyModel(BaseModel):
    """My model."""
    id: int
    name: str
```

**4. Test with the inspector or `local/mcp_client.py` before connecting to Claude.**


## Adding a new module (e.g. PagerDuty)

```
pagerduty/
├── client.py
├── config.py
├── models.py
└── tools.py
```

Register in `main.py`:
```python
from pagerduty.tools import register_tools as pagerduty_tools
pagerduty_tools(mcp)
```

## Linting and type checking

```bash
uv run pylint .
uv run mypy .
```

Config lives in `pyproject.toml`.
