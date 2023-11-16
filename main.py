from correctPathModule import getCorrectPathByPyScript
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from database import dbWorker
from configparser import ConfigParser
import logging
import asyncio
import json
import g4f
from g4f import Provider
# from background import keep_alive
from random import choice

print(f'[G4F Version] {g4f.version}; Last: {g4f.version_check}')
MAIN_PATH = getCorrectPathByPyScript(__file__)

# SETTINGS
logging.basicConfig(level=logging.INFO)
config = ConfigParser()
config.read(f'{MAIN_PATH}/config.ini')
token = config['Telegram']['token']
alias = config['Telegram']['alias']
rawAvailableModels = config['GPT']['availableModels']
defaultModel = config['GPT']['defaultModel']
availableModels = rawAvailableModels.split(', ')
startSystemMessage = config['GPT']['startSystemMessage']
databaseFileName = config['Data']['databaseFileName']
rawAvailableLangs = config['Data']['availableLangs']
defaultLang = config['Data']['defaultLang']
availableLangs = rawAvailableLangs.split(', ')
secretKey = config['Data']['secretKey']

db = dbWorker(databaseFileName)
bot = Bot(token)
dp = Dispatcher()
providersGPT3_5 = [
    Provider.ChatForAi,
    Provider.GPTalk,
    Provider.AiAsk,
    Provider.Yqcloud
]


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

async def getResponseGPT(userId, messages, model):
    firstMessages = [{'role': 'system', 'content': startSystemMessage}]
    countAttempts = 0
    while True:
        countAttempts += 1
        try:
            if model == 'gpt-4': provider = None
            else: provider = choice(providersGPT3_5)
            response = await g4f.ChatCompletion.create_async(
                model=model,
                messages=firstMessages+messages,
                provider=provider
            )
            if len(response) < 4096: return response
        except Exception as err: print(f'[ERROR] {err}')
        if countAttempts > 10:
            db.setInUser(userId, 'messages', [])
            return getTranslation(userId, 'error.message')

def checkPermissions(userId, text):
    if db.isAdmin(userId):
        return 1
    if text == secretKey:
        db.setInUser(userId, 'messages', [])
        db.setInUser(userId, 'permission', 'admin')
        return 2
    return 0

def getTranslationChangeModel(userId, nameModel):
    nameKey = 'button.selected.model' if nameModel in db.getFromUser(userId, 'model') else 'button.unselected.model'
    return getTranslation(userId, nameKey,[nameModel])

def getMainKeyboard(userId):
  mainButtons = [[types.KeyboardButton(text=getTranslationChangeModel(userId, nameModel))] for nameModel in availableModels]
  mainButtons += [[types.KeyboardButton(text=getTranslation(userId, 'button.clear'))]]
  mainKeyboard = types.ReplyKeyboardMarkup(keyboard=mainButtons, resize_keyboard=True)
  return mainKeyboard

def getUserInfo(message, isCommand=False):
    userInfo = { 'chatId': message.chat.id,
                 'userId': message.from_user.id,
                 'username': message.from_user.username,
                 'userFirstName': message.from_user.first_name,
                 'userFullName': message.from_user.full_name,
                 'messageId': message.message_id,
                 'userText': message.text }
    if not db.userExists(userInfo['userId']):
        db.addNewUser(userInfo['userId'], userInfo['username'],
                      userInfo['userFullName'], defaultLang, defaultModel)
    elif not isCommand:
        db.addNewMessageInUser(userInfo['userId'], 'user', userInfo['userText'])
    print(' | '.join(list(map(str, userInfo.values()))))
    return userInfo

# COMMANDS
@dp.message(Command('start'))
async def startHandler(message: types.Message):
    userInfo = getUserInfo(message, isCommand=True)
    await message.answer(getTranslation(userInfo['userId'], 'start.message', [userInfo['userFirstName']]))
    if not checkPermissions(userInfo['userId'], userInfo['userText']):
        await message.answer(getTranslation(userInfo['userId'], 'permissons.getadminkey'), parse_mode='HTML')

def isChangleModelCommand(userText):
    return userText[2:-2] in availableModels

