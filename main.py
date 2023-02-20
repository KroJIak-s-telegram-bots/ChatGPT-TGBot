import openai
import logging
from time import asctime
from aiogram import Bot, Dispatcher, executor, types

#SETTINGS
openai.api_key = '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'
telegramToken = '5924249688:AAH_ApBfEgzoEqCgcXZCDp5QUrizHCmbDcw'
logging.basicConfig(level=logging.INFO)
bot = Bot(telegramToken)
dp = Dispatcher(bot=bot)
temp = 0.1
maxTokens= 2000
startDialogue = 'Продолжи диалог.'
dialogues = {}

def getUserInfo(message): return [message.from_user.id,
                                  message.from_user.first_name,
                                  message.from_user.full_name,
                                  clearText(message.text)]

#COMMANDS
@dp.message_handler(commands=['start'])
async def startHandler(message: types.Message):
    userId, userName, userFullName, text = getUserInfo(message)
    logging.info(f'<{asctime()}> [{userId}|{userFullName}]: {text}')
    await message.reply(f'Привет, {userName}! Я самый лучший бот, который обращается к ChatGPT запросами. Я работаю на полною катушку, так что не суди если ответ приходит долго или он зациклился. Меня кста создал самый лучший разработчик(@krojiak). Если ты хочешь очистить диалог, напиши команду /clear', reply=False)

@dp.message_handler(commands=['clear'])
async def clearHandler(message: types.Message):
    userId, userName, userFullName, text = getUserInfo(message)
    logging.info(f'<{asctime()}> [{userId}|{userFullName}]: {text}')
    dialogues[int(userId)] = ''
    await message.reply('Диалог очищен.', reply=False)

@dp.message_handler()
async def askHandler(message: types.Message):
    userId, userName, userFullName, text = getUserInfo(message)
    logging.info(f'<{asctime()}> [{userId}|{userFullName}] TO BOT: {text}')
    curDialogue = f' Я написал: {text}'
    if not curDialogue[-1] in ['.', '?', '!']: curDialogue += '.'
    curDialogue += ' Ты написал: '
    try: dialogues[int(userId)] += curDialogue
    except: dialogues[int(userId)] = startDialogue + curDialogue
    try:
        answer = ask(dialogues[int(userId)], False)
        dialogues[int(userId)] += f'{clearText(answer)}'
        logging.info(f'<{asctime()}> BOT TO [{userId}|{userFullName}]: {answer}')
        await message.reply(answer, reply=False)
    except: await message.reply('Извините, я призадумался. Повторите ещё раз.', reply=False)


#CHATGPT
def ask(pmt, clear):
    completion = openai.Completion.create(engine='text-davinci-003',
                                          prompt=pmt,
                                          temperature=temp,
                                          max_tokens=maxTokens)
    return completion.choices[0]['text']

clearText = lambda text: ' '.join(text.replace('\n', ' ').split())

if __name__ == '__main__':
    executor.start_polling(dp)