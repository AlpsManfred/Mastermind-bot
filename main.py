from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext, \
    CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from simple_bot import SimpleBot
from utils import to_byte_array
from advanced_bot import AdvancedBot
from text_utils import create_text
import pymorphy2

TOKEN = '1714855501:AAHe0feLA42F36y-3luseYthox3gadVF5Rk'
max_num_moves = 10
wikipedia = 'https://ru.wikipedia.org/wiki/%D0%91%D1%8B%D0%BA%D0%B8_%D0%B8_%D0%BA%D0%BE%D1%80%D0%BE%D0%B2%D1%8B'

keyboard = [
    [
        InlineKeyboardButton("Классический", callback_data='1'),
        InlineKeyboardButton("Обычный", callback_data='2'),
        InlineKeyboardButton("Продвинутый", callback_data='3')
    ],
    [InlineKeyboardButton("Правила", url=wikipedia)],
]

morph = pymorphy2.MorphAnalyzer()
move_word = morph.parse('ходы')[0]


def reply(update, context):
    bot = context.user_data.get('bot')
    if bot:
        reply_image(update, context)
        return
    update.message.reply_text('Если хотите начать игру заново, напишите /start.')


def button(update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    message = query.data
    if message == '1':
        bot = SimpleBot(9, 4, False)
    elif message == '2':
        bot = SimpleBot(6, 4, True)
    elif message == '3':
        bot = AdvancedBot(8, 5, True)

    context.user_data['bot'] = bot
    context.user_data['moves'] = []

    query.edit_message_text(bot.get_greeting())


def reply_image(update, context):
    bot = context.user_data['bot']
    msg = to_byte_array(update.message.text, bot.num_symbols, bot.num_colors, bot.repetition)
    if type(msg) == str:
        update.message.reply_text(msg)
        return
    answer = bot.get_answer(msg)
    context.user_data['moves'].append((msg, answer))
    text = create_text(context.user_data['moves'])
    if answer[0] == bot.num_symbols:
        update.message.reply_text(f'{text}\n\nПоздравляю, вы угадали! Игра окончена.'
                                  )
        context.user_data.clear()
    else:
        if len(context.user_data['moves']) >= max_num_moves:
            update.message.reply_text(f'{text}\n\nВы проиграли!'
                                      )
            context.user_data.clear()
        else:
            left_moves = max_num_moves - len(context.user_data["moves"])
            left_moves_word = move_word.make_agree_with_number(left_moves).word
            update.message.reply_text(f'{text}\n\nУ Вас осталось {left_moves} {left_moves_word}.'
                                      )


def start(update, context: CallbackContext):
    context.user_data.clear()
    update.message.reply_text('Выберите режим игры:',
                              reply_markup=InlineKeyboardMarkup(keyboard,
                                                                one_time_keyboard=True))


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    text_handler = MessageHandler(Filters.text, reply)
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(text_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
