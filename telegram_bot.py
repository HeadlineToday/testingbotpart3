import requests
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

# Your Telegram bot token
TOKEN = '7352954965:AAEebmVPec3kGMQ42fNdue2AylShZywvMq8'

def create_database():
    conn = sqlite3.connect('anime_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_anime (
            week TEXT PRIMARY KEY,
            top_anime TEXT
        )
    ''')
    conn.commit()
    conn.close()

def fetch_anime_data(query):
    url = 'https://graphql.anilist.co'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json={'query': query}, headers=headers)
    print("Response Status Code:", response.status_code)
    print("Response Body:", response.text)
    if response.status_code == 200:
        return response.json()
    return None

def get_weekly_top_anime():
    query = '''
    {
      Page {
        media(sort: POPULARITY_DESC, type: ANIME, season: WINTER, seasonYear: 2024) {
          title {
            romaji
            english
          }
          id
        }
      }
    }
    '''
    data = fetch_anime_data(query)
    if data and 'data' in data and 'Page' in data['data']:
        return data['data']['Page']['media']
    return None

def get_trending_anime():
    query = '''
    {
      Page {
        media(sort: TRENDING_DESC, type: ANIME) {
          title {
            romaji
            english
          }
          id
        }
      }
    }
    '''
    data = fetch_anime_data(query)
    if data and 'data' in data and 'Page' in data['data']:
        return data['data']['Page']['media']
    return None

def get_top_anime_list():
    query = '''
    {
      Page {
        media(sort: SCORE_DESC, type: ANIME) {
          title {
            romaji
            english
          }
          id
        }
      }
    }
    '''
    data = fetch_anime_data(query)
    if data and 'data' in data and 'Page' in data['data']:
        return data['data']['Page']['media']
    return None

async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Weekly Top Anime", callback_data='weekly')],
        [InlineKeyboardButton("Trending Anime", callback_data='trending')],
        [InlineKeyboardButton("Top Anime List", callback_data='top')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose:', reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    # Fetching the appropriate data based on the button clicked
    data = None
    if query.data == 'weekly':
        data = get_weekly_top_anime()
    elif query.data == 'trending':
        data = get_trending_anime()
    elif query.data == 'top':
        data = get_top_anime_list()

    print("Fetched Data:", data)  # Check what is being fetched

    if data:
        # Format the message text with labels
        message_lines = [f"{i+1}. {anime['title']['romaji']} ({anime['title']['english']})"
                         for i, anime in enumerate(data)]
        message = "\n".join(message_lines)
    else:
        message = 'No data available.'

    await query.edit_message_text(text=message)

def main() -> None:
    create_database()
    # Initialize the application with the token
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))

    # Start polling
    application.run_polling()

if __name__ == '__main__':
    main()
