from aiogram import Bot, Dispatcher, executor, types

#SETTINGS
telegramToken = '34g3ererfgdfg34g334gtef'
bot = Bot(telegramToken)
dp = Dispatcher(bot=bot)

@dp.message_handler()
async def mainHandler(message: types.Message):
    resAnswer = 'А'
    resAnswer2 = 'АБ'
    firstMessage = True
    for i in range(2):
        if firstMessage:
            await message.reply(resAnswer, reply=False)
            firstMessage = False
        else:
            #вставить код сюда


executor.start_polling(dp)
