from flask_sqlalchemy import SQLAlchemy
from install import make_settings, install_module
import json
import os
import string
import random
from pythonping import ping
import datetime, time


#________________________________________________________________________
#
# Global variables
#
app = None
db = SQLAlchemy()
dbm = None
dbdir = "dbcontroller"
dbname = "rpismarthome.db"
dbpath = f"{dbdir}/{dbname}"
saltFile = "salts.csv"
saltPath = f"{dbdir}/{saltFile}"
dbconnector = f"sqlite:///{dbpath}"
secret_key = "default_secret_key"
settingspath = "settings.json"
auth_debug = False
refresh_widget_delay = 1000 # 1000 ms

logs = []


def check_project_files():
    '''
    Check project structure and install/add missing package/files
    '''
    run_app = True

    install_module('flask')
    install_module('flask_sqlalchemy')

    if not os.path.isfile(settingspath):
        print("   + [ ! ] Nie odnaleziono pliku konfiguracyjnego.")
        make_settings(settingspath)
        
        if not os.path.isfile(settingspath):
            print("   + [ ! ] Nie udało się stworzyć pliku konfiguracyjnego.")
            run_app = False

    else: print("   + Settings file: OK")

    return run_app


def secret_key_generator(size=128, chars=string.ascii_letters + string.digits):
    '''
    Return generated random symbols string
    '''
    return ''.join(random.choice(chars) for _ in range(size))


def loadSettingsFile():
    '''
    Load secret_key from settings.json
    '''
    if check_project_files():
        file = open(settingspath, 'r')
        settings = json.load(file)
        secret_key = settings['secret_key']


#________________________________________________________________________
#
# Universal fns
#

def tryip(ip: str):
    '''
    Return True if device responds or False if not
    '''
    try:
        ping_result = ping(ip, count=1)
    except:
        return False
    return False if str(ping_result).split("\n")[-3] == "Request timed out\r" else True


def getDateTime(format='datetime'):
    '''
    Return time in choosed format
        number   -> 1321234.123123
        time     -> 12:00:00
        date     -> 01-01-2000
        datetime -> 01-01-2000 12:00:00 [default]
        daytime  -> 1 12:00:00
        custom like %d-%m-%Y
    '''
    if format=='numbers': return time.time()
    elif format=='time': return datetime.datetime.now().strftime("%H:%M:%S")
    elif format=='date': return datetime.datetime.now().strftime("%d-%m-%Y")
    elif format=='datetime': return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    elif format=='daynrtime': return datetime.datetime.now().strftime("%a %H:%M:%S")
    elif format=='daytime': return datetime.datetime.now().strftime("%w %H:%M:%S")
    else:
        try:
            dt = datetime.datetime.now().strftime(format)
            return dt
        except:
            return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")