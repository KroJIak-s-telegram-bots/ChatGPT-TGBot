#import pip
#pip.main(['install', 'seleniumwire', 'selenium', 'fake_useragent', 'aiogram'])

from background import keep_alive

from aiogram import Bot, Dispatcher, executor, types
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent
from time import sleep, time
import os


#SETTINGS
telegramToken = '5924249688:AAH_ApBfEgzoEqCgcXZCDp5QUrizHCmbDcw'
bot = Bot(telegramToken)
dp = Dispatcher(bot=bot)
data = {}
curIdSession = -1
secretKey = 'ILoveYourMom'
options = webdriver.ChromeOptions()
options.add_argument(f'user-agent={UserAgent().random}')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
mainUrl = 'https://chat.forefront.ai/'

addToClipBoard = lambda text: os.system(f'echo {text.strip()}| clip')

def getFromXPATH(count, typeObject, fr, names, mObject='driver', level='all'):
    if mObject == 'driver': mObject = driver
    if level == 'all': slash = '//'
    elif level == 'single': slash = './'
    else: return None
    if count == 'list': return list(mObject.find_elements(By.XPATH, f'{slash}{typeObject}[@{fr}="{names}"]'))
    elif count == 'alone': return mObject.find_element(By.XPATH, f'{slash}{typeObject}[@{fr}="{names}"]')
    else: return None

def sendPrompt(prompt):
    inputPrompts = getFromXPATH('alone', 'div', 'data-slate-node', 'element')
    addToClipBoard(prompt)
    actions = ActionChains(driver)
    actions.click(inputPrompts)
    actions.key_down(Keys.CONTROL)
    actions.send_keys('v')
    actions.key_up(Keys.CONTROL)
    actions.send_keys(Keys.ENTER)
    actions.perform()

def checkPermUser(id, text):
    global data
    if id not in data:
        if text == secretKey or id in [1250991011, 418428404]:
            data[id] = {
                'hasChat': False
            }
            if id in [1250991011, 418428404]: return 1
            return 0
        else: return -1
    return 1

def getUserInfo(message): return [message.from_user.id,
                                  message.from_user.first_name,
                                  message.from_user.full_name,
                                  message.text]

#COMMANDS
@dp.message_handler(commands=['start', 'about'])
async def startHandler(message: types.Message):
    userId, userName, userFullName, userText = getUserInfo(message)
    if userId in data: await message.reply(f'Привет, {userName}! Я гей. Меня кста создал самый лучший разработчик(@krojiak).', reply=False)
    else: await message.reply('Enter secret key:', reply=False)

@dp.message_handler(commands=['commands'])
async def commandsHandler(message: types.Message):
    userId, userName, userFullName, userText = getUserInfo(message)
    if userId in data: await message.reply('Команды: \n'
                                            '/about - обо мне \n'
                                            '/wwc',
                                            '/photo - сделать скриншот сайта',
                                            '/clear - очистить диалог',
                                            reply=False)
    else: await message.reply('Enter secret key:', reply=False)

@dp.message_handler(commands=['wwc'])
async def wwcHandler(message: types.Message):
    await message.reply(f'what \n\n\n\n\n\n\n\n\n\n who\n\n\n\n\n\n\n\n\n\n\n     caaaares', reply=False)

@dp.message_handler(commands=['photo'])
async def photoHandler(message: types.Message):
    userId, userName, userFullName, userText = getUserInfo(message)
    if userId in data:
        screen = driver.get_screenshot_as_png()
        await message.reply_photo(screen, reply=False)
    else: await message.reply('Enter secret key:', reply=False)

@dp.message_handler(commands=['clear'])
async def clearHandler(message: types.Message):
    userId, userName, userFullName, userText = getUserInfo(message)
    resCheck = checkPermUser(userId, userText)
    if resCheck == -1: await message.reply('No.', reply=False)
    elif resCheck == 0: await message.reply('Yes.', reply=False)
    elif resCheck == 1:
        data[userId]['hasChat'] = False
        data[userId]['nameChat'] = None
        await message.reply('Диалог очищен.', reply=False)

