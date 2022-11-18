import telebot
from telebot import types
import requests
import json
import os
from dotenv import load_dotenv,find_dotenv
import openai
import psycopg2
import googletrans
from config import *
from googletrans import Translator
from bot import BotDB

load_dotenv(find_dotenv())
translator = Translator()
openai.api_key = os.getenv('OPENAI_TOKEN')
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))
lungimea_textului = 150
limba_ai = 'en'
temperature_ai = 90
print(111)  #importarea cheile si default setari
chat_ai = False
result_primit = ""

@bot.message_handler(commands=['admin'])
def admin(message):
  global sms
  if (message.from_user.id == 1369086481):
    print("access granted")
    bot.send_message(1369086481,"Текст для рассылки:")
    bot.register_next_step_handler(
            message, sms_all)
  else:
    print("admin error")

@bot.message_handler(commands=['start'])  #dupa comanda start actiune
def start(message):
  try:
    print(message.from_user.id)
    print(message.from_user.username)
    if(not BotDB.user_exists(message.from_user.id)):
      BotDB.add_user(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("AI Chat🤖")
    item2 = types.KeyboardButton("Settings⚙️")
    markup.add(item1, item2)  #aparitia 3 butoanelor
    bot.send_message(
      message.chat.id,
      "Buna, {0.first_name}!\nEu - <b>{1.first_name}</b>, bot care raspunde folosind AI creat de Negrusceac Nichita cu Openai API daca apare vreun bug @fakebreath."
      .format(message.from_user, bot.get_me()),
      parse_mode='html',
      reply_markup=markup)  #mesajul
  except:
    print(message.from_user)
    bot.send_message(message.chat.id,"db error start-contact @fakebreath")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("AI Chat🤖")
    item2 = types.KeyboardButton("Settings⚙️")
    markup.add(item1, item2)  #aparitia 3 butoanelor
    bot.send_message(
      message.chat.id,
      "Buna, {0.first_name}!\nEu - <b>{1.first_name}</b>, bot care raspunde folosind AI creat de Negrusceac Nichita cu Openai API daca apare vreun bug @fakebreath."
      .format(message.from_user, bot.get_me()),
      parse_mode='html',
      reply_markup=markup)  #mesajul


@bot.message_handler(content_types=['text'])  #dupa anumit text actiune
def Text_input(message):
  global chat_ai
  global temperature_ai
  global result_primit
  global text_primit
  if(not BotDB.user_exists(message.from_user.id)):
    BotDB.add_user(message.from_user.id)
  settings = BotDB.settings_get(message.from_user.id)
  lungimea_textului,temperature_ai,limba_ai,chat_ai = settings
  try:
      if message.chat.type == 'private':
        if message.text == 'AI Chat🤖':
          chat_ai = BotDB.chat_ai(1,message.from_user.id)
          markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
          item2 = types.KeyboardButton("Stop⏸")
          item3 = types.KeyboardButton("Translate🔠")
          item4 = types.KeyboardButton("More💬")
          item5 = types.KeyboardButton("Regenerate🔁")
          back = types.KeyboardButton("Menu🔙")
          markup.add(item2, item3,item4,item5,back)  #trimitere a mesajului scril la functia mesaju_ai
          bot.send_message(
            message.chat.id,
            "Ati Pornit Chatul cu Intelect Artificial\nPentru a opri prelucrarea measagelor de AI apasati Stop⏸\nPentru a reveni in menu apasati Menu🔙\nDaca doriti sa translati raspunsul lui AI (en-ro,ro-en) apasati Translate🔠\nDaca doriti ca AI sasi continue raspunsul apasati More💬\nDaca doriti sa regenerati raspunsul apasati Regenerate🔁\nDonate:https://www.donationalerts.com/r/fakebreath\nDaca Aveti idei/propuneri @fakebreath.",
            reply_markup=markup)

        elif message.text == "Menu🔙":
          chat_ai = BotDB.chat_ai(0,message.from_user.id)
          markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
          item1 = types.KeyboardButton("AI Chat🤖")
          item2 = types.KeyboardButton("Settings⚙️")
          markup.add(item1, item2)
          bot.send_message(message.chat.id,
                           "Sunteti in Meniul botului\nDonate:https://www.donationalerts.com/r/fakebreath\nDaca Aveti idei/propuneri @fakebreath.",
                           reply_markup=markup)

        elif message.text == 'Settings⚙️':
          markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
          item1 = types.KeyboardButton('Limba🔃')
          item2 = types.KeyboardButton('Nr.Cuvinte🔃')
          item3 = types.KeyboardButton('Temperature🔃')
          back = types.KeyboardButton("Menu🔙")
          markup.add(item1, item2, item3, back)
          bot.send_message(message.chat.id, "Settings⚙️:", reply_markup=markup)

        elif message.text == 'Limba🔃':
          markup_inline = types.InlineKeyboardMarkup()
          item_engleza = types.InlineKeyboardButton(text='Engleza',
                                                    callback_data='Engleza')
          item_romana = types.InlineKeyboardButton(text='Romana',
                                                   callback_data='Romana')
          markup_inline.add(item_romana, item_engleza)
          bot.send_message(
            message.chat.id,
            "Limba Intelectului Artificial(in ce limba va raspunde)",
            reply_markup=markup_inline
          )  #Sub text aparitia 2 butoane si setarea variabilii callback_data

        elif message.text == 'Nr.Cuvinte🔃':
          bot.send_message(
            message.chat.id,
            "Scrie lungimea maxima a textului(nr.cuvinte in raspuns la ai) intre 0 si 2048"
          )
          bot.register_next_step_handler(
            message, parametrs)  #trimiterea mesajului la functia parametri

        elif message.text == "Temperature🔃":
          bot.send_message(
            message.chat.id,
            "Scrie un numar dela 1 pana la 100.Temperature(Controlează caracterul aleatoriu: scăderea are ca rezultat finalizări mai puțin aleatorii. Pe măsură ce temperatura se apropie de zero, modelul va deveni determinist și repetitiv.)"
          )
          bot.register_next_step_handler(message, temperature)
        elif message.text == "Continue▶️":
          chat_ai = BotDB.chat_ai(1,message.from_user.id)
          markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
          item2 = types.KeyboardButton("Stop⏸")
          item3 = types.KeyboardButton("Translate🔠")
          item4 = types.KeyboardButton("More💬")
          item5 = types.KeyboardButton("Regenerate🔁")
          back = types.KeyboardButton("Menu🔙")
          markup.add(item2,item3,item4,item5,back)
          bot.send_message(
            message.chat.id,
            "Ai pornit chatul cu AI de acum toate messagele vor fi prelucrate si raspunse",reply_markup=markup
          )


        elif message.text == "Stop⏸":
          markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
          item2 = types.KeyboardButton("Continue▶️")
          item3 = types.KeyboardButton("Translate🔠")
          item4 = types.KeyboardButton("More💬")
          item5 = types.KeyboardButton("Regenerate🔁")
          back = types.KeyboardButton("Menu🔙")
          markup.add(item2,item3,item4,item5,back)
          chat_ai = BotDB.chat_ai(0,message.from_user.id)
          bot.send_message(
            message.chat.id,
            "Ai oprit chatul cu AI de acum message nu vor fi prelucrate",reply_markup=markup)


        elif message.text == "Regenerate🔁":
          print("_________________________________\n Regenerate🔁:")
          chat_ai = BotDB.chat_ai(0,message.from_user.id)
          result = BotDB.get_last_request(message.from_user.id)
          print(result)
          response = openai.Completion.create(  #trimiterea la api lui openai cu setari
            model="text-curie-001",
            prompt=f"\n{result}  ",
            temperature=temperature_ai/100,
            max_tokens=2000,
            top_p=1,  
            frequency_penalty=0.0,
            presence_penalty=0.0 
          )  #salvarea a textului din raspuns log
          print("\nAI:"+response["choices"][0]["text"] )
          print(limba_ai+ "\n_____________________________")
          text_primit = translator.translate(
            response["choices"][0]["text"], dest=str(limba_ai)
          )  #translarea textului din en in limba setata de user(default = en)
          result_primit = text_primit.text
          BotDB.add_response(result_primit,message.from_user.id)
          bot.send_message(message.chat.id, text_primit.text)
          chat_ai = BotDB.chat_ai(1,message.from_user.id)

        elif message.text == "More💬":
          chat_ai = BotDB.chat_ai(0,message.from_user.id)
          lng,last_response = BotDB.get_translate(message.from_user.id)
          text = translator.translate(last_response,dest='en')  #translarea textului in en daca e in alta limba
          result = text.text
          print(f"_________________________________\nContinue this text:{result}.  ")
          response = openai.Completion.create(  #trimiterea la api lui openai cu setari
            model="text-davinci-002",
            prompt=f"\nContinue this text:{result}  ",
            temperature=temperature_ai/100,
            max_tokens=3000,
            top_p=1,  
            frequency_penalty=0.0,
            presence_penalty=0.0 
          )  #salvarea a textului din raspuns log
          print("\nAI:"+response["choices"][0]["text"] )
          print(limba_ai+ "\n_____________________________")
          text_primit = translator.translate(
            response["choices"][0]["text"], dest=str(limba_ai)
          )  #translarea textului din en in limba setata de user(default = en)
          result_primit = text_primit.text
          BotDB.add_response(result_primit,message.from_user.id)
          bot.send_message(message.chat.id, text_primit.text)
          chat_ai = BotDB.chat_ai(1,message.from_user.id)

        elif message.text == "Translate🔠":
          chat_ai=False
          translate = BotDB.get_translate(message.from_user.id)
          lng,last_response = translate
          if len(last_response) > 1:
            if lng == 'en':
              bot.send_message(message.chat.id,
                               (translator.translate(last_response,
                                                     dest='ro')).text)
              chat_ai = True
            elif lng == 'ro':
              bot.send_message(message.chat.id,
                               (translator.translate(last_response,
                                                     dest='en')).text)
              chat_ai = True
          else:
            bot.send_message(message.chat.id,
                             "Mesaggeul de la AI nu este depistat sau este numar")
            chat_ai = True

        elif bool(chat_ai) == True:
          print(f"_________________________________\nMesaju lui {message.from_user.username}:{message.text}\n")
          text = translator.translate(
            message.text,
            dest='en')  #translarea textului in en daca e in alta limba
          result = text.text
          moderation =openai.Moderation.create(input=result)
          print(moderation['results'][0]['flagged'])
          if(moderation['results'][0]['flagged']==True): #Classifies if text violates OpenAI's Content Policy
            bot.send_message(message.chat.id,"Textul incalca OpenAI's Content Policy")
          else:
              BotDB.add_last_request(result,message.from_user.id)
              response = openai.Completion.create(  #trimiterea la api lui openai cu setari
                model="text-curie-001",
                prompt=f"\n{result}.  ",
                temperature=temperature_ai/100,
                max_tokens=lungimea_textului,
                top_p=1,  
                frequency_penalty=0.0,
                presence_penalty=0.0, 
                )  #salvarea a textului din raspuns log
              print("\nAI:"+response["choices"][0]["text"] )
              print(limba_ai+ "\n_____________________________")
              text_primit = translator.translate(
                response["choices"][0]["text"], dest=str(limba_ai)
              )  #translarea textului din en in limba setata de user(default = en)
              result_primit = text_primit.text
              BotDB.add_response(result_primit,message.from_user.id)
              bot.send_message(message.chat.id, text_primit.text)
  except:
    if bool(chat_ai) == False:
        pass
        bot.send_message(message.chat.id, 'Nu te inteleg')



@bot.callback_query_handler(func=lambda call: True)
def function(
    call):  #functia ce dupa tastarea butonului schimba variabila limbii
  global limba_ai
  if call.data == "Engleza":
    BotDB.limba_ai('en',call.from_user.id)
    bot.send_message(call.message.chat.id, "Limba selectata:Engleza✅")
  elif call.data == "Romana":
    BotDB.limba_ai('ro',call.from_user.id)
    bot.send_message(call.message.chat.id, "Limba selectata:Romana✅")


def temperature(message):
  try:
    if isinstance(int(message.text), int):
      if int(message.text) <= 100 and int(message.text) >= 0:
        BotDB.temperature_ai((int(message.text)),message.from_user.id)
        bot.send_message(message.chat.id,
                         f"Temperature🔃 este setata la {message.text}")
      else:
        bot.send_message(message.chat.id,
                         f"Numarul {message.text} este prea mare sau prea mic")
  except:
    bot.send_message(message.chat.id,
                     f"Format gresit {message.text} nu este numar intreg intre 0 si 100")


def parametrs(message):
  if message.chat.type == "private":
    try:
        if (message.text.isnumeric()):  #verificarea daca mesajul este numar
          if int(message.text) > 2048:
            bot.send_message(
              message.chat.id,
              "Numerele mai mare ca 2048 seteaza lungimea la maxim(2048)"
            )  #daca nr este >2048 se seteaza in variabila maximum
            BotDB.lungimea_textului(2048,message.from_user.id)
          elif int(message.text) < 2048:
            bot.send_message(
              message.chat.id,
              f"Lungimea maxima textului este setata la {message.text} cuvinte")
            BotDB.lungimea_textului((int(message.text)),message.from_user.id)  #setarea variabilii la nr scris de user
    except:
      bot.send_message(message.chat.id,
                       "Ai scris ceva gresit")  #daca mesajul nu este numar
def sms_all(message):
  global sms
  spam_base =  BotDB.get_all_users()
  for i in range(len(spam_base)):
    bot.send_message(spam_base[i][0],message.text)
  print(f"Отправлено {len(spam_base)} собщений с текстом {message.text}.")

bot.polling(none_stop=True)  #pornirea permanenta a botului
