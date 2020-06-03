from telegram.ext import Updater, CommandHandler
import psycopg2
import logging
import os
# logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


REQUEST_KWARGS={
    'proxy_url': 'socks5://127.0.0.1:9050',
    }


mode = os.getenv("WORKTYPE")
token = os.getenv("TOKEN")

updater = Updater(token, use_context=True)
'''
If we use use_context=True in Updater, we should pass arguments to the function this way:
def greet_user(`update: Update, context: CallbackContext`):
    update.message.reply_text('hello')
'''


class Connect:
    def __init__(self, host, database, user, password):
        self = psycopg2.connect(host=host, database=database, user=user, password=password)




def run(updater):
    global conn, cur
    if mode == 'local':
        try:
            updater.start_polling()
            print("Connecting to Database")
            conn = psycopg2.connect(host="localhost", database="telbotdb", user="telbot", password="telbotpass")
            cur = conn.cursor()
            print("Connected")
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
    elif mode == 'host':
        try:
            PORT = int(os.environ.get("PORT", "8443"))
            HEROKU_APP_NAME = os.environ.get("HEROKKU__APP_NAME")
            updater.start_webhook(listen="0.0.0.0",
                                  port=PORT,
                                  url_path=token)
            updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, token))

            print("Connecting to host Database")
            conn = psycopg2.connect(host="ec2-54-243-252-232.compute-1.amazonaws.com",
                                    database="deni53okj1kfg0",
                                    user="slwywneiwysvah",
                                    password="81f78c5ae27dcbbf381e572dfb257b9a41c01c2f3952a3280fad77cb70e7ff59")
            cur = conn.cursor()
            print("Connected host database")
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
    else:
        logger.error("Mode is has not een set")





# ------------------------------------------------------------------


def close(update, context):
    if conn is not None:
        conn.close()
        print("Connection Closed")
    update.message.reply_text('connection closed')


# -----------------------------------------------------------------


def connect(update, context):
 #   chat_id = update.message.chat.id
 #   bot.sendMessage(chat_id, 'salam')
    cur.execute('SELECT version()')
    db_version = cur.fetchone()
    update.message.reply_text(str(db_version) + '/close')

def start(update, context):
    logger.info("User {} started bot".format(update.effective_user["id"]))
    update.message.reply_text('good start')


run(updater)
start_command = CommandHandler('start', start)
connect_command = CommandHandler('connect', connect)
finish_command = CommandHandler('close', close)
updater.dispatcher.add_handler(start_command)
updater.dispatcher.add_handler(connect_command)
updater.dispatcher.add_handler(finish_command)
updater.dispatcher.add_error_handler(error)

updater.idle()