@dp.message_handler()
async def mainHandler(message: types.Message):
    global curIdSession
    userId, userName, userFullName, userText = getUserInfo(message)
    print(userId, userName, userFullName, userText)
    print(f'curIdSession: {curIdSession}')
    resCheck = checkPermUser(userId, userText)
    if resCheck == -1: await message.reply('No.', reply=False)
    elif resCheck == 0: await message.reply('Yes.', reply=False)
    elif resCheck == 1:
        if curIdSession == userId and data[userId]['hasChat']:
            print('stay')

            answersBefore = getFromXPATH('list', 'div', 'class', 'post-markdown flex flex-col gap-4 text-th-primary-dark text-base')
            sendPrompt(userText)
            firstMessage = True
            oldResAnswer = ''
            countButtonShare, delay = 0, 0
            while countButtonShare == 0 or time() < delay:
                try:
                    countButtonShare = len(getFromXPATH('list', 'p', 'class', 'text-sm font-medium whitespace-nowrap '))
                    answers = getFromXPATH('list', 'div', 'class', 'post-markdown flex flex-col gap-4 text-th-primary-dark text-base')
                    if len(answers) > len(answersBefore):
                        answer = [x for x in answers if x not in answersBefore]
                        resAnswer = answer[0].get_attribute('textContent')
                        if oldResAnswer != resAnswer:
                            delay = time() + 3
                            panelsCode = getFromXPATH('list', 'div', 'class', 'text-th-background-secondary opacity-100 flex bg-th-code-secondary px-4 justify-between items-center gap-2 py-1')
                            if len(panelsCode) > 0:
                                for panel in panelsCode:
                                    repText = panel.get_attribute('textContent')
                                    resAnswer = resAnswer.replace(repText, '\n')
                            if firstMessage:
                                sent_message = await message.reply(resAnswer, reply=False)
                                firstMessage = False
                            else: await bot.edit_message_text(chat_id=message.chat.id, message_id=sent_message.message_id, text=resAnswer)
                            oldResAnswer = resAnswer
                except: pass

        elif not data[userId]['hasChat']:
            print('new')

            newChatButtons = getFromXPATH('alone', 'button', 'class', 'cursor-pointer w-full rounded bg-transparent shadow text-th-primary-medium border border-th-border-secondary hover:bg-th-background-hover hover:border-th-primary-light hover:text-th-primary-dark flex gap-[6px] items-center justify-center py-[6px]')
            newChatButtons.click()

            answersBefore = getFromXPATH('list', 'div', 'class', 'post-markdown flex flex-col gap-4 text-th-primary-dark text-base')
            sendPrompt(userText)
            firstMessage = True
            oldResAnswer = ''
            countButtonShare, delay = 0, 0
            while countButtonShare == 0 or time() < delay:
                try:
                    countButtonShare = len(getFromXPATH('list', 'p', 'class', 'text-sm font-medium whitespace-nowrap '))
                    answers = getFromXPATH('list', 'div', 'class', 'post-markdown flex flex-col gap-4 text-th-primary-dark text-base')
                    if len(answers) > len(answersBefore):
                        answer = [x for x in answers if x not in answersBefore]
                        resAnswer = answer[0].get_attribute('textContent')
                        if oldResAnswer != resAnswer:
                            delay = time() + 3
                            panelsCode = getFromXPATH('list', 'div', 'class', 'text-th-background-secondary opacity-100 flex bg-th-code-secondary px-4 justify-between items-center gap-2 py-1')
                            if len(panelsCode) > 0:
                                for panel in panelsCode:
                                    repText = panel.get_attribute('textContent')
                                    resAnswer = resAnswer.replace(repText, '\n')
                            if firstMessage:
                                sent_message = await message.reply(resAnswer, reply=False)
                                firstMessage = False
                            else: await bot.edit_message_text(chat_id=message.chat.id, message_id=sent_message.message_id, text=resAnswer)
                            oldResAnswer = resAnswer
                except: pass

            actions = ActionChains(driver)
            divFolders = getFromXPATH('alone', 'div', 'class', 'group flex px-4 py-2')
            actions.move_to_element(divFolders)
            actions.perform()
            newFolderButton = getFromXPATH('alone', 'div', 'class', 'relative', mObject=divFolders, level='single')
            newFolderButton.click()
            sleep(1)
            listChats = getFromXPATH('alone', 'ul', 'role', 'list')
            choiceFolder = getFromXPATH('list', 'div', 'class', 'flex gap-2', mObject=listChats)
            while len(choiceFolder) == 0: getFromXPATH('list', 'div', 'class', 'flex gap-2', mObject=listChats)
            sleep(1)
            choiceFolderIn = getFromXPATH('list', 'div', 'class', 'relative', mObject=choiceFolder[0], level='single')
            choiceFolderIn[1].click()
            sleep(1)
            optionsFolder = getFromXPATH('alone', 'div', 'class', 'pl-4 pr-2 flex items-center gap-1 justify-center absolute right-0 h-full')
            optionsFolder.click()
            buttonsDeleteFolder = getFromXPATH('alone', 'li', 'class', 'flex gap-[6px] text-th-primary-medium hover:text-th-primary-dark items-center p-1 cursor-pointer hover:bg-th-background-hover text-xs px-3 py-2 ')
            buttonsDeleteFolder.click()
            sleep(1)

            tabChat = getFromXPATH('alone', 'div', 'class', 'group relative min-w-[200px] max-w-[200px] h-[36px] py-2 px-4 flex items-center gap-2 cursor-pointer bg-th-background')
            chats = getFromXPATH('list', 'li', 'role', 'listitem')
            for i, chat in enumerate(chats):
                #print(chat.get_attribute('textContent'), tabChat.get_attribute('textContent'))
                if chat.get_attribute('textContent') == tabChat.get_attribute('textContent'):
                    data[userId]['hasChat'] = True
                    optionsChat = getFromXPATH('list', 'div', 'class', 'pl-4 pr-2 flex items-center gap-1 justify-center absolute right-0 h-full')
                    optionsChat[i].click()
                    buttonRenameChat = getFromXPATH('alone', 'li', 'class', 'flex gap-2 text-th-primary-medium hover:text-th-primary-dark items-center cursor-pointer hover:bg-th-background-hover font-medium text-xs px-3 py-2 border-b border-th-border-secondary', mObject=chat)
                    buttonRenameChat.click()
                    inputRenameChat = getFromXPATH('alone', 'input', 'class', 'text-th-primary-medium bg-inherit text-xs whitespace-nowrap flex-1 overflow-hidden outline-none', mObject=chat)
                    actions = ActionChains(driver)
                    actions.click(inputRenameChat)
                    actions.key_down(Keys.CONTROL)
                    actions.send_keys('a')
                    actions.key_up(Keys.CONTROL)
                    actions.key_up(Keys.DELETE)
                    actions.perform()
                    inputRenameChat.send_keys(userId)
                    choiceFolder = getFromXPATH('alone', 'div', 'class', 'flex gap-2', mObject=chat)
                    choiceFolderIn = getFromXPATH('list', 'div', 'class', 'relative', mObject=choiceFolder, level='single')
                    choiceFolderIn[0].click()
                    sleep(1)
                    break
        else:
            print('swap')

            chats = getFromXPATH('list', 'li', 'role', 'listitem')
            chatExists = False
            for chat in chats:
                print(chat.get_attribute('textContent'), userId)
                if chat.get_attribute('textContent') == str(userId):
                    chat.click()
                    chatExists = True
            sleep(1)

            if chatExists:
                answersBefore = getFromXPATH('list', 'div', 'class', 'post-markdown flex flex-col gap-4 text-th-primary-dark text-base')
                sendPrompt(userText)
                firstMessage = True
                oldResAnswer = ''
                countButtonShare, delay = 0, 0
                while countButtonShare == 0 or time() < delay:
                    try:
                        countButtonShare = len(getFromXPATH('list', 'p', 'class', 'text-sm font-medium whitespace-nowrap '))
                        answers = getFromXPATH('list', 'div', 'class', 'post-markdown flex flex-col gap-4 text-th-primary-dark text-base')
                        if len(answers) > len(answersBefore):
                            answer = [x for x in answers if x not in answersBefore]
                            resAnswer = answer[0].get_attribute('textContent')
                            if oldResAnswer != resAnswer:
                                delay = time() + 3
                                panelsCode = getFromXPATH('list', 'div', 'class', 'text-th-background-secondary opacity-100 flex bg-th-code-secondary px-4 justify-between items-center gap-2 py-1')
                                if len(panelsCode) > 0:
                                    for panel in panelsCode:
                                        repText = panel.get_attribute('textContent')
                                        resAnswer = resAnswer.replace(repText, '\n')
                                if firstMessage:
                                    sent_message = await message.reply(resAnswer, reply=False)
                                    firstMessage = False
                                else: await bot.edit_message_text(chat_id=message.chat.id, message_id=sent_message.message_id, text=resAnswer)
                                oldResAnswer = resAnswer
                    except: pass
                sleep(1)
            else:
                await message.reply('Сори, я потерял твой чат :P', reply=False)
                return None

        curIdSession = userId

