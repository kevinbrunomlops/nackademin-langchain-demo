from urllib.parse import urlparse

import requests
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults

from util.models import get_model
from util.streaming_utils import STREAM_MODES, handle_stream
from util.pretty_print import get_user_input

SYSTEM_PROMPT = """
ROLE: 
Du är en hjälpsam assistent som kan besvara frågor med hjälp av webbkällor. 

Goal: 
Besvara användarens frågor genom att hämta och använda relevant information ifrån webben. 

Rules: 
1. Svara alltid på svenska.
2. Gissa aldrig domännamn eller URL:er.
3. Använd först sökverktyget för att hitta relevanta länkar.
4. Använd sedan fetch-verktyget på den mest relevanta länken.
5. Bygg svaret på det du faktiskt hittar på webben. 
6. Om informationen inte räcker ska du säga det istället för att gissa.
7. Hitta inte på fakta eller fyll i med egen kunskap.

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

search_tool = DuckDuckGoSearchResults(
    max_results=5,
    output_format="list"
)
@tool
def fetch_webpage(url: str) -> str:
    """
    Hämtar textinnehåll från en webbsida via en fullständig URL.
    Returnerar ett tydligt felmeddelande istället för att krascha.
    """
    parsed = urlparse(url)

    if parsed.scheme not in{"http", "https"} or not parsed.netloc:
        return "Fel: Ogiltig URL. En fullständig http/https-URL krävs."
    
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; LangChainDem/1.0)"
    }

    try: 
        response = requests.get(url, headers=headers, temout=15)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "").lower()
        if "text/html" not in content_type and "text/plain" not in content_type:
            return (
                f"Fel: Sidan kunde hämtas men innehållet verkar inte vara läsbar textinnehåll.  "
                f"(content-type: {content_type})."
            )
        
        text = response.text.strip()
        if not text:
            return "Fel: Sidan hämtades men innehållet var tomt."
        return text[:12000]
    except requests.exceptions.RequestException as e:
        return f"Fel vid hämtning av sidan: {e}"
    
def run():
    model = get_model(
        temperature=0.2,
        top_p=0.8,
    )
    tools = [search_tool, fetch_webpage]

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        )
    
    try:
        while True:
            user_input = get_user_input("Ställ din fråga (skriv 'exit' för att avsluta)")

            if user_input.lower() in ["exit", "quit"]:
                print("Avslutar agenten...")
                break
    
            process_stream = agent.stream(
                {"messages": [{"role": "user", "content": user_input}]},
                stream_mode=STREAM_MODES,
            )
            handle_stream(process_stream)
    except KeyboardInterrupt:
        print("\nAvbruten av användaren")
    

if __name__ == "__main__":
    run()


     