import pandas as pd
import os
import tiktoken
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

# Load environment variables from a .env file, if it exists (not in git)
load_dotenv()
openai = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Load the cl100k_base tokenizer which is designed to work with the ada-002 model
tokenizer = tiktoken.get_encoding("cl100k_base")

df = pd.read_csv('export.csv', index_col=0)
df.columns = ['title', 'body']

# Tokenize the text and save the number of tokens to a new column
df['n_tokens'] = df.body.apply(lambda x: len(tokenizer.encode(x)))

chunk_size = 1000  # Max number of tokens

text_splitter = RecursiveCharacterTextSplitter(
        # This could be replaced with a token counting function if needed
    length_function = len,
    chunk_size = chunk_size,
    chunk_overlap  = 0,  # No overlap between chunks
    add_start_index = False,  # We don't need start index in this case
)

shortened = []

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

df = pd.DataFrame(shortened, columns=['body'])
df['n_tokens'] = df.body.apply(lambda x: len(tokenizer.encode(x)))

df['embeddings'] = df.body.apply(lambda x: openai.embeddings.create(
    input=x, model='text-embedding-ada-002').data[0].embedding)

df.to_csv('embeddings.csv')
