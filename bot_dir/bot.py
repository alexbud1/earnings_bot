import logging
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import (ReplyKeyboardRemove, 
							ReplyKeyboardMarkup, 
							KeyboardButton, 
							InlineKeyboardMarkup, 
							InlineKeyboardButton)

API_TOKEN = '5315460310:AAEFeFr0pAuArhpV3kZBN8e7ZvXrg5j40_w'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
	main_menu_button1 = KeyboardButton('Show Earnings')
	main_menu_button2 = KeyboardButton('Add Earnings')
	startup_markup = ReplyKeyboardMarkup(resize_keyboard = True)
	# .add(main_menu_button1).add(main_menu_button2)
	startup_markup.row(main_menu_button1,main_menu_button2)
	await message.reply("Hi!\nI'm Salary Bot!\nMy main purpose is to help you count how much you have earned.", reply_markup=startup_markup)


@dp.message_handler()
async def keyboard(message: types.Message):
	if message.text == 'Show Earnings':
		f = open('earnings.json')
		data = json.load(f)
		if str(message.from_user.id) in data:
			msg = "You have totally earned:  " + data.get(str(message.from_user.id))
			await bot.send_message(message.from_user.id, msg)
		else:
			data[str(message.from_user.id)] = '0'
			with open("earnings.json", "w") as jsonFile:
				json.dump(data, jsonFile)
			await message.reply("You have not been registered yet.\nNow you were registered.\nYou are welcome!")
	if message.text == 'Add Earnings':
		await bot.send_message(message.from_user.id, 'Enter sum of money, which you want to add')
		
	# await message.answer(message.text)

if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)