import os
from urllib import parse
import psycopg2
import urllib
import time, telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
from findstall import findstall
from rate import rate
from weather import Weather
import yweather
from telepot import DelegatorBot
from telepot.delegate import pave_event_space, per_chat_id, create_open

class ntuBot(telepot.helper.ChatHandler):

    def __init__(self, *args, **kwargs):
        #initialize some parameters
        super(ntuBot, self).__init__(include_callback_query=True, *args, **kwargs)
        self.state = 0
        self.can = 0
        self.stall = []
        self.stall1 = ''

    def on_chat_message(self,msg):
        global state, stall, stall1, can
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type == 'text':

            # get message payload
            msg_text = msg['text']

            if (msg_text.startswith('/')):

                # parse the command excluding the '/'
                command = msg_text[1:].lower()

                # prepare the correct response based on the given command
                if (command == 'start'):
                    #display current weather at start of bot
                    weather = Weather()

                    # Lookup WOEID via http://weather.yahoo.com.
                    client = yweather.Client()
                    Singapore_NTU = client.fetch_woeid('Nanyang Technological University')
                    lookup = weather.lookup(Singapore_NTU)
                    condition = lookup.condition()
                    response = "Current Weather in NTU: " + condition['text'] + '\n\nRating Stalls or Finding Food? \nTo Rate a Stall, enter /rate\nTo Find Food, enter /find \n\nTo view all commands, enter /list'
                    bot.sendMessage(chat_id, response)

                elif (command == 'list'):
                    #dispaly list of avaiable commands
                    response = 'Here are a list of all available commands: \n/start Begin your food journey! \n/rate Rate your dining experience at stall! \n/find Find delicious food by location or cuisine! \n/feedback Send any feedback, queries or errors spotted to us! \n/quit Exit what you are doing'
                    bot.sendMessage(chat_id, response)
                elif (command == 'feedback'):
                    #set state to 4 to receive feedback from user
                    self.state = 4
                    bot.sendMessage(chat_id, 'Please enter feedback your feedback!')
                elif (command == 'rate'):
                    #set state to 1 to proceed to next stage of rating process
                    self.state = 1
                    canlist = ['Canteen 1', 'Canteen 2', 'Canteen 4', 'Canteen 9', 'Canteen 11', 'Canteen 13', 'Canteen 14', 'Canteen 16', 'Koufu', 'NIE Canteen',
                               'North Hill Canteen', 'North Spine Foodcourt', 'Pioneer Canteen'] 
                    rm = ReplyKeyboardMarkup(one_time_keyboard=True,
                                                               keyboard=[[KeyboardButton(text=i)]for i in canlist])
                    bot.sendMessage(chat_id, 'Choose Canteen', reply_markup= rm)
                    
                elif (command == 'find'):
                    response='Filter by Canteen or Cuisine?'
                    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='Canteen', callback_data='can')],
                        [InlineKeyboardButton(text='Cuisine', callback_data='cui')],])
                    bot.sendMessage(chat_id, response, reply_markup = confirm_keyboard)
                elif (command == 'quit'):
                    #used to exit and reset to initial state
                    self.state = 0
            elif(self.state == 0):
                #initial state. Prompt if no valid command is entered
                bot.sendMessage(chat_id, "Hi, please enter /start to begin! \n\nFor feedback, please enter \n/feedback \n\nTo exit at anytime, enter /quit")
            elif(self.state == 1):
                self.check = 0
                conn_string = "host='ec2-54-225-237-64.compute-1.amazonaws.com' dbname='d7dkk1sep0usei' user='gdzxodktfaiogm' password='a4ad4ecd6b25911c8eea09b601378a27e0a00210b42a27f9d2b953a69f81f43c'"
                conn = psycopg2.connect(conn_string)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM store")
                rlist = cursor.fetchall()

                #check if user input for canteen is valid (matches with that in master list from database table "store")
                for i in range(len(rlist)):
                    if(msg_text == rlist[i][0]):
                        self.check = 1
                #if input valid, we set state to the next state, and prompt user for input of stall
                if(self.check):
                    can = msg_text
                    otpt = "List of stalls in " + msg_text + "\n"
                    self.stall = []
                    #find list of stalls in selected canteen
                    for i in range(0, len(rlist)):
                        if(rlist[i][0] == msg_text):
                            otpt = otpt + rlist[i][2] + "\n"
                            self.stall.append(rlist[i][2])
                    RM = ReplyKeyboardMarkup(one_time_keyboard=True, keyboard=[[KeyboardButton(text=stall)] for stall in self.stall])

                    bot.sendMessage(chat_id,otpt, reply_markup = RM)
                    self.state = 2    
                #if input invalid, stay at current state and prompt user for input of canteen again
                else:
                    canlist = ['Canteen 1', 'Canteen 2', 'Canteen 4', 'Canteen 9', 'Canteen 11', 'Canteen 13', 'Canteen 14', 'Canteen 16', 'Koufu', 'NIE Canteen',
                               'North Hill Canteen', 'North Spine Foodcourt', 'Pioneer Canteen'] 
                    rm = ReplyKeyboardMarkup(one_time_keyboard=True,
                                                               keyboard=[[KeyboardButton(text=i)]for i in canlist])
                    bot.sendMessage(chat_id, 'Choose Canteen', reply_markup= rm)
                    self.state = 1
                    
            elif(self.state == 2):
                self.check = 0
                #check if user input of stall is valid
                for i in range(len(self.stall)):
                    if(msg_text == self.stall[i]):
                        self.check = 1
                #for valid input, ask user to input ratings and move to next state, state 3
                if(self.check == 1):
                    self.stall1 = msg_text
                    self.state = 3
                    RM = ReplyKeyboardMarkup(one_time_keyboard=True, keyboard=[[KeyboardButton(text=rating)] for rating in ['5','4','3','2','1']])
                    bot.sendMessage(chat_id, "Input Ratings" , reply_markup = RM)
                #for invalid stall input, prompt user for input of stall, while remaining at current state
                else:
                    bot.sendMessage(chat_id, "Input Stall: ", reply_markup = ReplyKeyboardMarkup(one_time_keyboard=True, keyboard=[[KeyboardButton(text=stall)] for stall in self.stall]))

            elif(self.state == 3):
                #for valid rating input, attempt to save review using rate.py. check for multiple rating by single user is made in rate.py
                if((msg_text == '1') | (msg_text == '2') | (msg_text == '3') | (msg_text == '4') | (msg_text == '5')):
                    self.state = 0
                    bot.sendMessage(chat_id, rate(can,self.stall1,msg_text,str(chat_id)) )
                #for invalid rating input, prompt user for rating input and remain at current state
                else:
                    self.state = 3
                    bot.sendMessage(chat_id, "Input Ratings" , reply_markup = ReplyKeyboardMarkup(one_time_keyboard=True, keyboard=[[KeyboardButton(text=rating)] for rating in ['5','4','3','2','1']]))
            elif(self.state == 4):
                #send feedback and userid to the admin and return to initial state
                response = str(msg_text) + '\nUserID : ' + str(chat_id)
                bot.sendMessage(408469886, response)
                bot.sendMessage(chat_id, 'Thank you, your feedback was recorded!')
                self.state = 0
                
    def on_callback_query(self,msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

        #Handle Callback Query
        inline_message_id = msg['message']['chat']['id'], msg['message']['message_id']
        bot.editMessageReplyMarkup(inline_message_id, reply_markup=None)

        #for finding stalls by location, provide list of canteens for user to choose from
        if(query_data=='can'):
            #choice1="Canteen"
            canteen_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='Canteen 1', callback_data='can1')],
                        [InlineKeyboardButton(text='Canteen 2', callback_data='can2')],
                        [InlineKeyboardButton(text='Canteen 4', callback_data='can2')],
                        [InlineKeyboardButton(text='Canteen 9', callback_data='can9')],
                        [InlineKeyboardButton(text='Canteen 11', callback_data='can11')],
                        [InlineKeyboardButton(text='Canteen 13', callback_data='can13')],
                        [InlineKeyboardButton(text='Canteen 14', callback_data='can14')],
                        [InlineKeyboardButton(text='Canteen 16', callback_data='can16')],
                        [InlineKeyboardButton(text='Koufu', callback_data='koufu')],
                        [InlineKeyboardButton(text='NIE Canteen', callback_data='niecan')],
                        [InlineKeyboardButton(text='North Hill Canteen', callback_data='nhcan')],
                        [InlineKeyboardButton(text='North Spine Food Court', callback_data='nspine')],
                        [InlineKeyboardButton(text='Pioneer Canteen', callback_data='piocan')],])

            bot.sendMessage(from_id, "Select Canteen", reply_markup = canteen_keyboard)
        #thereafter, use findstall.py to output list of filtered and sorted stalls in selected canteen
        elif(query_data=='can1'):
            response = findstall("Canteen","Canteen 1")
            bot.sendMessage(from_id, response)
        elif(query_data=='can2'):
            response = findstall("Canteen","Canteen 2")
            bot.sendMessage(from_id, response)
        elif(query_data=='can4'):
            response = findstall("Canteen","Canteen 4")
            bot.sendMessage(from_id, response)
        elif(query_data=='can9'):
            response = findstall("Canteen","Canteen 9")
            bot.sendMessage(from_id, response)
        elif(query_data=='can11'):
            response = findstall("Canteen","Canteen 11")
            bot.sendMessage(from_id, response)
        elif(query_data=='can13'):
            response = findstall("Canteen","Canteen 13")
            bot.sendMessage(from_id, response)
        elif(query_data=='can14'):
            response = findstall("Canteen","Canteen 14")
            bot.sendMessage(from_id, response)
        elif(query_data=='can16'):
            response = findstall("Canteen","Canteen 16")
            bot.sendMessage(from_id, response)    
        elif(query_data=='koufu'):
            response = findstall("Canteen","Koufu")
            bot.sendMessage(from_id, response)
        elif(query_data=='niecan'):
            response = findstall("Canteen","NIE Canteen")
            bot.sendMessage(from_id, response)
        elif(query_data=='nhcan'):
            response = findstall("Canteen","North Hill Canteen")
            bot.sendMessage(from_id, response)
        elif(query_data=='nspine'):
            response = findstall("Canteen","North Spine Foodcourt")
            bot.sendMessage(from_id, response)
        elif(query_data=='piocan'):
            response = findstall("Canteen","Pioneer Canteen")
            bot.sendMessage(from_id, response)

        #for finding stalls by cuisine, provide list of cuisine types for user to choose from
        elif(query_data=='cui'):
            cuisine_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Drinks", callback_data="cui1")],
                [InlineKeyboardButton(text="Western", callback_data="cui2")],
                [InlineKeyboardButton(text="Chinese", callback_data="cui3")],
                [InlineKeyboardButton(text="Muslim", callback_data="cui4")],
                [InlineKeyboardButton(text="Indian", callback_data="cui5")],
                [InlineKeyboardButton(text="Japanese", callback_data="cui6")],
                [InlineKeyboardButton(text="Korean", callback_data="cui7")],
                [InlineKeyboardButton(text="Yong Tau Fu", callback_data="cui8")],
                [InlineKeyboardButton(text="Economical Rice", callback_data="cui9")],
                [InlineKeyboardButton(text="Chicken Rice", callback_data="cui10")],
                [InlineKeyboardButton(text="Asian", callback_data="cui11")],
                [InlineKeyboardButton(text="Dessert", callback_data="cui12")],
                [InlineKeyboardButton(text="Malay", callback_data="cui13")],
                [InlineKeyboardButton(text="Thai", callback_data="cui14")],
                [InlineKeyboardButton(text="Vietnamese", callback_data="cui15")],])
            bot.sendMessage(from_id, "Select Cuisine", reply_markup = cuisine_keyboard)

        #thereafter, use findstall.py to output list of filtered and sorted stalls for selected cuisine
        elif(query_data=='cui1'):
            response = findstall("Cuisine","Drinks")
            bot.sendMessage(from_id, response)
        elif(query_data=='cui2'):
            response = findstall("Cuisine","Western")
            bot.sendMessage(from_id, response)
        elif(query_data=='cui3'):
            response = findstall("Cuisine","Chinese")
            bot.sendMessage(from_id, response)
        elif(query_data=='cui4'):
            response = findstall("Cuisine","Muslim")
            bot.sendMessage(from_id, response)
        elif(query_data=='cui5'):
            response = findstall("Cuisine","Indian")
            bot.sendMessage(from_id, response)
        elif(query_data=='cui6'):
            response = findstall("Cuisine","Japanese")
            bot.sendMessage(from_id, response)
        elif(query_data=='cui7'):
            response = findstall("Cuisine","Korean")
            bot.sendMessage(from_id, response)
        elif(query_data=='cui8'):
            response = findstall("Cuisine","Yong Tau Fu")
            bot.sendMessage(from_id, response)
        elif(query_data=='cui9'):
            response = findstall("Cuisine","Economical Rice")
            bot.sendMessage(from_id, response)
        elif(query_data=='cui10'):
            response = findstall("Cuisine","Chicken Rice")
            bot.sendMessage(from_id, response)
        elif(query_data=='cui11'):
            response = findstall("Cuisine","Asian")
            bot.sendMessage(from_id, response)
        elif(query_data=='cui12'):
            response = findstall("Cuisine","Dessert")
            bot.sendMessage(from_id, response)
        elif(query_data=='cui13'):
            response = findstall("Cuisine","Malay")
            bot.sendMessage(from_id, response)
        elif(query_data=='cui14'):
            response = findstall("Cuisine","Thai")
            bot.sendMessage(from_id, response)
        elif(query_data=='cui15'):
            response = findstall("Cuisine","Vietnamese")
            bot.sendMessage(from_id, response)

            
        # answer callback query or else telegram will forever wait on this
        bot.answerCallbackQuery(query_id)

#Implement DelegatorBot
bot = DelegatorBot('442165685:AAHSNlvMc4CzsBVgXJv2kExQ3rCB9DJ_uAg', [
    pave_event_space()
    (per_chat_id(), create_open, ntuBot, timeout=300)
])
MessageLoop(bot).run_as_thread()

while True:
    time.sleep(10)
