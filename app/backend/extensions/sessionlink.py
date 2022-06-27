import string
import random
import time
import extensions.logger  as log
from flask import request, jsonify
import extensions.globals as g
#________________________________________________________________________
#
# Secret and tokens generator
#

# tokensDict = { anon : { token : 'n312jk123kj1h3jk1h23', created_time : 1243145.213434 }, ... }
tokensDict = {}
tokenLifeTime = 420 # 420 sek == 7 min

def generate_numeric_token(token_key):
    '''Return: 'numeric_token_for_api' >> '3187819739173981' '''
    chars_token = ''
    count = 0
    # Prepare char token. Actualy string.
    for v in token_key:
        vd = ord(v) + count
        vd = chr(vd)
        count+=1
        chars_token = f'{chars_token}{vd}'
    
    # Convert to numeric token. Return numbers in string.
    numeric_token = ''
    for v in chars_token:
        vd = ord(v)
        numeric_token = f'{numeric_token}{vd}'
    return numeric_token


def secret_generator(size=32, chars=string.ascii_letters + string.digits):
    '''Return: [token_for_server, token_for_api] >> ['adyasd7a8sd7', '81237167317368]'''
    token_key = ''.join(random.choice(chars) for _ in range(size))
    return[token_key, generate_numeric_token(token_key)]


def authorize_connectionlink(uname, token):
    global tokensDict
    global tokenLifeTime

    if uname in tokensDict:
        token_existing_time = int(time.time() - tokensDict[uname]['created_time'])
        if token_existing_time >= tokenLifeTime: # if token out of date
            tokensDict.pop(uname)
            log.logger(['terminal', 'log'], f'authorize_connectionlink: Session time ended for user "{uname}"')
            return False

        else:
            tokensDict[uname]['created_time'] = time.time() # refresh token time
            if tokensDict[uname]['token'] == token: return True
            
    return False


def create_sessionlink(uname):
    global tokensDict
    if uname in tokensDict: return tokensDict[uname]['token']
    else: 
        new_token = secret_generator()
        tokensDict[uname] = {'token': new_token[1], 'created_time':time.time()}
        return new_token[1]


def rm_sessionlink(uname):
    global tokensDict
    tokensDict.pop(uname)


def auth(func):
    def wrapper(*args,**kwargs):
        if request.method == "POST":
            uname = request.get_json()["user"]
            token = request.get_json()["sessionlink"]
            if g.auth_debug: return func(*args, **kwargs)
    
            if authorize_connectionlink(uname, token): return func(*args, **kwargs)
            else: return log.unauthorized_request_log(request.get_json())

        else: jsonify({"auth":False, 'message':'Wrong method.'})

    wrapper.__name__ = func.__name__
    return wrapper