from correctPathModule import getCorrectPathByPyScript
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from database import dbWorker
from configparser import ConfigParser
import logging
import asyncio
import json
import openai
# from background import keep_alive

MAIN_PATH = getCorrectPathByPyScript(__file__)

# SETTINGS
logging.basicConfig(level=logging.INFO)
config = ConfigParser()
config.read(f'{MAIN_PATH}/config.ini')
token = config['Telegram']['token']
alias = config['Telegram']['alias']
apiKey = config['ChatGPT']['apiKey']
model = config['ChatGPT']['model']
databaseFileName = config['Data']['databaseFileName']
rawAvailableLangs = config['Data']['availableLangs']
defaultLang = config['Data']['defaultLang']
availableLangs = rawAvailableLangs.split(', ')
secretKey = config['Data']['secretKey']

openai.api_key = apiKey
db = dbWorker(databaseFileName)
bot = Bot(token)
dp = Dispatcher()

def getTranslation(userId, name, inserts=[], lang=None):
    if lang is None: nameLang = db.getFromUser(userId, 'lang')
    else: nameLang = lang
    with open(f'{MAIN_PATH}/lang/{nameLang}.json', encoding='utf-8') as langFile:
        langJson = json.load(langFile)
    text = langJson[name]
    if len(inserts) > 0:
        splitText = text.split('%{}%')
        resultText = splitText[0]
        for i, ins in enumerate(inserts, start=1):
            resultText += ins
            if i < len(splitText): resultText += splitText[i]
        return resultText
    else:
        return text

async def getResponseGPT(pmt):
    try:
      completion = openai.ChatCompletion.create(
          model=model,
          messages=[
              { 'role': 'user', 'content': pmt }
          ])
      return completion.choices[0].message.content
    except openai.error.RateLimitError:
      return 'TimeOut. Подождите несколько секунд перед следующим отправлением...'

def checkPermissions(userId, text):
    if db.isAdmin(userId):
        return True
    if text == secretKey:
        db.setInUser(userId, 'permission', 'admin')
        return True
    return False

def getUserInfo(message):
    userInfo = {'chatId': message.chat.id,
                'userId': message.from_user.id,
                'username': message.from_user.username,
                'userFirstName': message.from_user.first_name,
                'userFullName': message.from_user.full_name,
                'messageId': message.message_id,
                'userText': message.text}
    if not db.userExists(userInfo['userId']):
        db.addNewUser(userInfo['userId'], userInfo['username'], userInfo['userFullName'], defaultLang)
    print(' | '.join(list(map(str, userInfo.values()))))
    return userInfo

# COMMANDS
@dp.message(Command('start'))
async def startHandler(message: types.Message):
    global data
    userInfo = getUserInfo(message)
    await message.answer(getTranslation(userInfo['userId'], 'start.message', [userInfo['userFirstName']]))
    await message.answer(getTranslation(userInfo['userId'], 'permissons.getadminkey'))

@dp.message(Command('clear'))
async def clearHandler(message: types.Message):
    userInfo = getUserInfo(message)
    if not checkPermissions(userInfo['userId'], userInfo['userText']):
        await message.answer(getTranslation(userInfo['userId'], 'permissons.getadminkey'))
        return
    await message.answer(getTranslation(userInfo['userId'], 'clear.message'))

@dp.message()
async def mainHandler(message: types.Message):
    userInfo = getUserInfo(message)
    if not checkPermissions(userInfo['userId'], userInfo['userText']):
        await message.answer(getTranslation(userInfo['userId'], 'permissons.getadminkey'))
        return
    responseGPT = await getResponseGPT(userInfo['userText'])
    await message.answer(responseGPT)

async def mainTyping():
    while True:
        userIds = db.getUserIds()
        for userId in userIds:
            await bot.send_chat_action(userId, 'typing')
            await asyncio.sleep(1)

async def onStartupBot(): asyncio.create_task(mainTyping())

async def mainTelegram():
    dp.startup.register(onStartupBot)
    await dp.start_polling(bot)

if __name__ == '__main__':
    # keep_alive()
    asyncio.run(mainTelegram())
