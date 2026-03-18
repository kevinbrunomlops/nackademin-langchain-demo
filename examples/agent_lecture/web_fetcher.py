from langchain.agents import create_agent
from langchain_community.agent_toolkits.openapi.toolkit import RequestsToolkit
from langchain_community.utilities.requests import TextRequestsWrapper

from util.models import get_model
from util.streaming_utils import STREAM_MODES, handle_stream
from util.pretty_print import get_user_input

SYSTEM_PROMPT = """
ROLE: 
Du är en hjälpsam assistent som kan hämta innehåll fråm webbsidor. 

Goal: 
Besvara användarens frågor genom att hämta och använda relevant information ifrån webben. 

Rules: 
1. Svara alltid på svenska.
2. Använd verktyget att gå ut på webben för att hämta relevant information användaren ställer till dig. 
3. Bygg svaret på det du faktiskt hittar på webben.
4. Om informationen  du hittar inte räcker ska du säga att underlaget saknas istället för att gissa.
5. Hitta inte på fakta eller fyll i med egen kunskap.

Source handling:
- Referera gärna till vilka hemsidor informationen kommer ifrån. 
- Om flera källor används, kombinera de tydligt och konsekvent. 

Style: 
- Tydlig och pedagogisk
- Kortfattad men informativ
- Använd punktlistor vid behov

Output format: 
- Direkt svar på frågan
- (Om relevant) Notera om information saknas. 
""".strip()

def run():
    model = get_model
    tools = RequestsToolkit(
        requests_wrapper=TextRequestsWrapper(headers={}),
        allow_dangerous_requests=True, 
    ).get_tools()

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        )
    
    user_input = get_user_input("Ställ din fråga")

    process_stream = agent.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        stream_mode=STREAM_MODES,
    )

    handle_stream(process_stream)

if __name__ == "__name__":
    run()


     