async def changleModelHandler(userInfo, message):
    await bot.delete_message(userInfo['userId'], userInfo['messageId'])
    db.removeLastMessageInUser(userInfo['userId'])
    db.setInUser(userInfo['userId'], 'model', userInfo['userText'][2:-2])
    mainKeyboard = getMainKeyboard(userInfo['userId'])
    await message.answer(getTranslation(userInfo['userId'], 'changemodel.message', [userInfo['userText'][2:-2]]), reply_markup=mainKeyboard, parse_mode='HTML')

def isClearCommand(userId, userText):
    return userText in ['/clear', f'/clear@{alias}', getTranslation(userId, 'button.clear')]

async def clearHandler(userInfo, message):
    await bot.delete_message(userInfo['userId'], userInfo['messageId'])
    db.setInUser(userInfo['userId'], 'messages', [])
    mainKeyboard = getMainKeyboard(userInfo['userId'])
    await message.answer(getTranslation(userInfo['userId'], 'clear.message'), reply_markup=mainKeyboard, parse_mode='HTML')

@dp.message(Command('send'))
async def sendHandler(message: types.Message):
    userInfo = getUserInfo(message, isCommand=True)
    if not checkPermissions(userInfo['userId'], userInfo['userText']):
        await message.answer(getTranslation(userInfo['userId'], 'permissons.getadminkey'))
        return
    recipUserData = userInfo['userText'].split()[1]
    allUserIds = db.getUserIds()
    for userId in allUserIds:
        userName = db.getFromUser(userId, 'username')
        if userName is not None and userName in recipUserData:
            recipUserId = userId
            break
    else: return
    recipText = ' '.join(userInfo['userText'].split()[2:])
    mainKeyboard = getMainKeyboard(userInfo['userId'])
    await bot.send_message(recipUserId, recipText, reply_markup=mainKeyboard, parse_mode='HTML')

@dp.message(Command('sendAll'))
async def sendAllHandler(message: types.Message):
    userInfo = getUserInfo(message, isCommand=True)
    if not checkPermissions(userInfo['userId'], userInfo['userText']):
        await message.answer(getTranslation(userInfo['userId'], 'permissons.getadminkey'))
        return
    recipText = ' '.join(userInfo['userText'].split()[1:])
    mainKeyboard = getMainKeyboard(userInfo['userId'])
    allUserIds = db.getUserIds()
    for userId in allUserIds:
        if db.isAdmin(userId):
            await bot.send_message(userId, recipText, reply_markup=mainKeyboard, parse_mode='HTML')

@dp.message()
async def mainHandler(message: types.Message):
    userInfo = getUserInfo(message)
    resultPermission = checkPermissions(userInfo['userId'], userInfo['userText'])
    if not resultPermission:
        await message.answer(getTranslation(userInfo['userId'], 'permissons.getadminkey'))
        return
    if resultPermission == 2: return

    if isChangleModelCommand(userInfo['userText']):
        await changleModelHandler(userInfo, message)
        return
    elif isClearCommand(userInfo['userId'], userInfo['userText']):
        await clearHandler(userInfo, message)
        return

    await bot.send_chat_action(userInfo['userId'], 'typing')
    mainKeyboard = getMainKeyboard(userInfo['userId'])
    botMessage = await message.answer(getTranslation(userInfo['userId'], 'sending.message'), reply_markup=mainKeyboard, parse_mode='HTML')
    curUserModel = db.getFromUser(userInfo['userId'], 'model')
    responseGPT = await getResponseGPT(userInfo['userId'], db.getFromUser(userInfo['userId'], 'messages'), model=curUserModel)
    if not responseGPT:
        db.removeLastMessageInUser(userInfo['userId'])
        return
    db.addNewMessageInUser(userInfo['userId'], 'bot', responseGPT)
    await bot.delete_message(userInfo['userId'], botMessage.message_id)
    await message.answer(responseGPT, reply_markup=mainKeyboard, parse_mode='HTML')

async def mainTelegram():
    await dp.start_polling(bot)

if __name__ == '__main__':
    # keep_alive()
    asyncio.run(mainTelegram())

