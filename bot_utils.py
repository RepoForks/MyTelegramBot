import platform

def read_alias_data(f):
    return {k.strip():v.strip() for k, v in (l.split('=') for l in f)}

def save_alias_data(d, f):
    for key in d:
        f.write('{k}={v}\n'.format(k = key, v = d[key]))
    f.close()

def isWindows():
    return platform.system() == 'Windows'
