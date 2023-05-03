import openai
import logging
from time import asctime
from aiogram import Bot, Dispatcher, executor, types

#SETTINGS
openai.api_key = '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'
telegramToken = '6158220173:AAHSh7A6x4FhGFrpLeBKFjirCWTEMFKVrgE'
logging.basicConfig(level=logging.INFO)
bot = Bot(telegramToken)
dp = Dispatcher(bot=bot)
temp = 0.1
maxTokens= 2500

def getUserInfo(message): return [message.from_user.id,
                                  message.from_user.first_name,
                                  message.from_user.full_name,
                                  message.text]

#COMMANDS
@dp.message_handler(commands=['start'])
async def startHandler(message: types.Message):
    userId, userName, userFullName, text = getUserInfo(message)
    logging.info(f'<{asctime()}> [{userId}|{userFullName}]: {text}')
    await message.reply(f'Привет, {userName}! Я второй самый лучший бот, который обращается к ChatGPT запросами. Я работаю на полною катушку, так что не суди если ответ приходит долго или он зациклился. Меня кста создал самый лучший разработчик(@krojiak). Если ты хочешь очистить диалог, напиши команду /clear', reply=False)

@dp.message_handler()
async def askHandler(message: types.Message):
    userId, userName, userFullName, text = getUserInfo(message)
    logging.info(f'<{asctime()}> [{userId}|{userFullName}] TO BOT: {text}')
    try:
        answer = ask(text)
        await message.reply(answer, reply=False)
    except:
        await message.reply('Извините, я призадумался. Повторите ещё раз.', reply=False)

#CHATGPT
def ask(pmt):
    completion = openai.Completion.create(engine='code-davinci-002',
                                          prompt=pmt,
                                          temperature=temp,
                                          max_tokens=maxTokens)
    return completion.choices[0]['text']

if __name__ == '__main__':
    executor.start_polling(dp)