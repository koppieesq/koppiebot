#!/usr/bin/env python3

import getpass
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
import json
import requests

# Load environment variables from a .env file, if it exists (not in git)
load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

# Load langchain components
llm = init_chat_model("gpt-4o", model_provider="openai")
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = InMemoryVectorStore(embeddings)

# Load the blog knowledge
# df = pd.read_csv(f"{current_path}/embeddings.csv", index_col=0)
# df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)

# Load the environment variable for the blog URL
blog_url = os.environ.get("API_URL")

# Load the blog knowledge
# loader = WebBaseLoader(
#     web_paths=(blog_url,),
#     bs_kwargs=dict(
#         parse_only=bs4.SoupStrainer(
#             class_=("post-content", "post-title", "post-header")
#         )
#     ),
# )
# docs = loader.load()

# For development environments only
is_dev = os.getenv('ENVIRONMENT') == 'development'
verify_ssl = False if is_dev else True
response = requests.get(blog_url, verify=verify_ssl)

try:
    data = response.json()
except json.JSONDecodeError as e:
    print(f"Error parsing JSON: {e}")

docs = [Document(page_content=post['body'][0]['value']) for post in data]
# print(docs)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)

# Index chunks
_ = vector_store.add_documents(documents=all_splits)

# Define prompt for question-answering
prompt = hub.pull("rlm/rag-prompt")


# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


# Define application steps
def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


# Compile application and test
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

response = graph.invoke({"question": "Who is Jordan Koplowicz?"})
print(response["answer"])