def main():
    driver.get(mainUrl)
    waitListChats = 0
    while waitListChats == 0: waitListChats = len(getFromXPATH('list', 'img', 'class', 'object-cover rounded'))
    selectModel = Select(getFromXPATH('alone', 'select', 'id', 'model-select'))
    selectModel.select_by_visible_text('GPT-3.5')
    optionsChats = getFromXPATH('list', 'div', 'class', 'pl-4 pr-2 flex items-center gap-1 justify-center absolute right-0 h-full')
    print(f'Count chats: {len(optionsChats)}')
    for optionsChat in optionsChats:
        optionsChat.click()
        buttonsDeleteChat = getFromXPATH('list', 'li', 'class', 'flex gap-[6px] text-th-primary-medium hover:text-th-primary-dark items-center cursor-pointer hover:bg-th-background-hover font-medium text-xs px-3 py-2 ')
        buttonsDeleteFolder = getFromXPATH('list', 'li', 'class', 'flex gap-[6px] text-th-primary-medium hover:text-th-primary-dark items-center p-1 cursor-pointer hover:bg-th-background-hover text-xs px-3 py-2 ')
        buttonsDelete = buttonsDeleteChat+buttonsDeleteFolder
        buttonsDelete[0].click()
    sleep(1)
    print('Browser is ready!')
    executor.start_polling(dp)

if __name__ == '__main__':
    keep_alive()
    driver = webdriver.Chrome(options=options)
    main()
