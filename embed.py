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
import argparse

# Start the timer
start_time = time()

# Load environment variables from a .env file, if it exists (not in git)
load_dotenv()
openai = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Load the cl100k_base tokenizer which is designed to work with the ada-002 model
tokenizer = tiktoken.get_encoding("cl100k_base")

# Parse command line arguments using argparse
parser = argparse.ArgumentParser(description='Process and embed CSV data.')
parser.add_argument('--url', type=str, default='https://d10.koplowiczandsons.com/export', help='URL of the CSV file to process')
parser.add_argument('--unsafe', action='store_true', help='Disable SSL certificate verification (INSECURE)')
parser.add_argument('--primary', type=str, default='body', help='Column to use as primary key (default: body)')
args = parser.parse_args()

url = args.url
unsafe = args.unsafe
primary = args.primary

# Download the CSV from URL
def load_csv_from_url(url, unsafe):
    if unsafe:
        # Disable SSL certificate verification
        print("Warning: SSL certificate verification is disabled.")
        response = requests.get(url, verify=False)
    else:
        response = requests.get(url)
    response.raise_for_status()
    return pd.read_csv(StringIO(response.text))

print("Loading CSV from " + url)
df = load_csv_from_url(url, unsafe)

print("CSV columns detected:", list(df.columns))

# Use the primary column specified by the user (default 'body')
if primary not in df.columns:
    raise ValueError(f"Primary column '{primary}' not found in CSV columns: {list(df.columns)}")

print("Found primary column:", primary)

# Tokenize the text and save the number of tokens to a new column
df['n_tokens'] = df[primary].apply(lambda x: len(tokenizer.encode(str(x))))

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
    if pd.isna(row[1][primary]):
        continue
    # If the number of tokens is greater than the max number of tokens, split the text into chunks
    if row[1]['n_tokens'] > chunk_size:
        chunks = text_splitter.create_documents([row[1][primary]])
        for chunk in chunks:
            shortened.append(chunk.page_content)
    else:
        shortened.append(row[1][primary])

print("Creating embeddings...")
df_embed = pd.DataFrame(shortened, columns=[primary])
df_embed['n_tokens'] = df_embed[primary].apply(lambda x: len(tokenizer.encode(str(x))))

print("Sending embeddings for processing...")
df_embed['embeddings'] = df_embed[primary].apply(lambda x: openai.embeddings.create(
    input=str(x), model='text-embedding-ada-002').data[0].embedding)

print("Saving embeddings to CSV...")
df_embed.to_csv('embeddings.csv', index=False)

end_time = time()
print(f"Script completed in {end_time - start_time:.2f} seconds")
