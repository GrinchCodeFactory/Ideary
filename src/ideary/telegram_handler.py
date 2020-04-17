import json
import logging
from typing import Dict

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, CallbackQuery
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater, CallbackQueryHandler

from src.ideary import read_conf, telegram_util, now
from src.ideary.diary import DiaryEntry
from src.ideary.media import get_media_content_stream
from src.ideary.storage import get_user_diary

conf = read_conf()['telegram']

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

updater = Updater(token=conf['token'], use_context=True)
dispatcher = updater.dispatcher

ongoingCreation: Dict[int, DiaryEntry] = {}


def testAction(data):
    print(str(data))


actionList = {'test': testAction}


def help(update, context):
    lines = ["I am your diary!",
             "Here are the rules:",
             "1. Don't lie to me",
             "2. Try to add 1 entry per day",
             "To add an entry type /add {text}",
             "To get an entry type /get {id}"]
    chat_id = update.effective_chat.id
    for line in lines:
        context.bot.send_message(chat_id=chat_id, text=line)


def get_creating_entry(chat_id: int) -> DiaryEntry:
    if chat_id not in ongoingCreation:
        text = ''
        diary = get_user_diary(chat_id)
        entry = DiaryEntry(
            number=diary.next_entry_number(),
            text=text,
            timestamp=now(),
            diary_id=diary.diary_id,
        )
        ongoingCreation[chat_id] = entry

    return ongoingCreation[chat_id]


def submit_creating_entry(chat_id: int, context):
    if not chat_id in ongoingCreation:
        return None
    entry = ongoingCreation[chat_id]
    get_user_diary(chat_id).add_entry(entry)

    logger.debug("Added: %s", entry)
    context.bot.send_message(chat_id=chat_id, text='Added entry #%d !' % entry.number)

    del ongoingCreation[chat_id]
    return entry


def getEntryById(update, context:CallbackQuery):
    chatID = update.effective_chat.id
    # 5: because of command length
    n = update.message.text[5:]

    if n.isdigit():
        n = int(n)
        entry = get_user_diary(chatID).get_entry(n)
        if entry.image:
            with get_media_content_stream(entry.image) as fh:
                context.bot.send_photo(chat_id=chatID, photo=fh, caption=entry.text)
        context.bot.send_message(chat_id=update.effective_chat.id, text=str(entry))
    else:
        logger.debug('Passed id is NOT a number')
        context.bot.send_message(chat_id=update.effective_chat.id, text='Passed ID is NOT a number')


def addText(update, context):
    chatID = update.effective_chat.id
    get_creating_entry(chatID).text = update.message.text
    sendReply(update, context)


def addImage(update, context):
    global ongoingCreation

    chatID = update.effective_chat.id
    photoId = update.message.photo[-1].file_id
    file = context.bot.getFile(photoId)

    entry = get_creating_entry(chatID)
    entry.image = telegram_util.store_photo(file, user_id=chatID)

    sendReply(update, context)


def addTags(update, context):
    global ongoingCreation

    chatID = update.effective_chat.id

    entry = get_creating_entry(chatID)
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

    chat_id = update.effective_chat.id
    del ongoingCreation[chat_id]

    logger.debug("removed entry with key: " + str(chat_id))

    query.edit_message_text(text='Entry deleted!: ', reply_markup=ReplyKeyboardRemove())
    query.answer()


def addEntryByCommand(update, context):
    chatID = update.effective_chat.id
    text = update.message.text[5:]
    get_creating_entry(chatID).text = text
    submit_creating_entry(chatID, context=context)


def saveEntry(update, context, callData):
    chat_id = update.effective_chat.id
    entry = submit_creating_entry(chat_id, context=context)
    if not entry:
        context.bot.send_message(text='What would you like to add?')


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

addEntry_handler = MessageHandler(Filters.text, addText)
dispatcher.add_handler(addEntry_handler)

addImage_handler = MessageHandler(Filters.photo, addImage)
dispatcher.add_handler(addImage_handler)

updater.dispatcher.add_handler(CallbackQueryHandler(callbackHandler))

updater.start_polling()
