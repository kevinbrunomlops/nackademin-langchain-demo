
import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents.middleware import wrap_tool_call

from util.models import get_model
from util.pretty_print import get_user_input

@wrap_tool_call
async def simplify_tool_output(request, handler):
    result = await handler(request)

    if isinstance(result, dict):
        if "priority" in result:
            return (
                f"Uppgift: {result.get('task_name')}. "
                f"Prioritet: {result.get('priority')}. "
                f"Poäng: {result.get('score')}. "
            )
        
        if "sessions_needed" in result:
            return (
                f"Uppgift: {result.get('task_name')}. "
                f"Behöver ungefär {result.get('sessions_needed')} studiesessioner."
            )
        if "risk_level" in result:
            return (
                f"Uppgift: {result.get('task_name')}. "
                f"Risknivå: {result.get('risk_level')}. "
                f"Kommentar: {result.get('warning')}"
                )
        
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
        "estimate_study_sessions",
        "risk_check_deadline",
    }
    filtered_tools = [tool for tool in tools if tool.name in allowed_tool_names]
    

    # Create agent
    agent = create_agent(
        model=model,
        tools=filtered_tools,
        middleware=[simplify_tool_output],
        system_prompt=""" 
            Du är en studieassistent som hjälper användaren att planera studier och uppgifter. 
            
            Regler: 
            - Vid allmäna frågor som "Hur kan du hjälpa mig idag" eller "Jag behöver hjälp med studierna", svara direkt i vanlig svensk text.
            - Använd inte verktyg direkt om användarens fråga är vag eller allmän.
            - Skriv aldrig JSON, toll-call-format eller påhittade funktionsansrop i svaret. 
            - Om användaren skriver något brett, som "Jag behöver hjälp med studierna", börja med att förklara vilken typ av hjälp du kan ge.
            - Använd verktyg först när användaren har gett tillräckligt med information, till exempel deadline, antal timmar, svårighetsgrad eller typ av uppgift.
            - Hitta aldrig på siffror eller detaljer som användaren inte gett. 
            - När ett verktyg används, sammanfatta resultatet naturligt och kortfattat på svenska. 
            - Undvik tekniska eller konstiga formuleringar. 
            
        """
    )
    while True:
        user_input = get_user_input("Ställ din fråga: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": user_input}]}
        )
        print("\nSvar:")

        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            content = getattr(last_message, "content", "")
            print(content if content else "Jag kunde inte formulera ett svar")
        else:
            print("Inget svar returnerades från agenten.")


def run():
    asyncio.run(run_async())


if __name__ == "__main__":
    run()
