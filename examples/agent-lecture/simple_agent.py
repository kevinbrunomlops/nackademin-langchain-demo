from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from util.models import get_model
from util.streaming_utils import STREAM_MODES, handle_stream
from util.pretty_print import get_user_input

def run():
    # Get predefined attributes
    model = get_model(temperature=0.1,
                      top_p=0.9)
    
    memory = InMemorySaver()

    # Create agent
    agent = create_agent(
        model=model,
        system_prompt=(
            "Du är en hjälpsam assistent som svarar på användarens frågor."
            "Svara alltid på svenska och var koncis men informativ."
        ),
        checkpointer=memory,
    )

    thread_id = "user-session-1"
    
    print("Agent med minne startad. Skriv 'exit' för att avsluta.\n")

    while True:
        user_input = input("Ställ din fråga: ")
        if user_input.lower() == "exit":
            break

        result = agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": user_input}
                ]
            },
            config={
                "configurable": {
                    "thread_id": thread_id
                }
            }
        )

        print(f"Agent: {result['messages'][-1].content}\n")

    # Get user input
    # user_input = get_user_input("Ställ din fråga")

    # Call the agent
    # process_stream = agent.stream(
    #     {"messages": [{"role": "user", "content": user_input}]},
    #     stream_mode=STREAM_MODES,
    # )

    # Stream the process
    # handle_stream(process_stream)


if __name__ == "__main__":
    run()
