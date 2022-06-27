from dbcontroller.dbtemplate import User, Settings, Devices, Storage, Widget
import os
import hashlib
import base64

import extensions.globals as g
import extensions.logger  as log
import rpi.rpi_factorys   as rpif


usersSaltsDict = {}


def loadUsersSalts():
    if not os.path.exists(g.saltPath):
        log.logger(['terminal', 'log'], '   [ ! ] Salt file do not exist. Created new.')
        with open(g.saltPath, 'w') as f:
            f.write('')
    with open(g.saltPath, 'r') as f:
        for line in f.readlines():
            [uname, salt] = line.split(':')
            salt = salt[0:-1]
            usersSaltsDict[uname] = salt


def recreate():
    g.db.create_all()


def tryPassword(uname, passwd):
    if uname in usersSaltsDict:
        user = User.query.filter(User.uname == uname).first()
        if g.auth_debug: return user
        if user is not None:
            bytesSalt = bytes(usersSaltsDict[uname], encoding='utf-8')
            bytesPasswd  = hashlib.pbkdf2_hmac('sha256', passwd.encode('utf-8'), bytesSalt, 100000)

            stringPasswd = base64.b64encode(bytesPasswd).decode("utf-8")
            #print(f"{stringPasswd}\n{user.password}")

            if stringPasswd == user.password: 
                #print("Access granted")
                return user
    else: log.logger(['terminal', 'log'], f'[ ? ] tryPassword: Brak soli użytkownika {uname}')
    return None
    

def changeSaltInFile(uname, newSalt=None):
    linesList = []
    with open(g.saltPath, 'r') as f:
        lineToRemove = ''
        linesList = f.readlines()
        for line in linesList:
            [unameLine, salt] = line.split(':')
            if unameLine == uname: 
                lineToRemove=line
                break

    with open(g.saltPath, 'w') as f:
        for line in linesList:
            if line != lineToRemove:
                f.write(line)
        if newSalt is not None: f.write(newSalt)


def newUserPassword(uname, newPasswd, addUserMode=False):
    user = User.query.filter(User.uname == uname).first()
    if user is not None or addUserMode:
        newSalt   = g.secret_key_generator(size=64)
        bytesSalt = bytes(newSalt, encoding='utf-8')

        
        changeSaltInFile(uname, f'{uname}:{newSalt}\n')
        usersSaltsDict[uname] = newSalt

        bytesPasswd = hashlib.pbkdf2_hmac('sha256', newPasswd.encode('utf-8'), bytesSalt, 100000)
        stringPasswd = base64.b64encode(bytesPasswd).decode("utf-8")
        if addUserMode:
            return stringPasswd
        else:
            user.password = stringPasswd
            g.db.session.commit()
            return True


def adduser(newuser):
    [account_type, uname, fname, lname, email, password] = newuser
    passwd = newUserPassword(uname, password, addUserMode=True)
    if account_type == 'admin':
        user = User(account_type=account_type, uname=uname, fname=fname, lname=lname, email=email, password=passwd, 
                    active=True, available_menu='pilot;actions;administration', available_widgets='all', edit_widgets=True, edit_actions=True)
    else:
        user = User(account_type=account_type, uname=uname, fname=fname, lname=lname, email=email, password=passwd, 
                    active=True, available_menu='pilot', available_widgets='all', edit_widgets=False, edit_actions=False)
    g.db.session.add(user)
    g.db.session.commit()


def userexist(uname):
    return g.db.session.query(User.uname).filter_by(uname=uname).first() is not None


def remove_user(uname):
    admins = User.query.filter(User.account_type == "admin").with_entities(User.uname).all()
    admins_count = len(admins)
    removed = False
    
    def remove_from_db():
        removed = True if User.query.filter(User.uname == uname).delete() == 1 else False
        g.db.session.commit()
        changeSaltInFile(uname)

    if admins_count == 1:
        for admin in admins:
            if not admin[0] == uname:
                removed = remove_from_db()
    else:
        removed = remove_from_db()
    return removed

def check_db_file(app):
    if os.path.isfile(g.dbpath):
        log.logger(['terminal', 'log'], f"[ + ] Plik SQLite: OK")
    else:
        log.logger(['terminal', 'log', 'war'], f"Nie odnaleziono pliku bazy danych. Tworzenie nowego pliku na podstawie szablonu.")
        g.db.create_all()
        
        if os.path.isfile(g.dbpath): log.logger(['terminal', 'log', 'inf'], f"[ + ] Plik SQLite: OK")
        else: log.logger(['terminal', 'log', 'war'], f"Nie udało się utworzyć nowej bazy danych.")


