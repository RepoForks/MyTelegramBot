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
import time

bot = telebot.TeleBot(TELEBOT_TOKEN)
me = bot.get_me()

print('Fung Go\'s Telegram Bot is running now.')
print('Bot Account Infomation: ', me)

print('Loading alias....', end = '')
try:
    aliasfile = open('./data/alias.json', encoding = 'utf-8')
    alias = bot_utils.read_json_data(aliasfile)
    print('Success')
except FileNotFoundError:
    if not os.path.exists('./data'):
        os.mkdir('./data')
    aliasfile = open('./data/alias.json', 'w', encoding = 'utf-8')
    alias = {}
    print('Not found. Created new file.')
finally:
    aliasfile.close()

def is_message_outdate(message):
    if (bot_utils.get_now_time() - message.date > 30):
        return True
    else:
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if (is_message_outdate(message)):
        return False
    bot.reply_to(message, '欢迎使用烧饼的 Telegram Bot，机器人由 @fython 进行开发管理，源码地址在：https://github.com/fython/SCUTRouterTelegramBot 。输入 /help 获得更多帮助。')

@bot.message_handler(commands=['help'])
def send_help(message):
    if (is_message_outdate(message)):
        return False
    bot.reply_to(message, '''
    目前本 Bot 支持的功能：
    /bindalias <key> <value> ： 在聊天群组中自动替换 key 为 value
    /excited : 念诗
    /dns : 显示推荐 DNS
    /ping : Ping
    /traceroute : Traceroute
    ''')

@bot.message_handler(commands=['excited'])
def read_poem(message):
    if (is_message_outdate(message)):
        return False
    bot.reply_to(message, random.choice(POEM))

@bot.message_handler(commands=['dns'])
def recommend_dns(message):
    if (is_message_outdate(message)):
        return False
    bot.reply_to(message, '''可用DNS: 1.2.4.8 ，119.29.29.29 ，223.5.5.5 ，114.114.114.114
    \n中山大学DNS： 202.116.64.2 ，202.116.64.3
    \nGoogle DNS (IPv6)：2001:4860:4860::8888 ，2001:4860:4860::8844
    ''')

@bot.message_handler(commands=['konachan'])
def random_anime_pic(message):
    if (is_message_outdate(message)):
        return False
    nsfw = False
    args = message.text.split(' ')
    if len(args) == 2 and (args[1] == 'nsfw' or '车' in args[1]):
        nsfw = True
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        choice = bot_utils.random_konachan_pic(nsfw)
        bot.send_photo(message.chat.id, 'https:' + choice['jpeg_url'], reply_to_message_id=message.message_id, caption='图片来源：' + choice['source'])
    except:
        bot.reply_to(message, '出现了点意外，等会再试试吧……')

@bot.message_handler(commands=['chattitle'])
def get_chat_title(message):
    if (is_message_outdate(message)):
        return False
    chat = bot.get_chat(message.chat.id)
    if (chat.type != 'private'):
        bot.send_message(message.chat.id, '当前群组标题：' + chat.title)
    else:
        bot.send_message(message.chat.id, '请在群组里面使用此功能。')

@bot.message_handler(commands=['bindalias'])
def bind_or_unbind_alias(message):
    if (is_message_outdate(message)):
        return False
    args = message.text.split(' ')
    if len(args) == 3:
        ### Bind alias
        key = args[1]
        value = args[2]
        if ('ignoreme' in key) or ('续一秒' in key) or ('以图搜图' in key):
            bot.reply_to(message, '这条规则不能被绑定。')
        else:
            if str(message.chat.id) not in alias.keys():
                alias[str(message.chat.id)] = {}
            if key in alias[str(message.chat.id)].keys():
                bot.reply_to(message, '{0} 已经被绑定。你可以输入 /bindalias {0} 来解绑。'.format(key))
            else:
                alias[str(message.chat.id)][key] = value
                bot_utils.save_json_data(alias, open('./data/alias.json', 'w', encoding = 'utf-8'))
                bot.reply_to(message, '{0} 已经被绑定。{0} 将会自动替换为 {1}。'.format(key, value))
    elif len(args) == 2:
        if (args[1] == 'ignoreme'):
            key = 'ignoreme@' + message.from_user.username
            if str(message.chat.id) not in alias.keys():
                alias[str(message.chat.id)] = {}
            if key in alias[str(message.chat.id)].keys():
                alias[str(message.chat.id)].pop(key)
                bot_utils.save_json_data(alias, open('./data/alias.json', 'w', encoding = 'utf-8'))
                bot.reply_to(message, '现在你发送的文本会被替换。')
            else:
                alias[str(message.chat.id)][key] = 'true'
                bot_utils.save_json_data(alias, open('./data/alias.json', 'w', encoding = 'utf-8'))
                bot.reply_to(message, '现在你发送的文本不会被替换。')
        elif (str(message.chat.id) in alias.keys()) and (args[1] in alias.keys()):
            alias[str(message.chat.id)].pop(args[1])
            bot_utils.save_json_data(alias, open('./data/alias.json', 'w', encoding = 'utf-8'))
            bot.reply_to(message, '{0} 绑定已经清除。'.format(args[1]))
        else:
            bot.reply_to(message, '找不到绑定的值。')
    else:
        bot.reply_to(message, '输入 /bindalias <key> <value> 进行绑定，<key>为要替换的值，<value>为替换结果。如需解绑请输入 /bindalias <key>。如果不想你发送的文本被替换可以输入 /bindalis ignoreme，再次输入可以取消。')

