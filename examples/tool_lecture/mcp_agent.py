
import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents.middleware import wrap_tool_call

from util.models import get_model
from util.streaming_utils import STREAM_MODES, handle_stream_async
from util.pretty_print import print_mcp_tools, get_user_input

@wrap_tool_call
async def simplify_tool_output(request, handler):
    result = await handler(request)

    if isinstance(result, dict):
        if "priority" in result:
            return (
                f"Uppgift: {result.get('task_name')}, "
                f"prioritet: {result.get['priority']}, "
                f"score: {result.get('score')}"
            )
        
        if "sessions_needed" in result:
            return (
                f"Antal studiesessioner som behövs: "
                f"{result.get('sessions_needed')}"
            )
        if "warning" in result:
            return f"Riskbedömning: {result.get('warning')}"
    return result 

async def run_async():
    # Get predefined attributes
    model = get_model()

    # Create MCP client
    mcp_client = MultiServerMCPClient(
        {
            "study_tools": {
                "transport": "streamable_http",
                "url": "http://localhost:8003/mcp",
        }
    }
)

    # Get tools from MCP client
    tools = await mcp_client.get_tools()

    allowed_tool_names = {
        "prioritize_task",
        "estimate_study_sessions"
        "risk_check_deadline"
    }
    filtered_tools = [tool for tool in tools if tool.name in allowed_tool_names]
    print_mcp_tools(filtered_tools)

    # Create agent
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=(
            "Du är en hjälpsam assistent som svarar på användarens frågor. "
            "Svara alltid på svenska och var koncis men informativ."
        ),
    )

    # Get user input
    user_input = get_user_input("Ställ din fråga")

    # Call the agent
    process_stream = agent.astream(
        {"messages": [{"role": "user", "content": user_input}]},
        stream_mode=STREAM_MODES,
    )

    # Stream the process
    await handle_stream_async(process_stream)


def run():
    asyncio.run(run_async())


if __name__ == "__main__":
    run()
