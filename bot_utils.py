# coding=utf-8
import platform
import urllib.request

def read_alias_data(f):
    return {k.strip():v.strip() for k, v in (l.split('=') for l in f)}

def save_alias_data(d, f):
    for key in d:
        f.write('{k}={v}\n'.format(k = key, v = d[key]))
    f.close()

def isWindows():
    return platform.system() == 'Windows'
    
def url_postdata(requrl, data_unencoded):
    req = urllib.request.Request(url = requrl, data = urllib.parse.urlencode(data_unencoded).encode(encoding='UTF8'))
    return urllib.request.urlopen(req).read().decode()
