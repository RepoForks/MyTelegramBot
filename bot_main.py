#!/usr/bin/python
# coding=utf-8

import os
import random
import telebot
from token_config import TELEBOT_TOKEN
from excited import POEM
import bot_utils
import urllib.error
import other_config
import traceback

bot = telebot.TeleBot(TELEBOT_TOKEN)
me = bot.get_me()

print('Fung Go\'s Telegram Bot is running now.')
print('Bot Account Infomation: ', me)

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
    bot.reply_to(message, '欢迎使用烧饼的 Telegram Bot，机器人由 @fython 进行开发管理，源码地址在：https://github.com/fython/SCUTRouterTelegramBot 。输入 /help 获得更多帮助。')

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, '''
    目前本 Bot 支持的功能：
    /bindalias <key> <value> ： 在聊天群组中自动替换 key 为 value
    /excited : 念诗
    /dns : 显示推荐 DNS
    /ping : Ping
    /traceroute : Traceroute
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
            bot.reply_to(message, '出现了点意外，等会再试试吧……')

@bot.message_handler(commands=['excited'])
def read_poem(message):
    bot.reply_to(message, random.choice(POEM))

@bot.message_handler(commands=['dns'])
def recommend_dns(message):
    bot.reply_to(message, '''可用DNS: 1.2.4.8 ，119.29.29.29 ，223.5.5.5 ，114.114.114.114
    \n中山大学DNS： 202.116.64.2 ，202.116.64.3
    \nGoogle DNS (IPv6)：2001:4860:4860::8888 ，2001:4860:4860::8844
    ''')

@bot.message_handler(commands=['konachan'])
def random_anime_pic(message):
    nsfw = False
    args = message.text.split(' ')
    if len(args) == 2 and (args[1] == 'nsfw' or '车' in args[1]):
        nsfw = True
    try:
        choice = bot_utils.random_konachan_pic(nsfw)
        bot.send_photo(message.chat.id, 'https:' + choice['jpeg_url'], reply_to_message_id=message.message_id, caption='图片来源：' + choice['source'])
    except:
        bot.reply_to(message, '出现了点意外，等会再试试吧……')

@bot.message_handler(func=lambda message: True)
def echo_alias(message):
    ### Do not echo alias in private chat
    result = message.text
    foundAlias = False
    for key in alias.keys():
        final = alias[key]
        while (key in result) and not (final in result and (result.find(key) >= result.find(final)) and ((result.find(key) + len(key)) <= (result.find(final) + len(final)))):
            foundAlias = True
            result = result.replace(key, '|||reP1aced|||')
        while '|||reP1aced|||' in result:
            result = result.replace('|||reP1aced|||', ' ' + final + ' ')
    if foundAlias:
        name = message.from_user.first_name
        if (message.from_user.last_name != None):
            name = name + ' ' + message.from_user.last_name
        bot.send_message(message.chat.id, '{0} 说：{1}'.format(name, result.strip()))
    process_message(message)

def process_message(message):
    if ('续一秒' in message.text) or ('續一秒' in message.text):
        try:
            total = int(bot_utils.url_postdata('https://angry.im/p/life', []))
            hour = total // 3600
            total = total % 3600
            minute = total // 60
            total = total % 60
            name = message.from_user.first_name
            if (message.from_user.last_name != None):
                name = name + ' ' + message.from_user.last_name
            bot.send_message(message.chat.id, '{0} 为长者续了一秒。长者的生命已经延续 {1} 时 {2} 分 {3} 秒了。\n（接口来自 https://angry.im ）'.format(name, hour, minute, total))
        except urllib.error.HTTPError:
            bot.reply_to(message, '暴力膜蛤不可取。\n（接口来自 https://angry.im ）')
    elif ('以图搜图' in message.text) and (message.reply_to_message != None):
        if (message.reply_to_message.content_type != 'photo'):
            bot.reply_to(message, '诶？这张好像不是图片吧……')
        else:
            search_photo_and_reply(message, message.reply_to_message.photo[1])
    elif ('怕了' in message.text) and (not '害' in message.text) and (message.forward_from_message_id == None):
        bot.forward_message(message.chat.id, message.chat.id, message.message_id)

@bot.message_handler(content_types=['photo'])
def receive_photo(message):
    if (message.caption != None) and (me.username in message.caption or '以图搜图' in message.caption):
        if (bot_utils.isWindows()):
            bot.reply_to(message, 'Bot 目前运行在 Windows 环境下，暂不支持这个操作。')
            return
        print('Receive a photo')
        search_photo_and_reply(message, message.photo[1])

def search_photo_and_reply(message, pic):
    raw = pic.file_id
    path = other_config.LINUX_HOST_IMAGE_PATH + raw + '.jpg'
    public_url = other_config.PUBLIC_IMAGE_PATH + raw + '.jpg'
    try:
        file_info = bot.get_file(raw)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(path, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(message.chat.id, '搜图快速入口：\n<a href=\"{0}\">Google</a>\n<a href=\"{1}\">Baidu</a>'.format(bot_utils.get_google_search_image(public_url), bot_utils.get_baidu_search_image(public_url)), reply_to_message_id=message.message_id, disable_web_page_preview = True, parse_mode = 'HTML')
    except:
        traceback.print_exc()
        bot.reply_to(message, '出现了点意外，等会再试试吧……')

bot.polling()
