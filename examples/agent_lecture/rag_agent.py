import os
from dotenv import load_dotenv
from pathlib import Path

from langchain.agents import create_agent
from langchain_core.tools import Tool
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import InMemorySaver

from util.models import get_model

load_dotenv()

base_url = os.getenv("OLLAMA_BASE_URL")
bearer_token = os.getenv("OLLAMA_BEARER_TOKEN")

if not bearer_token:
    raise ValueError("OLLAMA_BEARER_TOKEN must be set in .env")

DOCS_DIR = Path(__file__).parent / "rag_docs"

SYSTEM_PROMPT = """ 
Du är en svensk RAG-agent för kursmaterial

Arbetsregler:
1. Svara alltid på svenska.
2. Använd dokumentverktyg när frågan rör inehållet i dokumenten. 
3. Bygg svaret på det du faktiskt hittar i dokumenten.
4. Om dokumenten inte räcker ska du säga att underlaget saknas istället för att gissa.
5. Nämn gärna vilket dokument eller tema informationen kommer från.
""".strip()

def build_retriever():
    loader = DirectoryLoader(
        path="examples/agent_lecture/rag_docs",
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=False,
    )
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=120,
    )
    chunks = splitter.split_documents(documents)

    embeddings = OllamaEmbeddings(
        model="llama3.1:8b",
        base_url=base_url,
        client_kwargs={
            "headers": {
                "Authorization": f"Bearer {bearer_token}"
            }
        },
    )
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 4})

def run() -> None:
    model = get_model(temperature=0.1)
    memory = InMemorySaver()

    retriever = build_retriever()
    retriever_tool = Tool(
        name="search_course_documents",
        func=retriever.invoke,
        description=(
            "Search for relevant information in local course documents about LangChain, agents, "
            "RAG and tools. Use this when the user asks about the content of the documents. "
        ),
    )

    agent = create_agent(
        model=model,
        tools=[retriever_tool],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=memory,
    )

    thread_id = "rag-session-1"
    print("RAG-agent startad. Fråga om innehållet i dokumenten. Skriv 'exit' för att avsluta. \n")

    while True:
        user_input = input("Fråga: ").strip()
        if user_input.lower() == "exit":
            break

        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config={"configurable": {"thread_id": thread_id}},
        )
        print(f"\nAgent: {result['messages'][-1].content}\n")


if __name__ == "__main__":
    run()