def check_admin_exist():
    if len(User.query.all()) == 0:
        print("   + Tworzenie domyślnego użytkownika")
        passwd = newUserPassword('admin', 'admin', addUserMode=True)
        user = User(account_type='admin', uname='admin', fname='', lname='', email='', password=passwd, 
                    active=True, available_menu='pilot;actions;administration', available_widgets='all', edit_widgets=True, edit_actions=True)
        g.db.session.add(user)

        systemonoff = str({'active': True, 'id': '1', 'name': 'System On/Off', 'off_action': 'end', 'on_action': 'run', 'type': 'two_state_switch', 'watch_path': 'False if shome.active_smart_home_api_thread is None else True', 'watch_type': 'custom'})
        widget = Widget(meta=systemonoff)
        g.db.session.add(widget)
        
        g.db.session.commit()


def getUserWidgets(uname):
    user_row = User.query.filter(User.uname == uname).first()
    u_widgets = user_row.available_widgets.split(',')
    u_widgets.append(user_row.edit_widgets)
    return u_widgets


def check_permissions(uname):
    user_row = User.query.filter(User.uname == uname).first()
    if user_row.edit_actions == 1: return True
    return False

#------------------- SETTINGS -------------------


def loadSettings(uname):
    setting_row = Settings.query.filter(Settings.setting == 'refresh_widget_delay', Settings.uname == uname).first()
    try:
        if setting_row: g.refresh_widget_delay = int(setting_row.value)
        else: log.logger(['terminal', 'log'], f'loadSettings: Setting "refresh_widget_delay" not found for user "{uname}".')
    except:
        log.logger(['terminal', 'log'], f'loadSettings: Can not load "refresh_widget_delay" as int.')


def saveSettingInDB(uname, setting, value):
    setting_row = Settings.query.filter(Settings.setting == setting, Settings.uname == uname).first()
    try:
        if setting_row: setting_row.value = f'{value}'
        else: g.db.session.add(Settings(setting=f'{setting}', value=f'{value}' , uname=uname))
        g.db.session.commit()
    except:
        log.logger(['terminal', 'log'], f'saveSettingInDB: Can not save "{setting}" with value "{value}" in DB.')


#------------------- DEVICES -------------------


def loadDevices():
    devices = Devices.query.all()
    for device in devices:
        rpif.host_ip_list[device.alias] = {'ip': device.ip, 'work': False, 'enable': device.enable}

def addDevice(ip, alias, enable=1):
    device_row = Devices.query.filter(Devices.alias == alias).first()
    try:
        if enable in [1, True, "1"]: enable = 1
        elif enable in [0, False, "0"]: enable = 0
        if device_row: 
            device_row.ip = ip
            device_row.alias = alias
            device_row.enable = enable
        else: g.db.session.add(Devices(ip=ip, alias=alias, enable=enable))
        g.db.session.commit()
        rpif.host_ip_list[alias] = {'ip': ip, 'work': False, 'enable': enable}
    except:
        log.logger(['terminal', 'log'], f'addDevice: Can not add device "{alias} : {ip}" in to DB.')
    
def rmDevice(alias):
    removed = True if Devices.query.filter(Devices.alias == alias).delete() == 1 else False
    g.db.session.commit()
    rpif.host_ip_list.pop(alias)
    return removed

def toggleDevice(alias, toggle):
    device_row = Devices.query.filter(Devices.alias == alias).first()
    try:
        if device_row:
            if toggle in [1, True, "1"]: toggle = 1
            elif toggle in [0, False, "0"]: toggle = 0
            device_row.enable = toggle
            g.db.session.commit()
            rpif.host_ip_list[alias]['enable'] = toggle
            return {'type': 'success', 'msg': f'Toggled device: {toggle}.'}
        else: 
            log.logger(['terminal'], f'Device "{alias}" do not exist.')
            return {'type': 'error', 'msg': 'Device do not exist.'}
    except:
        log.logger(['terminal', 'log'], f'toggleDevice: Can not toggle device "{alias} : {toggle}" in to DB.')
        return {'type': 'error', 'msg': 'Exception error.'}


#------------------- STORAGE -------------------


def loadStorage(name):
    with g.app.app_context():
        storage_row = Storage.query.filter(Storage.name == name).first()
        if storage_row is None: return ''
        return storage_row

def saveStorage(name, value=''):
    with g.app.app_context():
        storage_row = Storage.query.filter(Storage.name == name).first()
        if storage_row:
            storage_row.value = f'{value}'
        else:
            g.db.session.add(Storage(name=name, value=f'{value}'))
        g.db.session.commit()