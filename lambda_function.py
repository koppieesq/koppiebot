import os
import json
from openai import OpenAI
import pandas as pd
import numpy as np
from questions import answer_question
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Define variables
tg_bot_token = os.environ['TG_BOT_TOKEN']
df = pd.read_csv('embeddings.csv', index_col=0)
df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)

# Main function: relay questions to answer_question()
async def koppiebot(update: Update, context: ContextTypes.DEFAULT_TYPE):
  print(f"Received message: {update.message}")
  answer = answer_question(df, question=update.message.text, debug=True)
  await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)

def lambda_handler(event, context):
  application = ApplicationBuilder().token(tg_bot_token).build()
  
  # Define a job queue to keep the chatbot running
  job_queue = application.job_queue
  job_queue.run_repeating(koppiebot, interval=60, first=0)

  koppiebot_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), koppiebot)
  application.add_handler(koppiebot_handler)

  application.run_polling()

if __name__ == '__main__':
  lambda_handler(None, None)