import logging
import time

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

from Ideary.src.key import Key

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

updater = Updater(token=Key.key, use_context=True)
dispatcher = updater.dispatcher

entryList = []


def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I am your diary!")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Here are the rules: ")
    context.bot.send_message(chat_id=update.effective_chat.id, text="1. Don't lie to me")
    context.bot.send_message(chat_id=update.effective_chat.id, text="2. Try to add 1 entry per day")
    context.bot.send_message(chat_id=update.effective_chat.id, text="To add an entry type /add {text}")
    context.bot.send_message(chat_id=update.effective_chat.id, text="To get an entry type /get {id}")


def addEntry(update, context):
    global entryList

    chatID = update.effective_chat.id
    # 5: because of command length
    text = update.message.text[5:]
    ts = int(round(time.time() * 1000))

    entryList.append({'id': len(entryList), 'text': text, 'ts': ts})
    logger.debug("Added: " + str({'id': chatID, 'text': text, 'ts': ts}))

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Entry has been added with ID: ' + str(len(entryList) - 1))


def getEntryById(update, context):
    chatID = update.effective_chat.id
    # 5: because of command length
    n = update.message.text[5:]

    if n.isdigit():
        n = int(n)
        context.bot.send_message(chat_id=update.effective_chat.id, text=str(entryList[n]))
    else:
        logger.debug('Passed id is NOT a number')
        context.bot.send_message(chat_id=update.effective_chat.id, text='Passed ID is NOT a number')


getLastNEntries_handler = CommandHandler('get', getEntryById)
dispatcher.add_handler(getLastNEntries_handler)

addEntry_handler = CommandHandler('add', addEntry)
dispatcher.add_handler(addEntry_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

# echo_handler = MessageHandler(Filters.text, echo)
# dispatcher.add_handler(echo_handler)


updater.start_polling()
