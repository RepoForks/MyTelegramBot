#!/usr/bin/python

import os
import random
import telebot
from token_config import TELEBOT_TOKEN
from excited import POEM
import bot_utils

bot = telebot.TeleBot(TELEBOT_TOKEN)

print('SCUT Router Telegram Bot is running now.')

print('Loading alias....', end='')
try:
    aliasfile = open('./data/.alias', encoding='utf-8')
    alias = bot_utils.read_alias_data(aliasfile)
    print('Success')
except FileNotFoundError:
    if not os.path.exists('./data'):
        os.mkdir('./data')
    aliasfile = open('./data/.alias', 'w', encoding='utf-8')
    alias = {}
    print('Not found. Created new file.')
finally:
    aliasfile.close()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, '''欢迎使用华工路由器群 Telegram Bot，官方 Telegram 群
    ：https://t.me/scuters 。\n机器人目前由 @fython 进行开发管理，源码地址在
    GitHub 搜索 scutrouter 即可找到。\n如有任何意见请在路由器群内 @ 作者反馈。
    输入 /help 获得更多帮助。
    ''')

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, '''
    目前本 Bot 支持的功能：
    /alias <key> <value> ： 在聊天群组中自动替换 key 为 value
    /excited : 念诗
    ''')

@bot.message_handler(commands=['alias'])
def bind_or_unbind_alias(message):
    args = message.text.split(' ')
    if len(args) == 3:
        ### Bind alias
        key = args[1]
        value = args[2]
        if key in alias.keys():
            bot.reply_to(message, '{key} 条目已经被绑定，如果想修改，请先输入/alias {key} 进行解绑。'.format(key = key))
        else:
            alias[key] = value
            bot_utils.save_alias_data(alias, open('./data/.alias', 'w', encoding='utf-8'))
            bot.reply_to(message, '{key} 条目成功绑定，将自动更换消息中的 {key} 为 {value}。'.format(key = key, value = value))
    elif len(args) == 2:
        ## Unbind alias
        if args[1] in alias.keys():
            alias.pop(args[1])
            bot_utils.save_alias_data(alias, open('./data/.alias', 'w', encoding='utf-8'))
            bot.reply_to(message, '{key} 条目成功删除。'.format(key = args[1]))
        else:
            bot.reply_to(message, '没有找到这个条目。')
    else:
        bot.reply_to(message, '很抱歉，你输入的参数有误。\n如需绑定请输入 /alias <key> <value>， 解绑请输入 /alias <key>')

@bot.message_handler(commands=['excited'])
def read_poem(message):
    bot.reply_to(message, random.choice(POEM))

@bot.message_handler(commands=['dns'])
def recommend_dns(message):
    bot.reply_to(message, '''可用DNS: 1.2.4.8 ，119.29.29.29 ，223.5.5.5 ，114.114.114.114
    \n中山大学DNS： 202.116.64.2 ，202.116.64.3
    \nGoogle DNS (IPv6)：2001:4860:4860::8888 ，2001:4860:4860::8844
    ''')

@bot.message_handler(func=lambda message: True)
def echo_alias(message):
    ### Do not echo alias in private chat
    result = message.text
    foundAlias = False
    for key in alias.keys():
        while key in result:
            foundAlias = True
            result = result.replace(key, '|||reP1aced|||')
        while '|||reP1aced|||' in result:
            result = result.replace('|||reP1aced|||', ' ' + alias[key] + ' ')
    if foundAlias:
        name = message.from_user.first_name
        if (message.from_user.last_name != None):
            name = name + ' ' + message.from_user.last_name
        bot.send_message(message.chat.id, '{name} 说：{content}'.format(name = name, content = result.strip()))

bot.polling()
