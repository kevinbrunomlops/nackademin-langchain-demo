# Study Assistant agent (MCP + langchain)

This agent is a simple study assistant that helps the user plan and structure their schoolwork. It is connected to an external MCP server that provides various tools for analyzing taks and study time.     

## Problem it solves
Students who often have difficulty:

- Prioritizing tasks.
- Estimating how much time is needed.
- Determining whether they are at risk of missing a deadline.

The agent helps make better decisions about studies by using structured tools.


## Available tools (via MCP)
The agent has access to a selection of tools from the MCP server:
prioritize_task
- Calculates the importance of a task based on deadline, difficulty and estimated work time. 
estimate_study_sessions
- Calculates the number of study sessions needed to complete a task. 
risk_check_deadline
- Assesses the risk of not comppleting on time based on remaining work and available time. 

Note: The MCP server contains more tools, but the agents filters and uses only these.

### How it works
1. The user asks the agent a question.
2. The agent determines if a tool is needed.
3. If necessary, an MCP tool is called.
4. The tool result is processed via middleware.
5. The agent returns a clear and natural answer.


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
uv run python3 -m tool_lecture.mcp_agent
```

