from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from script import Course
import os
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    ConversationHandler,
)

(
    BACK_DATA,
    JOB
) = map(str, range(0,2))

CHAT_ID = os.environ.get("GROUP_ID") #"-733347120"

last_status = {"courses": {}}

def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text='please enter input like: Username - Pass - Course')

    return BACK_DATA

def message(update, context):
    username, password, course = update.message.text.split('-')
    buttons = [[InlineKeyboardButton(text='Click to start', callback_data='start')]]
    text = f'username: {username}\npassword: {password}\ncourse: {course}'
    context.bot.send_message(chat_id=update.message.chat_id,text=text, reply_markup=InlineKeyboardMarkup(buttons))

    context.user_data.update({'username':username, 'password':password, 'course':course})
    return JOB

def course_repeating(context):
    context = context.job.context
    course = context.user_data['course']
    course_class = context.user_data['course_class']
    info = course_class.course_searching(course)

    for course_name in info['courses'].keys():
        if last_status['courses'].get(course_name) != info['courses'].get(course_name) and info['courses'].get(course_name) != []:
            text = [f'# {session} - {seat} Left Seats\n' for session, seat in info['courses'].get(course_name)]
            context.bot.send_message(chat_id=CHAT_ID if CHAT_ID else context.user_data['chat_id'], text=f'* {course_name}\n\n{"".join(text)}\nopened: {info["opened"]}')
            last_status['courses'][course_name] = info['courses'].get(course_name)

    # if info['opened']:
    #     print(f'Hiiiiiiiiiiii Registeration is Opened.\n'*10)

def job(update, context):
    course_class = Course()
    course_class.log_in(context.user_data['username'], context.user_data['password'])
    context.bot.send_message(chat_id=CHAT_ID if CHAT_ID else update.callback_query.message.chat_id, text='session logged in and working now...') #update.callback_query.message.chat_id

    context.user_data.update({'course_class':course_class, 'chat_id':update.callback_query.message.chat_id})

    context.job_queue.run_repeating(course_repeating, interval=10, context=context)

def cancel(update, context):
    context.job_queue.stop()
    course_class = context.user_data['course_class']
    course_class.quit()
    context.bot.send_message(chat_id=CHAT_ID if CHAT_ID else update.message.chat_id, text='session ended.')

updater = Updater(os.environ.get("TOKEN")) #r"2045989311:AAGkpZbW9RTBwi1ET2WlgCw0ymCa3bP_N18"
conversation = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        BACK_DATA: [MessageHandler(Filters.text & (~Filters.command), message)],
        JOB: [CallbackQueryHandler(job, pass_job_queue=True)]
    },
    fallbacks=[CommandHandler('cancel', cancel, pass_job_queue=True)],
    run_async=True)
updater.dispatcher.add_handler(conversation)
updater.start_polling()
updater.idle()

