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
maxTokens= 1200
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
    global dialogues
    userId, userName, userFullName, text = getUserInfo(message)
    logging.info(f'<{asctime()}> [{userId}|{userFullName}]: {text}')
    try: del dialogues[userId]
    except: pass
    await message.reply('Диалог очищен.', reply=False)

@dp.message_handler()
async def askHandler(message: types.Message):
    global dialogues
    userId, userName, userFullName, text = getUserInfo(message)
    logging.info(f'<{asctime()}> [{userId}|{userFullName}] TO BOT: {text}')
    if not text[-1] in ['.', '?', '!']: text += '.'
    try: dialogues[userId].append(text)
    except: dialogues[userId] = [text]
    temp = True
    while temp:
        question = 'Продолжи диалог.\n'
        for i, phrase in enumerate(dialogues[userId]):
            if i % 2 == 0: question += f'Я сказал: {phrase}\n'
            else: question += f'Ты сказал: {phrase}\n'
        question += 'Ты сказал:'
        try:
            answer = ask(question)
            dialogues[userId].append(clearText(answer))
            logging.info(f'<{asctime()}> BOT TO [{userId}|{userFullName}]: {clearText(answer)}')
            await message.reply(answer, reply=False)
            temp = False
        except:
            dialogues[userId] = dialogues[userId][2:]
            logging.info(f'<{asctime()}> BOT TO [{userId}|{userFullName}]: ERROR-LIMIT')

#CHATGPT
def ask(pmt):
    completion = openai.Completion.create(engine='text-davinci-003',
                                          prompt=pmt,
                                          temperature=temp,
                                          max_tokens=maxTokens)
    return completion.choices[0]['text']

clearText = lambda text: ' '.join(text.replace('\n', ' ').split())

if __name__ == '__main__':
    executor.start_polling(dp)