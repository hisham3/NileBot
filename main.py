from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from NileBot.script import Course
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
    text = [f'# {session} - {seat} Left Seats\n' for session, seat in zip(info['session'], info['seats'])]

    if any(info['seats']):
        context.bot.send_message(chat_id=context.user_data['chat_id'], text=f'{course}\n{"".join(text)}\nopened: {info["opened"]}')

    if info['opened']:
        context.bot.send_message(chat_id=context.user_data['chat_id'], text=f'Hiiiiiiiiiiii Registeration is Opened.\n'*10)

def job(update, context):
    course_class = Course()
    course_class.log_in(context.user_data['username'], context.user_data['password'])
    context.bot.send_message(chat_id=update.callback_query.message.chat_id, text='session logged in and working now...')

    context.user_data.update({'course_class':course_class, 'chat_id':update.callback_query.message.chat_id})

    context.job_queue.run_repeating(course_repeating, interval=5, context=context)

def cancel(update, context):
    context.job_queue.stop()
    course_class = context.user_data['course_class']
    course_class.quit()
    context.bot.send_message(chat_id=update.message.chat_id, text='session ended.')

updater = Updater(os.environ.get('TOKEN'))
conversation = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        BACK_DATA: [MessageHandler(Filters.text & (~Filters.command), message)],
        JOB: [CallbackQueryHandler(job, pass_job_queue=True)]
    },
    fallbacks=[CommandHandler('cancel', cancel, pass_job_queue=True)]
)
updater.dispatcher.add_handler(conversation)
updater.start_polling()
updater.idle()

