import logging
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import (ReplyKeyboardRemove, 
							ReplyKeyboardMarkup, 
							KeyboardButton, 
							InlineKeyboardMarkup, 
							InlineKeyboardButton)
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext


API_TOKEN = 'Token'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

##### class for states initialization
class Form(StatesGroup):
	main = State()  
	amount = State()  

##### listener for 2 commands,  entrance in main state
@dp.message_handler(commands=['start', 'help'], state='*')
async def send_welcome(message: types.Message, state: FSMContext):
	##### creating buttons and keyboard
	main_menu_button1 = KeyboardButton('Show Earnings')
	main_menu_button2 = KeyboardButton('Add Earnings')
	startup_markup = ReplyKeyboardMarkup(resize_keyboard = True)
	startup_markup.row(main_menu_button1,main_menu_button2)

	await message.reply("Hi!\nI'm Salary Bot!\nMy main purpose is to help you count how much you have earned.", reply_markup=startup_markup)
	##### change state to main
	await Form.main.set()
	
##### listener for first menu
@dp.message_handler(state=Form.main)
async def keyboard(message: types.Message, state: FSMContext):

	if message.text == 'Show Earnings':
		##### open json file and check if user is registered
		f = open('earnings.json')
		data = json.load(f)
		if str(message.from_user.id) in data:
			msg = "You have totally earned:  " + str(data.get(str(message.from_user.id)))
			await bot.send_message(message.from_user.id, msg)
		else:
			##### register user
			data[str(message.from_user.id)] = '0'
			with open("earnings.json", "w") as jsonFile:
				json.dump(data, jsonFile)
			await message.reply("You have not been registered yet.\nNow you were registered.\nYou are welcome!")

	if message.text == 'Add Earnings':
		##### change state to next one (amount)
		await Form.next()
		await bot.send_message(message.from_user.id, 'Enter sum of money, which you want to add')
		
##### listener for integer value of money
@dp.message_handler(state=Form.amount)
async def add_amount(message: types.Message, state: FSMContext):
	##### check if value is int | if not => raise error
	try:
		users_input = int(message.text)
		await state.update_data(number=users_input)
		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton(text="✅", callback_data="agree"),types.InlineKeyboardButton(text="❌", callback_data="disagree"))
		await message.reply("Are you sure, that you have entered correct data?", reply_markup=keyboard)
	except ValueError:
		await message.reply("That's not a number! \n Please enter number")

##### listener for inline keyboard, especially '✅'
@dp.callback_query_handler(text="agree",state = Form.amount)
async def agree_inline(call: types.CallbackQuery, state: FSMContext):
	await call.message.answer('You agreed')
	##### open json file and add value to sum
	user_data = await state.get_data()
	users_input = user_data['number']
	f = open('earnings.json')
	data = json.load(f)
	balance = int(data.get(str(call.from_user.id))) + users_input
	data[str(call.from_user.id)] = balance
	with open("earnings.json", "w") as jsonFile:
		json.dump(data, jsonFile)
	await call.message.edit_text("Are you sure, that you have entered correct data?")
	##### disposing of circle in inline button 
	await call.answer()
	##### turn back to main state
	await Form.main.set()

##### listener for inline keyboard, especially '❌'
@dp.callback_query_handler(text="disagree",state = Form.amount)
async def disagree_inline(call: types.CallbackQuery, state: FSMContext):
	await call.message.answer('You disagreed')

	await call.message.edit_text("Are you sure, that you have entered correct data?")
	##### disposing of circle in inline button 
	await call.answer()
	##### turn back to main state
	await Form.main.set()

if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)