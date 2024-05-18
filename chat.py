import os
import json
from openai import OpenAI
import pandas as pd
import numpy as np
from questions import answer_question
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import daemon

# Define variables
tg_bot_token = os.environ['TG_BOT_TOKEN']
df = pd.read_csv('embeddings.csv', index_col=0)
df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)

# Main function: relay questions to answer_question()
async def koppiebot(update: Update, context: ContextTypes.DEFAULT_TYPE):
  print(f"Received message: {update.message}")
  answer = answer_question(df, question=update.message.text, debug=True)
  await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)

def chat():
  application = ApplicationBuilder().token(tg_bot_token).build()
  
  koppiebot_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), koppiebot)
  application.add_handler(koppiebot_handler)

  application.run_polling()

if __name__ == '__main__':
  with daemon.DaemonContext():
    chat()
