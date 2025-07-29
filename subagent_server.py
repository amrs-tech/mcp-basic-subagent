# subagent_server.py
from fastmcp import FastMCP
from typing import Dict

# State: in-memory agent hierarchy
AGENT_TREE: Dict[str, dict] = {
    "root": {"id": "root", "name": "root", "parent": None, "config": {}, "children": []}
}
MAX_DEPTH = 2

def depth_of(agent_id: str) -> int:
    node = AGENT_TREE.get(agent_id)
    return 0 if not node or node["parent"] is None else 1 + depth_of(node["parent"])

# Instantiate MCP server
mcp = FastMCP("Subagent Server")

@mcp.tool()
def create_subagent(parent_agent_id: str, new_agent_id: str, config: dict) -> str:
    """
    Create a new sub-agent under a parent, enforcing max depth and no cycles.
    """
    if parent_agent_id not in AGENT_TREE:
        raise ValueError(f"Parent '{parent_agent_id}' not found.")
    if depth_of(parent_agent_id) >= MAX_DEPTH:
        raise ValueError(f"Max depth ({MAX_DEPTH}) exceeded at parent '{parent_agent_id}'.")
    if new_agent_id in AGENT_TREE:
        raise ValueError(f"Agent ID '{new_agent_id}' already exists.")
    # Register
    AGENT_TREE[new_agent_id] = {
        "id": new_agent_id,
        "name": config.get("name", new_agent_id),
        "parent": parent_agent_id,
        "config": config,
        "children": []
    }
    AGENT_TREE[parent_agent_id]["children"].append(new_agent_id)
    return f"Created sub-agent '{new_agent_id}' under '{parent_agent_id}'."

@mcp.tool()
def list_subagents(parent_agent_id: str = "root") -> dict:
    """List direct children of a given agent."""
    node = AGENT_TREE.get(parent_agent_id)
    if not node:
        raise ValueError(f"No such agent: '{parent_agent_id}'")
    return {"children": node["children"]}

@mcp.tool()
def run_subagent(agent_id: str, input: dict) -> dict:
    """
    Run the specified subagent with the given input.
    The behavior here is a simple echo; modify as needed.
    """
    agent = AGENT_TREE.get(agent_id)
    if not agent:
        raise ValueError(f"No such agent: '{agent_id}'")

    config = agent.get("config", {})
    behavior = config.get("behavior", "echo")  # default behavior

    # Example behavior: echo or uppercase
    if behavior == "echo":
        return {"output": f"[{agent_id}] Echo: {input.get('message', '')}"}
    elif behavior == "uppercase":
        return {"output": input.get("message", "").upper()}
    else:
        return {"output": f"[{agent_id}] Unknown behavior"}


if __name__ == "__main__":
    mcp.run()  # defaults to stdio transport