@bot.message_handler(commands=['replace'])
def replace_keyword(message):
    if (is_message_outdate(message)):
        return False
    if (message.reply_to_message == None):
        bot.reply_to(message, '请选择一条文本消息回复进行替换。')
    elif (message.reply_to_message.content_type != 'text'):
        bot.reply_to(message, '请选择一条文本消息回复进行替换。')
    else:
        args = message.text.split(' ')
        if (len(args) != 3):
            bot.reply_to(message, '你输入的参数不对，格式：/replace <要替换的关键词> <替换结果>')
        else:
            key = args[1]
            final = args[2]
            result = message.reply_to_message.text
            while (key in result) and not (final in result and (result.find(key) >= result.find(final)) and ((result.find(key) + len(key)) <= (result.find(final) + len(final)))):
                result = result.replace(key, '|||reP1aced|||')
            while '|||reP1aced|||' in result:
                result = result.replace('|||reP1aced|||', '<b>' + final + '</b>')
            replacer = message.from_user.first_name
            if (message.from_user.last_name != None):
                replacer = replacer + ' ' + message.from_user.last_name
            author = message.reply_to_message.from_user.first_name
            if (message.reply_to_message.from_user.last_name != None):
                author = author + ' ' + message.reply_to_message.from_user.last_name
            bot.send_message(message.chat.id, '{0} 说 {1} 的意思是：“{2}”'.format(replacer, author, result), parse_mode = 'HTML')

@bot.message_handler(func=lambda message: True)
def echo_alias(message):
    if not process_message(message):
        if str(message.chat.id) in alias.keys():
            result = message.text
            foundAlias = False
            if '//' in result:
                return False
            for key in alias[str(message.chat.id)].keys():
                if ('ignoreme@' in key):
                    if (key.replace('ignoreme@', '') in message.from_user.username):
                        return False
                    continue
                final = alias[str(message.chat.id)][key]
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

def process_message(message):
    if (is_message_outdate(message)):
        return False
    if (message.text.find('/replace') == 0):
        replace_keyword(message)
        return True
    elif ('续一秒' in message.text) or ('續一秒' in message.text):
        try:
            bot.send_chat_action(message.chat.id, 'typing')
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
        return True
    elif ('以图搜图' in message.text) and (message.reply_to_message != None):
        if (message.reply_to_message.content_type != 'photo'):
            bot.reply_to(message, '诶？这张好像不是图片吧……')
        else:
            search_photo_and_reply(message, message.reply_to_message.photo[1])
        return True
    elif (('bot' in message.text.lower()) or ('机器人' in message.text) or ('Aoba' in message.text.lower())) and ('挂了' in message.text):
        for i in range(0, 2):
            bot.send_chat_action(message.chat.id, 'typing')
            time.sleep(3)
        bot.reply_to(message, '暂时还没挂。')
    return False

@bot.message_handler(content_types=['photo'])
def receive_photo(message):
    if (is_message_outdate(message)):
        return False
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
        bot.send_chat_action(message.chat.id, 'upload_photo')
        file_info = bot.get_file(raw)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(path, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(message.chat.id, '搜图快速入口：\n<a href=\"{0}\">Google</a>\n<a href=\"{1}\">Baidu</a>'.format(bot_utils.get_google_search_image(public_url), bot_utils.get_baidu_search_image(public_url)), reply_to_message_id=message.message_id, disable_web_page_preview = True, parse_mode = 'HTML')
    except:
        traceback.print_exc()
        bot.reply_to(message, '出现了点意外，等会再试试吧……')

for trytime in range(0, 3):
    print('Start polling...')
    bot.polling()
