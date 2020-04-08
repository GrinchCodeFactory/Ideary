import json
import logging
import time
from os.path import expanduser

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler, ConversationHandler
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

with open(expanduser("~/ideary-conf.json"), 'r') as fh:
    conf = json.load(fh)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

updater = Updater(token=conf['telegram']['token'], use_context=True)
dispatcher = updater.dispatcher

entryList = []


def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I am your diary!")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Here are the rules: ")
    context.bot.send_message(chat_id=update.effective_chat.id, text="1. Don't lie to me")
    context.bot.send_message(chat_id=update.effective_chat.id, text="2. Try to add 1 entry per day")
    context.bot.send_message(chat_id=update.effective_chat.id, text="To add an entry type /add {text}")
    context.bot.send_message(chat_id=update.effective_chat.id, text="To get an entry type /get {id}")


def addEntryByCommand(update, context):
    global entryList

    chatID = update.effective_chat.id
    # 5: because of command length
    text = update.message.text[5:]
    ts = int(round(time.time() * 1000))

    entryList.append({'id': len(entryList), 'text': text, 'ts': ts})
    logger.debug("Added: " + str({'id': chatID, 'text': text, 'ts': ts}))

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Entry has been added with ID: ' + str(len(entryList) - 1))


def addEntry(update, context):
    global entryList

    chatID = update.effective_chat.id
    text = update.message.text

    ts = int(round(time.time() * 1000))

    entry = {'id': len(entryList), 'text': text, 'ts': ts}

    keyboard = [[InlineKeyboardButton("Add as entry", callback_data=json.dumps(entry)),
                 InlineKeyboardButton("Do nothing", callback_data="{}")]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


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


def addAssEntry(update, context):
    global entryList
    query = update.callback_query
    if len(query.data) > 2:
        entry = json.loads(query.data)
        entryList.append(entry)
        query.edit_message_text(text='Entry has been added with ID: ' + str(len(entryList) - 1))
        logger.debug("Added: " + str(entry))
    else:
        query.edit_message_text(text='Stop wasting my time you prick!')

    query.answer()


getLastNEntries_handler = CommandHandler('get', getEntryById)
dispatcher.add_handler(getLastNEntries_handler)

addEntryByCommand_handler = CommandHandler('add', addEntryByCommand)
dispatcher.add_handler(addEntryByCommand_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

addEntry_handler = MessageHandler(Filters.text, addEntry)
dispatcher.add_handler(addEntry_handler)

updater.dispatcher.add_handler(CallbackQueryHandler(addAssEntry))

updater.start_polling()
