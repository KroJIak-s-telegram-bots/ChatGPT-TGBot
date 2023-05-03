from telebot import TeleBot, types
from threading import Thread
from queue import Queue
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
bot = TeleBot(telegramToken)
data = {}
size = (1920, 1080)
curIdSession = -1
messageQueue = Queue()
secretKey = 'ILoveYourMom'
options = webdriver.EdgeOptions()
options.add_argument(f'user-agent={UserAgent().random}')
options.add_experimental_option('debuggerAddress', 'localhost:8989')
options.add_argument(f"window-size={size[0]},{size[1]}")
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

def clearAllChats():
    optionsChats = getFromXPATH('list', 'div', 'class', 'pl-4 pr-2 flex items-center gap-1 justify-center absolute right-0 h-full')
    print(f'Count chats: {len(optionsChats)}')
    for optionsChat in optionsChats:
        optionsChat.click()
        buttonsDeleteChat = getFromXPATH('list', 'li', 'class', 'flex gap-[6px] text-th-primary-medium hover:text-th-primary-dark items-center cursor-pointer hover:bg-th-background-hover font-medium text-xs px-3 py-2 ')
        buttonsDeleteFolder = getFromXPATH('list', 'li', 'class', 'flex gap-[6px] text-th-primary-medium hover:text-th-primary-dark items-center p-1 cursor-pointer hover:bg-th-background-hover text-xs px-3 py-2 ')
        buttonsDelete = buttonsDeleteChat+buttonsDeleteFolder
        buttonsDelete[0].click()
    for id in data: data[id]['hasChat'] = False
    sleep(1)

def createDialogue(userId, userText, message):
    global bot
    answersBefore = getFromXPATH('list', 'div', 'class', 'post-markdown flex flex-col gap-4 text-th-primary-dark text-base')
    sendPrompt(userText)
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Стоп', callback_data='pressed')
    markup.add(button)
    firstMessage = True
    oldResAnswer = ''
    countButtonShare, delay = 0, 0
    while countButtonShare == 0 or time() < delay:
        try:
            if data[userId]['stopGenerating']:
                buttonStopGenerating = getFromXPATH('alone', 'div', 'class', 'pointer-events-auto group flex z-[8] pointer-events-all shadow items-center border rounded border-th-primary-light cursor-pointer bg-th-background text-th-primary-medium gap-1 px-3 py-2 h-[36px] hover:border-th-primary-medium shadow hover:bg-th-background-secondary hover:text-th-primary-dark')
                buttonStopGenerating.click()
                print('STOPPED')
                break
            countButtonShare = len(getFromXPATH('list', 'p', 'class', 'text-sm font-medium whitespace-nowrap '))
            answers = getFromXPATH('list', 'div', 'class', 'post-markdown flex flex-col gap-4 text-th-primary-dark text-base')
            if len(answers) > len(answersBefore):
                answer = [x for x in answers if x not in answersBefore]
                resAnswer = answer[0].get_attribute('textContent')
                if oldResAnswer != resAnswer:
                    delay = time() + 3
                    panelsCode = getFromXPATH('list', 'div', 'class', 'text-th-primary-dark opacity-100 flex bg-th-code-secondary px-4 justify-between items-center gap-2 py-1')
                    if len(panelsCode) > 0:
                        for panel in panelsCode:
                            repText = panel.get_attribute('textContent')
                            resAnswer = resAnswer.replace(repText, '\n')
                    if firstMessage:
                        sentMessage = bot.reply_to(message, resAnswer, reply_markup=markup)
                        firstMessage = False
                    else: bot.edit_message_text(chat_id=message.chat.id, message_id=sentMessage.message_id, text=resAnswer, reply_markup=markup)
                    oldResAnswer = resAnswer
        except: pass
    bot.edit_message_text(chat_id=message.chat.id, message_id=sentMessage.message_id, text=resAnswer)
    data[userId]['stopGenerating'] = False

def checkPermUser(id, text):
    global data
    if id not in data:
        if text == secretKey or id in [1250991011]:
            data[id] = {
                'hasChat': False,
                'stopGenerating': False
            }
            if id in [1250991011]: return 1
            return 0
        else: return -1
    return 1

def getUserInfo(message): return [message.from_user.id,
                                  message.from_user.first_name,
                                  message.from_user.full_name,
                                  message.text]

#COMMANDS
@bot.message_handler(commands=['start', 'about'])
def startHandler(message):
    userId, userName, userFullName, userText = getUserInfo(message)
    bot.send_message(message.chat.id, f'Привет, {userName}! Я самый крутой GPT бот созданный в мире. Меня кста создал самый лучший разработчик(@krojiak).')

