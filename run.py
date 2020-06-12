from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
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


def createTb(update, context):
    try:
        cur.execute(''' 
    CREATE TABLE public."user"(
    id serial,
    name "char",
    birth smallint,
    city "char",
    gender boolean,
    chatId integer,
    PRIMARY KEY (id) );
    ''')
        print("database created")
    except(Exception, psycopg2.DatabaseError) as error:
        cur.execute("ROLLBACK;")
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


def deleteTb(update, context):
    global cur
    try:
        cur.execute("DROP TABLE public.user")
        print("DATABASE deleted")
        update.message.reply_text("DATABASE deleted")
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
        update.message.reply_text(str(error))
        cur.execute("ROLLBACK;")
    db_version = cur.fetchone()


def start(update, context):
    global cur
#    cur.execute("ROLLBACK;")
    sql = "SELECT EXISTS (" \
          "SELECT FROM public.user " \
          "WHERE chatId = {})"
    try:
        cur.execute(sql.format(update.message.chat.id))
        user = cur.fetchone()
        if False in user:
            # update.message.reply_text("{} welcome to our bot.\nplease send me your birth year\n and press next".format(update.message.chat.first_name))
            # keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
            #              InlineKeyboardButton("Option 2", callback_data='2')],
            #             [InlineKeyboardButton("Option 3", callback_data='3')]]
            keyboard = [
                [InlineKeyboardButton("Next", callback_data=1)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("{} welcome to our bot.\n"
                                      "press next if u want to join us".format(update.message.chat.first_name),
                                      reply_markup=reply_markup)
        else:
            keyboard = [
                [InlineKeyboardButton("Next", callback_data=2)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("{} welcome back to our bot.\n"
                                      "press next if u want to join us".format(update.message.chat.first_name),
                                      reply_markup=reply_markup)
        return 0

    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
        cur.execute("ROLLBACK;")
        update.message.reply_text(str(error))
    help(update, context)


def first(update, context):
    global cur
    if update.callback_query:
        query = update.callback_query
        if update.callback_query.data == '1':

            # keyboard = [
            #     [InlineKeyboardButton("Next", callback_data="2")]
            # ]
            # reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text="Good Choice")
            # query.edit_message_reply_markup(reply_markup=reply_markup)
            sql = "INSERT INTO public.user" \
                  "(name, chatid)" \
                  "VALUES" \
                  "('{}',{})"
            cur.execute(sql.format(str(query.message.chat.first_name), query.message.chat.id))
        # keyboard = [
        #     [KeyboardButton("Next", callback_data=str(SECOND))]
        # ]
        # reply_markup = ReplyKeyboardMarkup(keyboard)
        # query.edit_message_text(text="first CallbackQueryHandler")
        # query.bot.sendMessage(chat_id=query.message.chat.id,
        #                       text="send me your name and press next",
        #                        reply_markup=reply_markup)

            keyboard = [
                [InlineKeyboardButton("Next", callback_data=2)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.bot.sendMessage(chat_id=query.message.chat.id,
                                  text="Now send me your birth year\n"
                                  "and press next",
                                  reply_markup=reply_markup)
        elif update.callback_query.data == '2':
            query.edit_message_text(text="Nice to meet u")
            sql = "SELECT EXISTS (" \
                  "SELECT FROM public.user " \
                  "WHERE chatId = {}" \
                  "AND birth != NULL )"
            try:
                cur.execute(sql.format(query.message.chat.id))
                user = cur.fetchone()
                if False in user:
                    keyboard = [
                        [InlineKeyboardButton("Next", callback_data=3)]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    query.bot.sendMessage(chat_id=query.message.chat.id,
                                          text="{} it seems u dont entered your birth year.\n"
                                          "send me your birth year and then \n"
                                          "press next".format(query.message.chat.first_name),
                                          reply_markup=reply_markup)
            except(Exception, psycopg2.DatabaseError) as error:
                print(error)
                cur.execute("ROLLBACK;")
                update.message.reply_text(str(error))
        elif update.callback_query.data == '3':
            return 1

    elif update.message:
        try:
            if int(update.message.text) > 1300:
                sql = "UPDATE public.user " \
                      "SET birth = {} " \
                      "WHERE chatid = {};"
                cur.execute(sql.format(int(update.message.text), update.message.chat.id))
                cur.execute("COMMIT;")
                update.message.reply_text("Your birth saved!! :/")
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            cur.execute("ROLLBACK;")
            update.message.reply_text(str(error))
            update.message.reply_text("Ahmagh!! :/")
    else:
        update.message.reply_text("Wrong answer, please send me your birth year")


def second(update, context):
    query = update.callback_query
#    query.edit_message_text(text="Second CallbackQueryHandler")
    query.bot.sendMessage(chat_id=query.message.chat.id,
                          text="send me your name and press next")
    return


def help(update, context):
    update.message.reply_text('/help '
                              '/start '
                              '/connect '
                              '/deleteTb '
                              '/close '
                              '/createTb ')


run(updater)

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        0: [CallbackQueryHandler(first), MessageHandler(Filters.all, first)],
        1: [CallbackQueryHandler(second)]
    },
    fallbacks=[CommandHandler('start', start)]
)

help_command =  CommandHandler('help', help)
#start_command = CommandHandler('start', start)
delete_command = CommandHandler('deleteTb', deleteTb)
connect_command = CommandHandler('connect', connect)
finish_command = CommandHandler('close', close)
create_command = CommandHandler('createTb', createTb)

updater.dispatcher.add_handler(delete_command)
updater.dispatcher.add_handler(help_command)
#updater.dispatcher.add_handler(start_command)
updater.dispatcher.add_handler(connect_command)
updater.dispatcher.add_handler(finish_command)
updater.dispatcher.add_handler(create_command)

updater.dispatcher.add_error_handler(error)
updater.dispatcher.add_handler(conv_handler)

updater.idle()


