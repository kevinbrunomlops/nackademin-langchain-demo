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
uv run python3 -m examples.agent-lecture.agent_of_your_chose
```
