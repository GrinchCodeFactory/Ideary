import json
import logging
import time
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater, CallbackQueryHandler

from src.ideary import read_conf
from src.ideary.diary import DiaryEntry
from src.ideary.storage import get_user_diary

conf = read_conf()['telegram']

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

updater = Updater(token=conf['token'], use_context=True)
dispatcher = updater.dispatcher

ongoingCreation = {}


# entryList = []

def testAction(data):
    print(str(data))


actionList = {'test': testAction}


def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I am your diary!")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Here are the rules: ")
    context.bot.send_message(chat_id=update.effective_chat.id, text="1. Don't lie to me")
    context.bot.send_message(chat_id=update.effective_chat.id, text="2. Try to add 1 entry per day")
    context.bot.send_message(chat_id=update.effective_chat.id, text="To add an entry type /add {text}")
    context.bot.send_message(chat_id=update.effective_chat.id, text="To get an entry type /get {id}")


def addEntryByCommand(update, context):
    chatID = update.effective_chat.id
    # 5: because of command length
    text = update.message.text[5:]
    ts = int(round(time.time() * 1000))

    diary = get_user_diary(chatID)
    entry = DiaryEntry(
        number=diary.next_entry_number(),
        text=text,
        timestamp=datetime.fromtimestamp(ts / 1000),
        diary_id=diary.diary_id,
    )
    get_user_diary(chatID).add_entry(entry)

    logger.debug("Added: %s", entry)

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Entry has been added with ID: ' + str(entry.number))


def getCurrentEntry(chatId):
    global ongoingCreation

    if chatId in ongoingCreation:
        return ongoingCreation[chatId]
    else:
        text = ''
        ts = int(round(time.time() * 1000))
        diary = get_user_diary(chatId)
        entry = DiaryEntry(
            number=diary.next_entry_number(),
            text=text,
            timestamp=datetime.fromtimestamp(ts / 1000),
            diary_id=diary.diary_id,
        )
        ongoingCreation[chatId] = entry
        return entry


def getEntryById(update, context):
    chatID = update.effective_chat.id
    # 5: because of command length
    n = update.message.text[5:]

    if n.isdigit():
        n = int(n)
        entry = get_user_diary(chatID).get_entry(n)
        context.bot.send_message(chat_id=update.effective_chat.id, text=str(entry))
    else:
        logger.debug('Passed id is NOT a number')
        context.bot.send_message(chat_id=update.effective_chat.id, text='Passed ID is NOT a number')


def addEntry(update, context):
    global ongoingCreation

    chatID = update.effective_chat.id

    entry = getCurrentEntry(str(chatID))

    entry.text = update.message.text

    sendReply(update, context)


def addImage(update, context):
    global ongoingCreation

    photoId = update.message.photo[-1].file_id

    file = context.bot.getFile(photoId)

    chatID = update.effective_chat.id

    entry = getCurrentEntry(str(chatID))

    entry.photo = file.download_as_bytearray()

    sendReply(update, context)


def addTags(update, context):
    global ongoingCreation

    chatID = update.effective_chat.id

    entry = getCurrentEntry(str(chatID))

    entry.tags = update.message.text[6:].split(',')

    sendReply(update, context)


def sendReply(update, context):
    chatID = update.effective_chat.id

    keyboard = [[InlineKeyboardButton("Finish",
                                      callback_data='{"actionName":"saveEntry","actionData":"' + str(chatID) + '"}'),
                 InlineKeyboardButton("Add tags/pics",
                                      callback_data='{"actionName":"doNothing","actionData":"' + str(chatID) + '"}'),
                 InlineKeyboardButton("Reject",
                                      callback_data='{"actionName":"rejectEntry","actionData":"' + str(chatID) + '"}')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def callbackHandler(update, context):
    global actionList
    query = update.callback_query.data

    if len(query) > 2:

        action = json.loads(query)
        actionData = action['actionData']
        actionName = action['actionName']
        actionList[actionName](update, context, actionData)

    else:
        logger.debug("Empty call back call")


def doNothing(update, context, acdata):
    query = update.callback_query

    logger.debug("Just chillin, doing nothing")

    query.edit_message_text(text='Just chillin, waiting for further input!: ')

    query.answer()


def rejectEntry(update, context, callData):
    query = update.callback_query

    del ongoingCreation[callData]

    logger.debug("removed entry with key: " + str(callData))

    query.edit_message_text(text='Entry deleted!: ', reply_markup=ReplyKeyboardRemove())

    query.answer()


def saveEntry(update, context, callData):
    global ongoingCreation

    query = update.callback_query

    entry = ongoingCreation[callData]

    diary = get_user_diary(callData)

    entry.number = diary.next_entry_number()

    get_user_diary(callData).add_entry(entry)

    del ongoingCreation[callData]

    logger.debug("Added: %s", entry)

    query.edit_message_text(text='Entry has been added with ID: ' + str(entry.number))

    query.answer()


actionList['saveEntry'] = saveEntry
actionList['rejectEntry'] = rejectEntry
actionList['doNothing'] = doNothing

getLastNEntries_handler = CommandHandler('get', getEntryById)
dispatcher.add_handler(getLastNEntries_handler)

addEntryByCommand_handler = CommandHandler('add', addEntryByCommand)
dispatcher.add_handler(addEntryByCommand_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

addTags_handler = CommandHandler('tags', addTags)
dispatcher.add_handler(addTags_handler)

addEntry_handler = MessageHandler(Filters.text, addEntry)
dispatcher.add_handler(addEntry_handler)

addImage_handler = MessageHandler(Filters.photo, addImage)
dispatcher.add_handler(addImage_handler)

updater.dispatcher.add_handler(CallbackQueryHandler(callbackHandler))

updater.start_polling()
