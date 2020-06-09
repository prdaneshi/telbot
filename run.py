from telegram.ext import Updater, CommandHandler
from telegram import bot
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
global conn, cur
conn = None


updater = Updater(token, use_context=True)
'''
If we use use_context=True in Updater, we should pass arguments to the function this way:
def greet_user(`update: Update, context: CallbackContext`):
    update.message.reply_text('hello')
'''


def run(updater):
    if mode == 'local':
        updater.bot.set_webhook()
        updater.start_polling()
    elif mode == 'host':
        try:
            PORT = int(os.environ.get("PORT", "8443"))
            HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
            updater.start_webhook(listen="0.0.0.0",
                                  port=PORT,
                                  url_path=token)
            updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, token))
        except Exception as error:
            print(error)
            logger.error(error)
    else:
        logger.error("Mode is has not een set")


# ------------------------------------------------------------------


def close(update, context):
    global conn
    if conn is not None:
        conn.close()
        conn = None
        print("Connection Closed")
        update.message.reply_text('connection closed')
    else:
        print("Already closed")
        update.message.reply_text("Already closed")


# -----------------------------------------------------------------


def createDb(update, context):
    try:
        cur.execute(''' 
    CREATE TABLE public."user"(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY,
    name "char" NOT NULL,
    birth smallint NOT NULL,
    city "char" NOT NULL,
    gender boolean NOT NULL,
    chatId integer NOT NULL,
    PRIMARY KEY (id) );
    ''')
        print("database created")
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)


def connect(update, context):
    global conn, cur
    if not conn:
        if mode == 'local':
            try:
                print("Connecting to local Database")
                conn = psycopg2.connect(host="localhost", database="telbotdb", user="telbot", password="telbotpass")
                cur = conn.cursor()
                print("Local database Connected")
            except(Exception, psycopg2.DatabaseError) as error:
                print(error)
        elif mode == 'host':
            try:
                print("Connecting to host Database")
                conn = psycopg2.connect(host="ec2-54-243-252-232.compute-1.amazonaws.com",
                                        database="deni53okj1kfg0",
                                        user="slwywneiwysvah",
                                        password="81f78c5ae27dcbbf381e572dfb257b9a41c01c2f3952a3280fad77cb70e7ff59")
                cur = conn.cursor()
                print("Host database connected")
            except(Exception, psycopg2.DatabaseError) as error:
                print(error)
                update.message.reply_text(error)
        else:
            logger.error("Mode has not been set")
            update.message.reply_text("Mode has not been set")
    else:
        print("Database has connected")
        update.message.reply_text("Database has connected")

    cur.execute('SELECT version()')
    db_version = cur.fetchone()
    update.message.reply_text(str(db_version) + '/close')


def creat(update, context):
    global cur
    cur.execute('SELECT version()')
    db_version = cur.fetchone()
    update.message.reply_text(str(db_version) + '/close')


def start(update, context):
    global cur
    update.message.reply_text('good start, what is your name?')
    cur.execute("ROLLBACK;")
    sql = "SELECT EXISTS (" \
          "SELECT FROM public.user " \
            "WHERE chatId = {} )"
    try:
        cur.execute(sql.format(update.message.chat.id))
        user = cur.fetchone()
        if False in user:
            update.message.reply_text("You are not a member")
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
        cur.execute("ROLLBACK;")
        update.message.reply_text(str(error))
    help(update, context)


def help(update, contex):
    update.message.reply_text('/help '
                              '/start '
                              '/connect '
                              '/close '
                              '/createDb ')

run(updater)
help_command =  CommandHandler('help', help)
start_command = CommandHandler('start', start)
connect_command = CommandHandler('connect', connect)
finish_command = CommandHandler('close', close)
create_command = CommandHandler('createDb', createDb)

updater.dispatcher.add_handler(help_command)
updater.dispatcher.add_handler(start_command)
updater.dispatcher.add_handler(connect_command)
updater.dispatcher.add_handler(finish_command)
updater.dispatcher.add_handler(create_command)

updater.dispatcher.add_error_handler(error)

updater.idle()


