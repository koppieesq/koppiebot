import os
import json
from openai import OpenAI
import pandas as pd
import numpy as np
from questions import answer_question
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import daemon
import discord
from discord.ext import commands

# Load the blog knowledge
df = pd.read_csv('embeddings.csv', index_col=0)
df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)

# Define a client for the Discord bot
class KoppieBot(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == 'ping':
            await message.channel.send('pong')
        
        answer = answer_question(df, question=message.content, debug=True)
        await message.channel.send(answer)

if __name__ == '__main__':
  with daemon.DaemonContext():
    # Define Discord bot
    intents = discord.Intents.default()
    intents.message_content = True
    client = KoppieBot(intents=intents)
    discord_bot_token = os.environ['DISCORD_BOT_TOKEN']
    client.run(discord_bot_token)
