# coding=utf-8
import platform
import urllib.request
import json
import time
import random
import datetime

latest_pic = {'id' : 240345, 'updated_at' : 1492495497.0}

def read_alias_data(f):
    return {k.strip():v.strip() for k, v in (l.split('=') for l in f)}

def save_alias_data(d, f):
    for key in d:
        f.write('{k}={v}\n'.format(k = key, v = d[key]))
    f.close()

def isWindows():
    return platform.system() == 'Windows'

def url_readstr(url):
    return urllib.request.urlopen(url).read().decode()

def url_postdata(requrl, data_unencoded):
    req = urllib.request.Request(url = requrl, data = urllib.parse.urlencode(data_unencoded).encode(encoding='UTF8'))
    return urllib.request.urlopen(req).read().decode()

def random_konachan_pic(nsfw):
    now = time.time()
    choice = None
    if (now - latest_pic['updated_at']) > 600:
        url = 'http://konachan.{}/post.json?limit=1'.format('com' if nsfw else 'net')
        print('Konachan Request url: ' + url)
        res = url_readstr(url)
        result = json.loads(res)[0]
        if (result['id'] != latest_pic['id']):
            latest_pic['updated_at'] = time.time()
            latest_pic['id'] = result['id']
            choice = result
            if (not nsfw) and (('censored' in choice['tags']) or ('nude' in choice['tags'])):
                choice = None
    attempt = 0
    while choice == None:
        attempt += 1
        url = 'http://konachan.{0}/post.json?limit=1&page={1}'.format('com' if nsfw else 'net', random.randrange(10000, latest_pic['id']))
        print('Konachan Request url: ' + url)
        try:
            res = url_readstr(url)
            choice = json.loads(res)[0]
            if (not nsfw) and (('censored' in choice['tags']) or ('nude' in choice['tags'])):
                choice = None
        except:
            pass
        if attempt > 3:
            break
    return choice

def get_google_search_image(url):
    return 'https://www.google.com.hk/searchbyimage?image_url={}&encoded_image=&image_content=&filename=&hl=zh-HK'.format(url)

def get_baidu_search_image(url):
    return 'http://image.baidu.com/n/pc_search?rn=10&appid=0&tag=1&queryImageUrl={}'.format(url)

def get_now_time():
    return time.mktime(datetime.datetime.now().timetuple())
