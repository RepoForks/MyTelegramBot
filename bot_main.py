#!/usr/bin/python
# coding=utf-8

import os
import random
import telebot
from token_config import TELEBOT_TOKEN
from excited import POEM
import bot_utils

bot = telebot.TeleBot(TELEBOT_TOKEN)

print('SCUT Router Telegram Bot is running now.')

print('Loading alias....', end = '')
try:
    aliasfile = open('./data/.alias', encoding = 'utf-8')
    alias = bot_utils.read_alias_data(aliasfile)
    print('Success')
except FileNotFoundError:
    if not os.path.exists('./data'):
        os.mkdir('./data')
    aliasfile = open('./data/.alias', 'w', encoding = 'utf-8')
    alias = {}
    print('Not found. Created new file.')
finally:
    aliasfile.close()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, '''欢迎使用华工路由器群 Telegram Bot，官方 Telegram 群
    ：https://t.me/scuters 。\n机器人目前由 @fython 进行开发管理，源码地址在：
    https://github.com/fython/SCUTRouterTelegramBot 。\n如有任何意见请在路由器群内 @ 作者反馈。
    输入 /help 获得更多帮助。
    ''')

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, '''
    目前本 Bot 支持的功能：
    /bindalias <key> <value> ： 在聊天群组中自动替换 key 为 value
    /excited : 念诗
    /dns : 显示华工推荐 DNS
    ''')

@bot.message_handler(commands=['bindalias'])
def bind_or_unbind_alias(message):
    args = message.text.split(' ')
    if len(args) == 3:
        ### Bind alias
        key = args[1]
        value = args[2]
        if key in alias.keys():
            bot.reply_to(message, '{0} 条目已经被绑定，如果想修改，请先输入/bindalias {0} 进行解绑。'.format(key))
        else:
            alias[key] = value
            bot_utils.save_alias_data(alias, open('./data/.alias', 'w', encoding = 'utf-8'))
            bot.reply_to(message, '{0} 条目成功绑定，将自动更换消息中的 {0} 为 {1}。'.format(key, value))
    elif len(args) == 2:
        ## Unbind alias
        if args[1] in alias.keys():
            alias.pop(args[1])
            bot_utils.save_alias_data(alias, open('./data/.alias', 'w', encoding = 'utf-8'))
            bot.reply_to(message, '{0} 条目成功删除。'.format(args[1]))
        else:
            bot.reply_to(message, '没有找到这个条目。')
    else:
        bot.reply_to(message, '很抱歉，你输入的参数有误。\n如需绑定请输入 /bindalias <key> <value>， 解绑请输入 /bindalias <key>')

@bot.message_handler(commands=['ping'])
def ping(message):
    args = message.text.split(' ')
    count = -1
    if len(args) == 2:
        ### ping 4 times
        count = 4
    elif len(args) == 3:
        try:
            count = int(args[2])
        except Error:
            bot.reply_to(message, '次数上限参数有误，请输入 1~20 之间的数字。')
        if count < 1 or count > 20:
            bot.reply_to(message, '次数上限参数有误，请输入 1~20 之间的数字。')
            count = -1
    else:
        bot.reply_to(message, '/ping <你要测试的地址> <次数，默认为4，限制 1~20>')
    if count != -1:
        symbols = ['<', '>', '=', '|', '&']
        for symbol in symbols:
            if symbol in args[1]:
                bot.reply_to(message, '你输入的地址有误，请不要试图破坏 Bot 正常工作。')
                return
        try:
            if bot_utils.isWindows():
                command = 'ping -n {0} {1}'
            else:
                command = 'ping -c {0} {1}'
            output = os.popen(command.format(count, args[1]))
            bot.reply_to(message, output.read())
        except Error:
            bot.reply_to(message, '发生了未知错误。')

@bot.message_handler(commands=['traceroute'])
def traceroute(message):
    args = message.text.split(' ')
    if len(args) != 2:
        bot.reply_to(message, '/traceroute <你要测试的地址>')
    else:
        symbols = ['<', '>', '=', '|', '&']
        for symbol in symbols:
            if symbol in args[1]:
                bot.reply_to(message, '你输入的地址有误，请不要试图破坏 Bot 正常工作。')
                return
        try:
            if bot_utils.isWindows():
                command = 'tracert {0}'
            else:
                command = 'traceroute {0}'
            bot.reply_to(message, '现在开始测试 {}……耗时可能比较长，请耐心等待。'.format(args[1]))
            output = os.popen(command.format(args[1]))
            bot.reply_to(message, output.read())
        except Error:
            bot.reply_to(message, '发生了未知错误。')

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
        bot.send_message(message.chat.id, '{0} 说：{1}'.format(name, result.strip()))

bot.polling()
