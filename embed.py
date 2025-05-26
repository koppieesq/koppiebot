#!/usr/bin/env python3

import pandas as pd
import os
import tiktoken
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from time import time
import requests
from io import StringIO

# Start the timer
start_time = time()

# Load environment variables from a .env file, if it exists (not in git)
load_dotenv()
openai = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Load the cl100k_base tokenizer which is designed to work with the ada-002 model
tokenizer = tiktoken.get_encoding("cl100k_base")


# Download the CSV from URL
def load_csv_from_url(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes
    return pd.read_csv(StringIO(response.text), index_col=0)

print("Loading CSV from URL...")
url = 'https://d10.koplowiczandsons.com/export'
df = load_csv_from_url(url)
df.columns = ['title', 'body']

# Tokenize the text and save the number of tokens to a new column
df['n_tokens'] = df.body.apply(lambda x: len(tokenizer.encode(x)))

chunk_size = 1000  # Max number of tokens

print("Splitting text into chunks...")
text_splitter = RecursiveCharacterTextSplitter(
    length_function = len,
    chunk_size = chunk_size,
    chunk_overlap  = 0,  # No overlap between chunks
    add_start_index = False,  # We don't need start index in this case
)

shortened = []

print("Embedding text chunks...")
for row in df.iterrows():

  # If the text is None, go to the next row
  if row[1]['body'] is None:
    continue

  # If the number of tokens is greater than the max number of tokens, split the text into chunks
  if row[1]['n_tokens'] > chunk_size:
    # Split the text using LangChain's text splitter
    chunks = text_splitter.create_documents([row[1]['body']])
    # Append the content of each chunk to the 'shortened' list
    for chunk in chunks:
      shortened.append(chunk.page_content)

  # Otherwise, add the text to the list of shortened texts
  else:
    shortened.append(row[1]['body'])

print("Creating embeddings...")
df = pd.DataFrame(shortened, columns=['body'])
df['n_tokens'] = df.body.apply(lambda x: len(tokenizer.encode(x)))

print("Sending embeddings for processing...")
df['embeddings'] = df.body.apply(lambda x: openai.embeddings.create(
    input=x, model='text-embedding-ada-002').data[0].embedding)

print("Saving embeddings to CSV...")
df.to_csv('embeddings.csv')

end_time = time()
print(f"Script completed in {end_time - start_time:.2f} seconds")
