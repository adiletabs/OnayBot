import telebot
import requests
import messages
import json
from telebot import types
from messages import*
from onay import get_balance

bot = telebot.TeleBot(TOKEN)

card_type = types.ReplyKeyboardMarkup(row_width=2)
universal_btn = types.KeyboardButton('Universal')
social_btn = types.KeyboardButton('Social')
pupil_btn = types.KeyboardButton('Pupil')
student_btn = types.KeyboardButton('Student')
card_type.row(universal_btn, social_btn)
card_type.row(pupil_btn, student_btn)

chosen_type = ''

def get_allcards():
	data = {}
	with open ('cards.json', 'r') as file:
		data = json.load(file)
	return data

@bot.message_handler(commands=['start'])
def send_intro(message):
    bot.send_message(message.chat.id, messages.INTRO)

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, messages.HELP)

@bot.message_handler(commands=['add'])
def define_type(message):
    bot.send_message(message.chat.id, messages.CHOOSETYPE, reply_markup = card_type)

@bot.message_handler(commands=['mycards'])
def my_cards(message):
	user_id = str(message.from_user.id)
	data = get_allcards()
	if data.get(user_id) is not None:
		mylist = 'Here are your cards:\n\n'	
		for i in data[user_id]:
			mylist += str(i) + '\n'
		bot.send_message(message.chat.id, mylist) 
	else:
		bot.send_message(message.chat.id, messages.EMPTY) 

@bot.message_handler(commands=['remove'])
def which_to_remove(message):
	user_id = str(message.from_user.id)
	data = get_allcards()
	if data.get(user_id) is not None:
		card_list = types.ReplyKeyboardMarkup(row_width=1)
		for i in data[user_id]:
			btn = types.KeyboardButton('Remove ' + i)
			card_list.add(btn)
		bot.send_message(message.chat.id, messages.WHICHREMOVE, reply_markup = card_list)
		@bot.message_handler(func=lambda message: len(message.text) == 26)
		def delete(message):
			user_id = str(message.from_user.id)
			data = get_allcards()
			if len(data[user_id]) > 1:
				data[user_id] = [x for x in data[user_id] if x != message.text[7:]]
			else:
				del data[user_id]
			with open('cards.json', 'w') as file:
				json.dump(data, file)
			bot.send_message(message.chat.id, messages.REMOVED, reply_markup = types.ReplyKeyboardRemove())
	else:
		bot.send_message(message.chat.id, messages.EMPTY)	

@bot.message_handler(commands=['hide'])
def define_type(message):
    bot.send_message(message.chat.id, reply_markup = types.ReplyKeyboardRemove())

@bot.message_handler(regexp='Universal')
def choose_universal(message):
    global chosen_type
    bot.send_message(message.chat.id, messages.PRINTCODE)
    chosen_type = 'Universal'
    send_code()

@bot.message_handler(regexp='Social')
def choose_social(message):
    global chosen_type
    bot.send_message(message.chat.id, messages.PRINTCODE)
    chosen_type = 'Social'
    send_code()

@bot.message_handler(regexp='Pupil')
def choose_pupil(message):
    global chosen_type
    bot.send_message(message.chat.id, messages.PRINTCODE)
    chosen_type = 'Pupil'
    send_code()

@bot.message_handler(regexp='Student')
def choose_student(message):
    global chosen_type
    bot.send_message(message.chat.id, messages.PRINTCODE)
    chosen_type = 'Student'
    send_code()

def define_prefix(chosen_type):
	if chosen_type == 'Universal':
		return '96431085033'
	elif chosen_type == 'Social':
		return '96439085033'
	elif chosen_type == 'Pupil':
		return '96439085033'
	elif chosen_type == 'Student':
		return '96439085033'

def send_code():
	@bot.message_handler(func=lambda message: len(message.text) == 8)
	def send_digits(message):
		user_id = str(message.from_user.id)
		data = get_allcards()
		cardcode = define_prefix(chosen_type) + message.text
		balance = get_balance(cardcode)
		if balance is not None:
			if data.get(user_id) is not None:
				l = data[user_id]
				if cardcode not in l:
					l.append(cardcode)
					data[user_id] = l
				else:
					bot.send_message(message.chat.id, messages.EXISTS, reply_markup = types.ReplyKeyboardRemove())
					return None
			else:
				data[user_id] = [cardcode]
			with open('cards.json', 'w') as file:
				json.dump(data, file)
			bot.send_message(message.chat.id, messages.ADDED, reply_markup = types.ReplyKeyboardRemove())
		else:
			bot.send_message(message.chat.id, messages.NOTEXIST)

@bot.message_handler(commands=['balance'])
def balance(message):
	user_id = str(message.from_user.id)
	data = get_allcards()
	if data.get(user_id) is not None:
		card_list = types.ReplyKeyboardMarkup(row_width=1)
		for i in data[user_id]:
			btn = types.KeyboardButton(i)
			card_list.add(btn)
		bot.send_message(message.chat.id, messages.CHOOSECARD, reply_markup = card_list)
		@bot.message_handler(func=lambda message: len(message.text) == 19)
		def check(message):
			balance = get_balance(message.text)
			bot.send_message(message.chat.id, 'Balance is of this card is %d tenge\nThank you!' %balance, 
				reply_markup = types.ReplyKeyboardRemove())
	else:
		bot.send_message(message.chat.id, messages.EMPTY)

if __name__ == '__main__':
	bot.polling()