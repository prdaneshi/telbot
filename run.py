from telegram.ext import Updater, CommandHandler
import psycopg2
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


REQUEST_KWARGS={
    'proxy_url': 'socks5://127.0.0.1:9050',
    }

updater = Updater('1168577282:AAF6gv-0KG4ZCiTMykR8X_vW9GLee07g1W8', use_context=True)
'''
If we use use_context=True in Updater, we should pass arguments to the function this way:
def greet_user(`update: Update, context: CallbackContext`):
    update.message.reply_text('hello')
'''

conn = None

# ------------------------------------------------------------------


def connect():
    try:
        print("Connecting to Database")
        conn = psycopg2.connect(host="localhost", database="telbotdb", user="telbot", password="telbotpass")
        global cur
        cur = conn.cursor()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)


def close(update, context):
    if conn is not None:
        conn.close()
        print("Connection Closed")
    update.message.reply_text('connection closed')


# -----------------------------------------------------------------


def start(update, context):
    connect()
 #   chat_id = update.message.chat.id
 #   bot.sendMessage(chat_id, 'salam')
    cur.execute('SELECT version()')
    db_version = cur.fetchone()
    update.message.reply_text(str(db_version) + '/close')


start_command = CommandHandler('connect', start)
finish_command = CommandHandler('close', close)
updater.dispatcher.add_handler(start_command)
updater.dispatcher.add_handler(finish_command)
updater.dispatcher.add_error_handler(error)
updater.start_polling()
updater.idle()

