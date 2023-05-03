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
dialogue = []
pronoun = 'Пасасинтос'
phrase = 'ERROR не отвечаю'
character = ''

def getUserInfo(message): return [message.from_user.id,
                                  message.from_user.first_name,
                                  message.from_user.full_name,
                                  clearText(message.text)]

#COMMANDS
@dp.message_handler(commands=['start'])
async def startHandler(message: types.Message):
    userId, userName, userFullName, text = getUserInfo(message)
    logging.info(f'<{asctime()}> [{userId}|{userFullName}]: {text}')
    await message.reply(f'Привет, {userName}! Я самый лучший бот, который обращается к ChatGPT запросами. Я работаю на полною катушку, так что не суди если ответ приходит долго или он зациклился. Меня кста создал самый лучший разработчик(@krojiak).', reply=False)

@dp.message_handler(commands=['clear'])
async def clearHandler(message: types.Message):
    global dialogue
    userId, userName, userFullName, text = getUserInfo(message)
    logging.info(f'<{asctime()}> [{userId}|{userFullName}]: {text}')
    try: dialogue = []
    except: pass
    await message.reply('Диалог очищен.')

@dp.message_handler(commands=['сharacter'])
async def setCharacterHandler(message: types.Message):
    global character
    userId, userName, userFullName, text = getUserInfo(message)
    if len(text.split()) > 1:
        text = ' '.join(text.split()[1:])
        if not text[-1] in ['.', '?', '!']: text += '.'
        character = text
        logging.info(f'<{asctime()}> [{userId}|{userFullName}] SET CHARACTER: {text}')
        await message.reply('Личность установлена.')
    else: await message.reply('Личность НЕ установлена.')

@dp.message_handler()
async def askHandler(message: types.Message):
    global dialogue
    userId, userName, userFullName, text = getUserInfo(message)
    logging.info(f'<{asctime()}> [{userId}|{userFullName}] TO BOT: {text}')
    if not text[-1] in ['.', '?', '!']: text += '.'
    dialogue.append([userFullName, text])
    temp = True
    while temp:
        question = f'Тебя зовут {pronoun}. {character} Ты человек и не знаешь собеседников, но можешь познакомиться с ними во время общения. У тебя есть два важных условия при общении:\n' \
                   f'1. Если в фразе собеседника нет упоминания твоего имени, то ты отвечаешь исключительно "{phrase}" без дополнительных фраз и почему.\n' \
                   '2. Если в фразе собеседника есть точное упоминание твоего имени, то ты отвечаешь на его сообщение.\n' \
                   'Продолжай диалог:\n'
        for i, data in enumerate(dialogue): question += f'{data[0]} сказал: {data[1]}\n'
        question += f'{pronoun} сказал: '
        try:
            answer = ask(question)
            if phrase not in answer:
                #print(question+answer)
                dialogue.append([pronoun, clearText(answer)])
                logging.info(f'<{asctime()}> BOT TO [{userId}|{userFullName}]: {clearText(answer)}')
                await message.reply(answer)
            else: logging.info(f'<{asctime()}> BOT TO [{userId}|{userFullName}]: DONT TALKING')
            temp = False
        except:
            dialogue = dialogue[1:]
            logging.info(f'<{asctime()}> BOT TO [{userId}|{userFullName}]: ERROR-LIMIT')
            if len(dialogue) == 0:
                await message.reply('Упс, я призадумался. Напиши ещё раз.')
                temp = False

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