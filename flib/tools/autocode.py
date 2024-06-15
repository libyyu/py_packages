# -*- coding: utf-8 -*-
from hashlib import md5
import base64
from time import time
from sys import version_info
PY2 = True if version_info < (3, 0) else False

_auth_key = 'JSLSDds56IO898ASLDdKLKL'
def auth_code(string = '', operation = 'DECODE', key = '', expiry = 0):
    def md5Raw(s):
        if PY2: return md5(s)
        else: return md5(s.encode("utf-8"))
    ckey_length = 4
    if not key: key = _auth_key
    key = md5Raw(key).hexdigest()
    keya = md5Raw(key[:16]).hexdigest()
    keyb = md5Raw(key[16:]).hexdigest()
    if ckey_length:
        if operation == 'DECODE':
            keyc = string[:ckey_length]
        else:
            keyc = md5Raw(str(time())).hexdigest()[-ckey_length:]
    else:
        keyc = ''
    cryptkey = keya + md5Raw(keya + keyc).hexdigest()
    key_length = len(cryptkey)
   
    if operation == 'DECODE':
        string = base64.urlsafe_b64decode(string[ckey_length:])
    else:
        if expiry: expiry = expiry + time()
        expiry = '%010d' % expiry
        string = expiry + md5Raw(string + keyb).hexdigest()[:16] + string
    string_length = len(string)
   
    result = ''
    box = range(256) if PY2 else list(range(256))
    rndkey = {}
    for i in range(256):
        rndkey[i] = ord(cryptkey[i % key_length])
   
    j = 0
    for i in range(256):
        j = (j + box[i] + rndkey[i]) % 256
        tmp = box[i]
        box[i] = box[j]
        box[j] = tmp
    a = 0
    j = 0
    for i in range(string_length):
        a = (a + 1) % 256
        j = (j + box[a]) % 256
        tmp = box[a]
        box[a] = box[j]
        box[j] = tmp
        cr = chr(ord(string[i])) if PY2 else int(string[i])
        try:
            if PY2:
                result += cr ^ (box[(box[a] + box[j]) % 256])
            else:
                result += str(cr ^ (box[(box[a] + box[j]) % 256]))
        except:
            print(string[i], cr, type(cr))
            print(box[(box[a] + box[j]) % 256])
            raise
    if operation == 'DECODE':
        if result[:10] == 0 or int(result[:10]) - time() > 0 or result[10:26] == md5Raw(result[26:] + keyb).hexdigest()[:16]:
            return result[26:]
        else:
            return ''
    else:
        if PY2:
            return keyc + base64.urlsafe_b64encode(result)
        else:
            be = base64.urlsafe_b64encode(bytes(result.encode("utf-8")))
            return keyc + str(be.decode("utf-8")) #replace('=', '')

if __name__ == '__main__':
    str1 = 'hello world !!!'
    encode_str = auth_code(str1, 'ENCODE') #加密
    print (encode_str)
    #print (base64.urlsafe_b64encode(encode_str))
    print (auth_code(encode_str)) #解密

