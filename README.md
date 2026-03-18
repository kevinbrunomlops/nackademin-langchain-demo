# AI-agent with RISE_AP (LangChain) - UV project

This project demonstrates how to build different AI-agents with LangChain and connect it to an external model via RISE-API. I focused on building 3 agents. One with memory, one with RAG (Retrival-Augmented Generation) and a web fetcher.    

## Technical overview 
```
User input (terminal)
        ↓
LangChain Agent
        ↓
ChatOllama (klient)
        ↓
RISE API (nackademin.icedc.se)
        ↓
LLM (Llama 3)
        ↓
Svar tillbaka till användaren
```
RISE-API exposes via a Ollama-compatible interface, which makes us use `ChatOllama` in LangChain.


### Prerequisites
- Python 3.12
- Ollama server with access to Llama models

### Setup

1. Clone the project
2. Set up the project with uv:
```bash
uv sync
```
3. Create a `.env` file with your configuration:
```bash
OLLAMA_BASE_URL=http://nackademin.icedc.se
OLLAMA_BEARER_TOKEN=your-bearer-token-here
```

### Running Examples

Run from project root:

```bash
uv run python3 -m examples.agent_lecture.agent_of_your_choice
```

### Short summary about the agents
#### Agent with memory 
This agent can have a coherent conversation by remembering previous messages in the same session. It uses a short-term memory (`InMemorySaver`) and a `thread_id` to connect the dialogue, which makes it able to answer follow up questions and refer to previous information.

Use case: 
Good for dialogues, chatbots and interactive assistents. 

#### RAG-Agent (Retrieval-Augmented Generation)
This agent get's information from local documents and uses it as it main source to answer questions. It builds vector databases (FAISS) of the documents and searches for relevant parts when the user asks a question. 

Use case:
Perfect when you want an agent that answers on specific material and not in genereal terms.

#### Web fetcher agent
This agent can get information from the web by:
1. Search after relevant web pages. 
2. Get information 
3. Base the answer on the information it got from the web. 

It is designed not to guess or make up information, but only to use what is actually available on the web. 

Use case: 
Good for topical issues or when information is not available locally. 