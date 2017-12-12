import logging
import sqlite3
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler


API_TOKEN = 'YOUR-API-TOKEN'

# Enable logging + basic config
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
leads_top_cnt = 5
fuck_patterns = ['fuck you', 'пшелнах', 'пошел нах', 'иди нах', 'пнх',
                 'иди ты нах', 'пошел ты нах', 'нах пошел', 'нах иди', 'нахуй иди', 'нахуй пошел']


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Посылать друзей нахуй - весело!')


def help(bot, update):
    global leads_top_cnt
    commands = [
        '/howto - показать эту справку',
        '/fuckerleads - топ-{0} посылающих'.format(leads_top_cnt),
        '/fuckedleads - топ-{0} посылаемых'.format(leads_top_cnt),
    ]
    update.message.reply_text('\n'.join(commands))
    

def fuckedleads(bot, update):
    leads(update, 'hits_in')


def fuckerleads(bot, update):
    leads(update, 'hits_out')


def leads(update, field):
    global leads_top_cnt
    connection = sqlite3.connect('fuckdb.sqlite')
    cursor = connection.cursor()
    cursor.execute('SELECT chatter_name, {0} '
                   'FROM stats WHERE chat_id = ? AND {0} > 0 '
                   'ORDER BY {0} DESC LIMIT {1}'.format(field, leads_top_cnt), [update.effective_chat.id])
    lexeme = 'был послан' if field == 'hits_in' else 'послал друзей'
    rows = cursor.fetchall()
    rating = ['{0}. {1} {2} нахуй {3} {4}!'.format(i + 1, name, lexeme, hits, get_stage_lexeme(hits))
              for i, (name, hits) in enumerate(rows)]
    update.message.reply_text('\n'.join(rating))


def general_msg(bot, update):
    if update.effective_message is not None:
        response = update.effective_message
        if response.reply_to_message is not None:
            request = response.reply_to_message
            global fuck_patterns
            msg = update.message.text.lower()
            for pattern in fuck_patterns:
                if msg.find(pattern) != -1:
                    new_hits = process_fuck(update.effective_chat.id, response.from_user, request.from_user)
                    answer = 'Дорогой наш @{0}! От лица @{1} торжественно посылаем тебя нахуй! ' \
                             'Счастливого путешествия!\n' \
                             'Конгратс! Тебя послали нахуй уже {2} {3}'.format(
                                request.from_user.username,
                                response.from_user.username,
                                new_hits,
                                get_stage_lexeme(new_hits))
                    update.message.reply_text(answer)
                    break


def process_fuck(chat_id, u_from, u_to):
    connection = sqlite3.connect('fuckdb.sqlite')
    cursor = connection.cursor()
    cursor.execute('SELECT chatter_id FROM stats WHERE chatter_id in (?, ?) AND chat_id = ?', (u_from.id, u_to.id, chat_id))
    
    current_chatters = set([cid for cid, in cursor.fetchall()])
    for chatter in {u_from, u_to}:
        if chatter.id not in current_chatters:
            cursor.execute('INSERT INTO stats (chatter_id, chatter_name, chat_id) VALUES (?, ?, ?)',
                           (chatter.id, chatter.username, chat_id))
            
    cursor.execute('UPDATE stats SET hits_out = hits_out + 1 WHERE chatter_id = ? AND chat_id = ?', (u_from.id, chat_id))
    cursor.execute('UPDATE stats SET hits_in = hits_in + 1 WHERE chatter_id = ? AND chat_id = ?', (u_to.id, chat_id))
    cursor.execute('SELECT hits_in FROM stats WHERE chatter_id = ? AND chat_id = ?', (u_to.id, chat_id))
    hits, = cursor.fetchone()
    connection.commit()
    return hits

    
def get_stage_lexeme(hits):
    return 'раза' if 1 < int(str(hits)[-1]) < 5 else 'раз'


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(API_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('howto', help))
    dp.add_handler(CommandHandler('fuckerleads', fuckerleads))
    dp.add_handler(CommandHandler('fuckedleads', fuckedleads))
    #dp.add_handler(CommandHandler('fuckoff', fuckoff))

    
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, general_msg))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
