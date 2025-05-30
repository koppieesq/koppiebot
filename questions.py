#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd
from openai import OpenAI
from typing import List
from scipy import spatial
from dotenv import load_dotenv

# Load environment variables from a .env file, if it exists (not in git)
load_dotenv()

openai = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
max_length = 5000

def distances_from_embeddings(
  query_embedding: List[float],
  embeddings: List[List[float]],
  distance_metric="cosine",
) -> List[List]:
  """Return the distances between a query embedding and a list of embeddings."""
  distance_metrics = {
      "cosine": spatial.distance.cosine,
      "L1": spatial.distance.cityblock,
      "L2": spatial.distance.euclidean,
      "Linf": spatial.distance.chebyshev,
  }
  distances = [
      distance_metrics[distance_metric](query_embedding, embedding)
      for embedding in embeddings
  ]
  return distances

def create_context(question, df, max_len=max_length):
  # Automatically detect the primary column
  exclude_cols = {'embeddings', 'n_tokens', 'distances'}
  text_cols = [col for col in df.columns if df[col].dtype == object and col not in exclude_cols]
  if not text_cols:
      raise ValueError("No suitable text column found in DataFrame!")
  primary_col = text_cols[0]

  """
    Create a context for a question by finding the most similar context from the dataframe
    """
  # Get the embeddings for the question
  q_embeddings = openai.embeddings.create(
      input=question, model='text-embedding-ada-002').data[0].embedding

  # Get the distances from the embeddings
  df['distances'] = distances_from_embeddings(q_embeddings,
                                              df['embeddings'].values,
                                              distance_metric='cosine')

  returns = []
  cur_len = 0

  # Sort by distance and add the text to the context until the context is too long
  for i, row in df.sort_values('distances', ascending=True).iterrows():
    # Add the length of the text to the current length
    cur_len += row['n_tokens'] + 4

    # If the context is too long, break
    if cur_len > max_len:
      break

    # Else add it to the text that is being returned
    returns.append(row[primary_col])

  # Return the context
  return "\n\n###\n\n".join(returns)

def answer_question(df,
                    model="gpt-4o",
                    question="What is the meaning of life?",
                    max_len=max_length,
                    debug=False,
                    max_tokens=1000,
                    stop_sequence=None):
  """
    Answer a question based on the most similar context from the dataframe texts
    """
  context = create_context(
      question,
      df,
      max_len=max_len,
  )
  # If debug, print the raw model response
  if debug:
    print("Context:\n" + context)
    print("\n\n")

  try:
    # Load prompt from prompt.txt
    with open("prompt.txt", "r") as f:
      prompt_template = f.read()
    prompt = prompt_template.format(context=context, question=question)

    # Create a completions using the question and context
    response = openai.chat.completions.create(
        model=model,
        messages=[{
            "role":
            "user",
            "content":
            prompt,
        }],
        temperature=0,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=stop_sequence,
    )

    if debug:
      print("Raw response:")
      print(response)
      print("\n\n")
      
    return response.choices[0].message.content
  except Exception as e:
    print(e)
    return ""
