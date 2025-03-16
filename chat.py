#!/usr/bin/env python3

import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from questions import answer_question
import daemon
import discord
from discord.ext import commands

# Load environment variables from a .env file, if it exists (not in git)
load_dotenv()

# Get the current path as an environment variable
current_path = os.path.dirname(os.path.abspath(__file__))

# Load the blog knowledge
df = pd.read_csv(f"{current_path}/embeddings.csv", index_col=0)
df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)

# Answer the question, and return the answer.
def answer(query):
    # Strip command from question before passing it to AI
    question = query.replace('/ask ', '')
    answer = answer_question(df, question=question, debug=False)
    return answer
