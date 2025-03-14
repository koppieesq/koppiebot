#!/usr/bin/env python3

import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from questions import answer_question
import daemon
import discord
from discord.ext import commands
import time

# Load environment variables from a .env file, if it exists (not in git)
load_dotenv()

# Get the current path as an environment variable
current_path = os.environ['CURRENT_PATH']

# Load the blog knowledge
df = pd.read_csv(f"{current_path}/embeddings.csv", index_col=0)
df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)

# Define Discord bot
# intents = discord.Intents.default()
# intents.message_content = True
# discord_bot_token = os.environ['DISCORD_BOT_TOKEN']
# bot = commands.Bot(command_prefix='/', intents=intents)

# Define langchain bot.
# This is a daemon process that runs in the background.
with daemon.DaemonContext():
  api_key = os.environ['LANGSMITH_API_KEY']
  while True:
    try:
      # Load the blog knowledge
      df = pd.read_csv(f"{current_path}/embeddings.csv", index_col=0)
      df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)
      print("Loaded blog knowledge")
      break
    except Exception as e:
      print(e)
      print("Retrying in 5 seconds...")
      time.sleep(5)

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command()
async def ask(ctx):
    # Strip command from question before passing it to AI
    question = ctx.message.content.replace('/ask ', '')
    answer = answer_question(df, question=question, debug=False)
    await ctx.send(answer)

bot.run(discord_bot_token)