@bot.message_handler(commands=['commands'])
def commandsHandler(message):
    userId, userName, userFullName, userText = getUserInfo(message)
    resCheck = checkPermUser(userId, userText)
    if resCheck == -1: bot.send_message(message.chat.id, 'No.')
    elif resCheck == 0: bot.send_message(message.chat.id, 'Yes.')
    elif resCheck == 1:
        bot.send_message(message.chat.id,
                              'Команды: \n'
                              '/about - обо мне \n'
                              '/wwc'
                              '/photo - сделать скриншот сайта'
                              '/clear - очистить все диалоги')

@bot.message_handler(commands=['wwc'])
def wwcHandler(message):
    bot.send_message(message.chat.id, f'what \n\n\n\n\n\n\n\n\n\n who\n\n\n\n\n\n\n\n\n\n\n     caaaares')

@bot.message_handler(commands=['photo'])
def photoHandler(message):
    userId, userName, userFullName, userText = getUserInfo(message)
    resCheck = checkPermUser(userId, userText)
    if resCheck == -1: bot.send_message(message.chat.id, 'No.')
    elif resCheck == 0: bot.send_message(message.chat.id, 'Yes.')
    elif resCheck == 1:
        screen = driver.get_screenshot_as_png()
        bot.send_photo(message.chat.id, screen)

@bot.message_handler(commands=['clear'])
def clearHandler(message):
    userId, userName, userFullName, userText = getUserInfo(message)
    if userId == 1250991011:
        clearAllChats()
        bot.send_message(message.chat.id, 'Все диалоги очищены.')
    else: bot.send_message(message.chat.id, 'ну заплачь')

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global curIdSession
    userId = call.message.chat.id
    if curIdSession == userId and call.data == 'pressed': data[userId]['stopGenerating'] = True

@bot.message_handler()
def enqueueMessage(message):
    global messageQueue
    # Добавляем сообщение пользователя в очередь
    messageQueue.put(message)
    print(f'Set new chat in queue: {message.chat.id} | {message.text}')

def mainHandler():
    global curIdSession
    while True:
        message = messageQueue.get()
        userId, userName, userFullName, userText = getUserInfo(message)
        print(f'{userId} | {userName} | {userFullName} | {userText}')
        print(f'curIdSession: {curIdSession}')
        resCheck = checkPermUser(userId, userText)
        if resCheck == -1: bot.send_message(message.chat.id, 'No.')
        elif resCheck == 0: bot.send_message(message.chat.id, 'Yes.')
        elif resCheck == 1:
            if curIdSession == userId and data[userId]['hasChat']:
                print('stay')
                createDialogue(userId, userText, message)
            elif not data[userId]['hasChat']:
                print('new')

                newChatButtons = getFromXPATH('alone', 'button', 'class', 'cursor-pointer w-full rounded bg-transparent shadow text-th-primary-medium border border-th-border-secondary hover:bg-th-background-hover hover:border-th-primary-light hover:text-th-primary-dark flex gap-[6px] items-center justify-center py-[6px]')
                newChatButtons.click()

                createDialogue(userId, userText, message)

                actions = ActionChains(driver)
                divFolders = getFromXPATH('alone', 'div', 'class', 'group flex px-4 py-2')
                actions.move_to_element(divFolders)
                actions.perform()
                newFolderButton = getFromXPATH('alone', 'div', 'class', 'relative', mObject=divFolders, level='single')
                newFolderButton.click()
                sleep(1)
                listChats = getFromXPATH('alone', 'ul', 'role', 'list')
                choiceFolder = getFromXPATH('list', 'div', 'class', 'flex gap-2', mObject=listChats)
                while len(choiceFolder) == 0: choiceFolder = getFromXPATH('list', 'div', 'class', 'flex gap-2', mObject=listChats)
                choiceFolderIn = getFromXPATH('list', 'div', 'class', 'relative', mObject=choiceFolder[0], level='single')
                choiceFolderIn[1].click()
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
                        sleep(1)
                        actions.send_keys(Keys.DELETE)
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
                    print(chat.get_attribute('textContent'), userId, chat.get_attribute('textContent') == str(userId))
                    if chat.get_attribute('textContent') == str(userId):
                        chat.click()
                        chatExists = True
                        break
                sleep(1)
                if chatExists:
                    createDialogue(userId, userText, message)
                    sleep(1)
                else:
                    bot.send_message(message.chat.id, 'Сори, я потерял твой чат :P')
                    return None

            curIdSession = userId

def main():
    driver.get(mainUrl)
    driver.set_window_size(size[0], size[1])
    waitListChats = 0
    while waitListChats == 0: waitListChats = len(getFromXPATH('list', 'img', 'class', 'object-cover rounded'))
    selectModel = Select(getFromXPATH('alone', 'select', 'id', 'model-select'))
    selectModel.select_by_visible_text('GPT-3.5')
    clearAllChats()
    Thread(target=mainHandler, daemon=True).start()
    print('Browser is ready!')
    bot.polling(none_stop=True)

if __name__ == '__main__':
    #os.startfile('hidden-browser.vbs')
    driver = webdriver.Edge(options=options)
    main()
