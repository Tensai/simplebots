import logging
import random
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler


API_TOKEN = 'YOUR_API_TOKEN_HERE'

# Enable logging + basic config
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
msg_skip = 10
msg_skipped = 0
msg_count = 1


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Лучший в мире хуебот с вами!')


def wassup(bot, update):
    """Send a message when the command /help is issued."""
    global msg_count
    global msg_skip
    answer = 'Привет! Я лучший в мире хуебот! Сейчас я пропускаю от 0 до {0} сообщений и хуефицирую {1} последних слов в предложении'.format(
        msg_skip, msg_count)
    update.message.reply_text(answer)

    
def skip(bot, update):
    try:
        global msg_skip
        global msg_skipped
        val = int(update.message.text.split(' ')[-1].strip())
        if val < 0:
            raise ValueError
        msg_skip = val
        msg_skipped = 0
        update.message.reply_text('Отлично! Я буду пропускать от 0 до {0} сообщений'.format(msg_skip))
    except ValueError:
        update.message.reply_text('Совсем тупой штоле? Используй команду /skip X, где Х - целое положительное число')


def count(bot, update):
    try:
        global msg_count
        val = int(update.message.text.split(' ')[-1].strip())
        if val < 0:
            raise ValueError
        msg_count = val
        update.message.reply_text('Отлично! Я буду хуефицировать {0} последних слов сообщения'.format(msg_count))
    except ValueError:
        update.message.reply_text('Совсем тупой штоле? Используй команду /count X, где Х - целое положительное число')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)
    
    
def general_msg(bot, update):
    global msg_skipped
    global msg_skip
    chance = 1 if msg_skipped >= msg_skip else 1 / msg_skip
    msg_skipped += 1
    if chance >= random.random():
        words = update.message.text.split(' ')
        if words:
            shift = min(len(words), msg_count)
            update.message.reply_text(' '.join([hueficate(word) for word in words[-shift:]]))
            msg_skipped = 0
            return
    

def hueficate(word):
    huefix = 'ху'
    replaces = {'а': 'я', 'е': 'е', 'ё': 'ё', 'и': 'и', 'о': 'е', 'у': 'ю', 'ю': 'ю', 'я': 'я', }
    vowels = replaces.keys()
    if word.find(huefix) != 0:
        for pos, letter in enumerate(word):
            if letter in vowels:
                return huefix + replaces[letter] + word[pos + 1:]
    return None


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(API_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('wassup', wassup))
    dp.add_handler(CommandHandler('skip', skip))
    dp.add_handler(CommandHandler('count', count))
    
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
