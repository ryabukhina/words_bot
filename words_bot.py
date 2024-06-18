from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
import telebot
from telebot import types
import random


bot_token = '7247314941:AAHD0iF0PXZGy8e62NTrbNQ9lTl4bIZL1WY'
bot = telebot.TeleBot(bot_token)

file_path = 'words.txt'

with open(file_path, 'r') as f:
    words = f.readlines()

words_list = words[0].split(',')

grog_api_key = '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'

llm = ChatGroq(
    temperature=0,
    model="llama3-70b-8192",
    api_key= grog_api_key
)

template = """You are my English teacher. I need to remember the meaning of words, and the best way to remember is to see them in the text in
context. I give you my word, you show me the translation into Russian and offer the text in which it is used.
The text must be in English and at an entry level, consisting of 1-2 sentences.

Here's the word:
{input}

Result:"""

prompt = PromptTemplate(input_variables=['input'], template=template)

chain_with_parser = prompt | llm | StrOutputParser() 

def generate_text(word):
    return chain_with_parser.invoke({'input': word})

# Dictionary to store user's chosen word
user_words = {}
word_list = random.sample(words_list, 4)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global word_list
    word_list = random.sample(words_list, 4)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    for word in word_list:
        btn = types.KeyboardButton(word)
        markup.add(btn)

    bot.reply_to(message, "Hello! Choose a word:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in word_list)
def handle_word_choice(message):
    chosen_word = message.text
    user_words[message.from_user.id] = chosen_word
    bot.reply_to(message, f"You chose the word: {chosen_word}\n\n{generate_text(chosen_word)}")


    # Generate a new set of 6 random words
    global word_list
    word_list = random.sample(words_list, 4)

    # Send a new message with the new set of words
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    for word in word_list:
        btn = types.KeyboardButton(word)
        markup.add(btn)

    bot.send_message(message.chat.id, "Choose another word:", reply_markup=markup)

@bot.message_handler(commands=['about'])
def send_about(message):
    about_message = "This bot is designed to learn English words."
    bot.reply_to(message, about_message)

bot.polling()
