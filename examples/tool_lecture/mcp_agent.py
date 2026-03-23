
import asyncio
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from util.models import get_model
from util.streaming_utils import STREAM_MODES, handle_stream_async
from util.pretty_print import print_mcp_tools, get_user_input


async def run_async():
    # Get predefined attributes
    model = get_model()

    # Create MCP client
    mcp_client = MultiServerMCPClient({
        "math_server": {
            "transport": "streamable_http",
            "url": "http://localhost:8001/mcp",
        },
        "weather": {
            "transport": "streamable_http",
            "url": "http://127.0.0.1:8002/mcp"
        }
    })

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
