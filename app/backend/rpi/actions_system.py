import copy
from sqlite3 import converters
from time import sleep
import time
import threading
import pprint
import re
from gpiozero import LED, MotionSensor, Button, Servo
import traceback

import extensions.logger as log
import rpi.rpi_factorys as rpif
import extensions.globals as g

from dbcontroller.dbtemplate import Actions
import dbcontroller.dbmanager as dbm
# ________________________________________________________________________
#
# STARTER VARS
#

vars_dict = {}
actions_dict = {}
working_actions = {}
stop_actions_list = []

# ________________________________________________________________________
#
# ACTION MANAGEMENT
#
def plus(a, b):
    if type(a) == type(""): a = int(a)
    if type(b) == type(""): b = int(b)
    return a + b


def convert(value, needtype='int', default=None, prefix='', sufix='', meta={}):
    success = True
    if isinstance(value, str):
        try:
            if needtype == 'int': value = int(value)
            elif needtype == 'float': value = float(value)
            else: 
                success = False
                if default: value = default
        except: 
            success = False
    elif isinstance(value, int) or isinstance(value, float):
        return value
    else:
        success = False

    if not success: 
        defval = '' if not defval else f' Zwrócono wartość domyślną {default}.'
        aid = '' if not meta else f'{meta["action_id"]}: '
        log.logger(['terminal', 'log', 'war'], f'{prefix}convert: {value}: {type(value)}:Nie można przekonwertować na {needtype}.{defval}{sufix}')
    
    return value


def translate_str(action={}, meta={}, someStr='', nested=False):
    pattern = r"(\$\{[^\}]+\})" if not nested else r"(\$\[[^\]]+\])"
    #print(someStr)
    someStr = f'{someStr}'
    maches = re.findall(pattern, someStr)
    #print(maches)

    if maches:
        for code in maches:
            #if nested: print(f'Nested: {code}')
            code_line = code[2:-1]
            #print(f'Code line: {code_line}')
            if re.match(r'^varid/.*', code_line) or code_line[0]=='/':
                varid = code_line.replace('varid', '')
                varid_value = get_var(path=varid, action=action, meta=meta)
                #print(f'Return someStr: {varid_value}')
                someStr = someStr.replace(code, f'{varid_value}', 1)
            elif code_line[0:3] == 'ev/':
                prepare_line = code_line.replace('ev/', '')
                #print(f'EV: {prepare_line}')
                if not nested: prepare_line = translate_str(action, meta, prepare_line, nested=True)
                #print(f'EV 2: {prepare_line}')
                try:
                    ev = eval(prepare_line)
                except Exception as e:
                    aid = f'{meta["action_id"]}: ' if 'action_id' in action else ''
                    log.logger(['terminal', 'log', 'evo'], f'translate_str:{aid} {e}')
                    ev = prepare_line
                someStr = someStr.replace(code, f'{ev}', 1)
        return someStr
    
    else: 
        #print(f'No matches. Nested: {nested}')
        return someStr


def loadActionsFromDB():
    allActions = Actions.query.all()
    for action in allActions:
        add_action({'meta': eval(action.meta),
                   'actions': eval(action.actions)})
    log.logger(['terminal', 'log'], '[ + ] Loaded actions from DB')


def action_id_exist(action_id):
    global actions_dict
    for k, a in actions_dict.items():
        aid = a["meta"]["action_id"]
        if aid == action_id:
            return True
    return False


def action_is_working(action_id):
    global working_actions
    return True if action_id in working_actions else False


def return_working_action(action_id):
    global working_actions
    return working_actions[action_id] if action_id in working_actions else False


def eval_action(actions, meta, first=False):
    global vars_dict
    global stop_actions_list

    if not meta['action_id'] in stop_actions_list:
        for action in actions:
            if action["fn"] in fns_dict():
                #print(f'DO: {action["fn"]}')
                fn = fns_dict()[action["fn"]]["fn"]
                try:
                    fn(action, meta)
                except Exception as e:
                    log.logger(['terminal', 'log', 'err'], f'eval_action: {e}')
                    break

            else:
                log.logger(['terminal', 'log', 'war'],
                        f'eval_action: {meta["action_id"]}: Nie można odnaleźć funkcji: {action["fn"]}')

    
    action_id = meta["action_id"]
    if first:
        if action_id in working_actions: working_actions.pop(action_id)
        if action_id in vars_dict: vars_dict.pop(action_id)
        if action_id in stop_actions_list: stop_actions_list.remove(action_id)
        log.logger(['terminal', 'log', 'run'], f'eval_action: Closed {action_id} : {meta["name"]}')


def gpio_close(gpio_factory_dict=None, action_id=None, factory_alias=None):
    # Close all gpio
    if gpio_factory_dict is None and factory_alias is None:
        #log.logger(['terminal', 'log'], f'close_gpios: gpio_factory_dict is None')
        for alias, factory in rpif.factory_dict.items():
            for gpio, pinDict in factory["gpio_link"].items():
                if pinDict["gpio_obj"] is not None:
                    try: pinDict["gpio_obj"].off()
                    except: pass

                    pinDict["gpio_obj"].close()
                    pinDict["gpio_obj"] = None
                    log.logger(['terminal', 'log', 'inf'], f'Closed GPIO {gpio}')
        rpif.factory_dict = {}
    
    #Clear selected gpio
    elif gpio_factory_dict is not None:
        #log.logger(['terminal', 'log'], f'close_gpios: gpio_factory_dict is not None')
        factory_alias = gpio_factory_dict["factory_alias"]
        gpio_num = gpio_factory_dict["gpio"]
        try:
            if 'gpio_obj' in rpif.factory_dict[factory_alias]['gpio_link'][gpio_num]:
                if rpif.factory_dict[factory_alias]['gpio_link'][gpio_num]['gpio_obj'] is not None:
                    if action_id in rpif.factory_dict[factory_alias]['gpio_link'][gpio_num]['binded_actions']:
                        rpif.factory_dict[factory_alias]['gpio_link'][gpio_num]['binded_actions'].remove(action_id)
                        working_actions[action_id]["binded_gpio"].remove(gpio_factory_dict)
                        
                    if len(rpif.factory_dict[factory_alias]['gpio_link'][gpio_num]['binded_actions']) == 0:
                        try: rpif.factory_dict[factory_alias]['gpio_link'][gpio_num]['gpio_obj'].off()
                        except: pass

                        rpif.factory_dict[factory_alias]['gpio_link'][gpio_num]['gpio_obj'].close()
                        rpif.factory_dict[factory_alias]['gpio_link'][gpio_num]['gpio_obj'] = None
        except Exception as e:
            log.logger(['terminal', 'log', 'err'], f'gpio_close: {e}')
    
    #Clear selectetd factory
    elif factory_alias is not None:
        #log.logger(['terminal', 'log'], f'close_gpios: factory_alias is not None')
        if factory_alias in rpif.factory_dict:
            factory = rpif.factory_dict[factory_alias]
            for gpio, pinDict in factory["gpio_link"].items():
                for action_id in pinDict['binded_actions']:
                    stop_action(action_id)
                    log.logger(["terminal"], f'Closed action {action_id}')

                if pinDict["gpio_obj"] is not None:
                    del pinDict["gpio_obj"]
                    pinDict["gpio_obj"] = None
                    log.logger(["terminal"], f'Closed GPIO {gpio}')

            del rpif.factory_dict[factory_alias]
            log.logger(['terminal', 'log', 'inf'], f'Removed factory "{factory_alias}". factory_dict: {rpif.factory_dict.keys()}')
            

def close_loops(action_id=None):
    global vars_dict
    global stop_actions_list
    global working_actions

    if action_id:
        if not action_id in stop_actions_list:
            stop_actions_list.append(action_id)

    elif action_id is None: 
        log.logger(['terminal', 'log', 'war'], f'close_loops: action_id ma wartość None. Zamykam wszystkie akcjie.')

        for aid in working_actions:
            if not action_id in stop_actions_list:
                stop_actions_list.append(aid)


def stop_action(action_id):
    if action_id in working_actions:
        if not action_id in stop_actions_list:
            stop_actions_list.append(action_id)

        close_loops(action_id)

        if "binded_gpio" in working_actions[action_id]:
            binded_gpio = working_actions[action_id]["binded_gpio"]
            for gpio_and_factory_dict in binded_gpio:
                gpio_close(gpio_and_factory_dict, action_id)
        del working_actions[action_id]
    
    else: log.logger(['treminal', 'log', 'war'], f'stop_action: Akcji {action_id} nie ma w liście akcji działających.')


def start_action(action_id, force=False, manual=True):
    if action_id in stop_actions_list:
        log.logger(['terminal', 'log', 'inf'], f'start_action: Akcja nosi oznaczenia "Do zatrzymania"')
    elif (not action_is_working(action_id) or force) and action_id in actions_dict:
        if not actions_dict[action_id]['meta']['active']:
            log.logger(["terminal", 'log', 'inf'], f'start_action: Akcja jest zdezaktywowana: {action_id} : {actions_dict[action_id]["meta"]["name"]}')
            return False

        else:
            new_working_action = {"meta": actions_dict[action_id]["meta"],
                                "actions": actions_dict[action_id]["actions"],
                                "thread": threading.Thread(target=eval_action,
                                                            daemon=True,
                                                            args=( actions_dict[action_id]["actions"], 
                                                                    actions_dict[action_id]["meta"], 
                                                                    True)),
                                "binded_gpio": []}
                                
            vars_dict[action_id] = {'working': True}
            working_actions[action_id] = new_working_action
            if manual:
                log.logger(
                    ["terminal", 'log', 'run'], f'start_action: Start: {action_id} : {actions_dict[action_id]["meta"]["name"]}')

            else:
                log.logger(
                    ["terminal", 'log', 'run'], f'start_action: Autostart of: {action_id} : {actions_dict[action_id]["meta"]["name"]}')

            new_working_action["thread"].start()


def fn_stop_action(action, meta):
    stop_action(action["action_id"])


def fn_start_action(action, meta):
    start_action(action["action_id"])


def add_action(action, update=False):
    aid = action["meta"]["action_id"]
    if action_id_exist(aid) and update is False:
        log.logger(["terminal", 'log', 'war'], "Action id is reserved. Change action id.")
    else:
        aid = action["meta"]["action_id"]
        actions_dict[aid] = action
        if action["meta"]["autostart"] and action["meta"]["active"]:
            start_action(aid, manual=False)


def reload_actions():
    global actions_dict
    for aid, action in actions_dict.items():
        if action["meta"]["autostart"] and action["meta"]["active"]:
            start_action(aid, manual=False)

# ________________________________________________________________________
#
# AVAILABLE FUNCTIONS FOR ACTIONS QUEUE
#

def gpio_check(action={}, meta={}, factory='', gpio_nr=None):   
    if not factory and 'factory' in action: factory = action['factory']
    if not gpio_nr and 'gpio_nr' in action: gpio_nr = action['gpio_nr']

    gpio_nr = convert(gpio_nr, 'int', -1, prefix='gpio_check', meta=meta)

    gpio_state = -1

    if factory and gpio_nr:
        if factory in rpif.factory_dict:
            if 'gpio_obj' in rpif.factory_dict[factory]['gpio_link'][gpio_nr]:
                if rpif.factory_dict[factory]['gpio_link'][gpio_nr]['gpio_obj']:
                    gpio_state = rpif.factory_dict[factory]['gpio_link'][gpio_nr]['gpio_obj'].value
                #else:
                    #log.logger(['terminal', 'log', 'inf'], f'gpio_check: "gpio_obj" to None. Ścieżka: rpif.factory_dict["{factory}"]["gpio_link"][{gpio_nr}]["gpio_obj"]')
            else:
                log.logger(['terminal', 'log', 'war'], f'gpio_check: "gpio_obj" nie istnieje w rpif.factory_dict["{factory}"]["gpio_link"][{gpio_nr}]')
        else:
            log.logger(['terminal', 'log', 'war'], f'gpio_check: factory "{factory}" is not in rpif.factory_dict')
            #pprint.PrettyPrinter().pprint(rpif.factory_dict)
    else:
        if not factory: log.logger(['terminal', 'log', 'war'], f'gpio_check: factory "{factory}" is empty')
        if not gpio_nr: log.logger(['terminal', 'log', 'war'], f'gpio_check: gpio_nr "{gpio_nr}" is empty')
        
    if gpio_state == 1 and 'actions_on' in action: 
        eval_action(action["actions_on"], meta)
    elif gpio_state == 0 and 'actions_off' in action:
        eval_action(action["actions_off"], meta)
    elif 'actions_none' in action: 
        eval_action(action["actions_none"], meta)

    log.logger(['terminal'], f'GPIO state: {gpio_state}')
    return gpio_state


def get_var(action={}, meta={}, path=None, default=0):
    global vars_dict
    
    if 'path' in action and not path: path = action['path']
    if 'default' in action and not default: default = action['default']

    path = path.split('/')
    if not path[0]: path.pop(0)

    if path and vars_dict and path[-1]:
        prefix = f'vars_dict'
        nextstep = ''
        path_len = len(path)

        if path_len == 1: 
            aid = meta['action_id'] if meta['action_id'] else 'global'
            path.insert(0, aid)
            path_len += 1

        for idx, p in enumerate(path):
            nextstep = f'["{p}"]'

            try: eval(f'{prefix}{nextstep}')
            except:
                newdict = {p: {}}
                if idx+1 == path_len: newdict = {p: default}

                eval(f'{prefix}.update({newdict})')

            prefix = f'{prefix}{nextstep}'

        return eval(prefix)


def set_var(action={}, meta={}, path='', value=''):
    global vars_dict
    
    if 'path' in action and not path: path = action['path']
    if 'value' in action and not value: value = action['value']
    value = translate_str(action=action, meta=meta, someStr=value)

    path = path.split('/')
    if not path[0]: path.pop(0)

    if path and vars_dict and path[-1]:
        prefix = f'vars_dict'
        nextstep = ''
        path_len = len(path)

        if path_len == 1: 
            aid = meta['action_id'] if meta['action_id'] else 'global'
            path.insert(0, aid)
            path_len += 1

        for idx, p in enumerate(path):
            nextstep = f'["{p}"]'

            try: 
                eval(f'{prefix}{nextstep}')
                if idx+1 == path_len: 
                    newdict = {p: value}
                    eval(f'{prefix}.update({newdict})')
            except:
                newdict = {p: {}}
                if idx+1 == path_len: newdict = {p: value}
                eval(f'{prefix}.update({newdict})')

            prefix = f'{prefix}{nextstep}'

        return ''


def set_to_list(action, meta): # TODO: Don't work! Rewrite!
    global vars_dict
    path = action["varid"].split('/')
    val = action["value"] if "value" in action else ""
    
    aid = ''
    vid = ''

    if len(path) == 1:
        aid = meta["action_id"]
        vid = path[0]
    
    elif len(path) == 2:
        aid = meta['action_id'] if path[0] == "" else path[0]
        vid = path[1]

    if aid and vid:
        if not aid in vars_dict:
            vars_dict[aid] = {}
        
        if not vid in vars_dict[aid]:
            vars_dict[aid][vid] = [val]

        elif type(vars_dict[aid][vid]) == type([]):
            vars_dict[aid][vid].append(val)

        else: vars_dict[aid][vid] = [vars_dict[aid][vid], val]


def myprint(action, meta):
    global vars_dict
    
    text = ""
    if "text" in action:
        text = action["text"]
        text = translate_str(action, meta, text)

    if text: log.logger(["terminal"], text)


def loop(action, meta):
    global vars_dict
    global stop_actions_list

    if action["type"] == "while":
        while not meta["action_id"] in stop_actions_list:
            eval_action(action["actions"], meta)
            mysleep(action, meta)

    elif action["type"] == "for":
        for x in range(action["range"]):
            if not meta["action_id"] in stop_actions_list:
                eval_action(action["actions"], meta)
                mysleep(action, meta)
            else:
                break


def add_value(action, meta):
    if "path" in action:
        for prop in ['path', 'value']:
            if not prop in action: return 0

        value = get_var(action=action, meta=meta, path=action['path'])
        toadd = action['value']

        if isinstance(value, str):
            try: value = float(value)
            except: return 0

        if isinstance(toadd, str):
            try: toadd = float(toadd)
            except: return 0

        set_var(path=action['path'], value=value+toadd, action=action, meta=meta)


def mysleep(action, meta=None):
    global stop_actions_list

    if 'sleep' in action:
        sek = convert(action['sleep'], 'float', 0, prefix='mysleep: ', meta=meta)
        if sek <= 1:
            sleep(sek)
        else:
            waitfor = time.time() + sek
            while waitfor > time.time():
                if meta['action_id'] in stop_actions_list:  break
                else: sleep(0.1)


def ifvar(action, meta):
    value1 = translate_str(action, meta, action["value1"])
    value2 = translate_str(action, meta, action["value2"])

    if not type(value1) == type(value2):
        if isinstance(value1, str):
            try: value1 = float(value1)
            except: pass

        if isinstance(value2, str):
            try: value2 = float(value2)
            except: pass

    if not type(value1) == type(value2):
        log.logger(
            ['terminal', 'log', 'inf'], f'ifvar: value1 nad value2 have different types: {type(value1)}: {value1} != {value2} :{type(value2)}')

    elif value1 and value2:
        if action["cond"] == ">":
            if value1 > value2:
                eval_action(action["iftrue"], meta)
            else:
                if "iffalse" in action:
                    eval_action(action["iffalse"], meta)

        elif action["cond"] == "<":
            if value1 < value2:
                eval_action(action["iftrue"], meta)
            else:
                if "iffalse" in action:
                    eval_action(action["iffalse"], meta)

        elif action["cond"] == "=":
            if value1 == value2:
                eval_action(action["iftrue"], meta)
            else:
                if "iffalse" in action:
                    eval_action(action["iffalse"], meta)

        elif action["cond"] == "!=":
            if not value1 == value2:
                eval_action(action["iftrue"], meta)
            else:
                if "iffalse" in action:
                    eval_action(action["iffalse"], meta)


def getdatetime(format='datetime'):
    return g.getDateTime(format)


def getStorage(name): #, separator = '', fromto = []):
    loaded = dbm.loadStorage(name)
    ''' if not separator == '':
        splited = loaded.value.split(separator)
        if fromto: return eval(f'splited{fromto}')
        else: return splited '''
    return loaded.value


def setStorage(action, meta):
    if not 'name'      in action: return False
    if not 'save_mode' in action: return False
    if not 'content'   in action: return False
    if not 'separator' in action: return False

    if action['save_mode'] in ['a', 'w']:
        content = translate_str(action, meta, action['content'])
        if action['save_mode'] == 'w': 
            dbm.saveStorage(action['name'], content)
        elif action['save_mode'] == 'a':
            loaded = getStorage(action['name'])
            separator = action['separator']
            dbm.saveStorage(action['name'], f'{loaded}{separator}{content}')


#------------- GPIO FNS


def gpio_motion_detect(action, meta):
    global stop_actions_list

    if not "factory" in action:
        return 0
    if not "gpio" in action:
        return 0

    gpio = convert(action["gpio"], prefix='gpio_motion_detect: ', meta=meta)
    if not isinstance(gpio, int): return False
    aid = meta["action_id"]

    if not action["factory"] in rpif.factory_dict:
        return 0
    selected_factory = rpif.factory_dict[action["factory"]]
    factory = selected_factory["factory"]

    working_actions[aid]["binded_gpio"].append(
        {"factory_alias": action["factory"], "gpio": gpio})

    gpio_link = selected_factory["gpio_link"]

    if "gpio_obj" in gpio_link[gpio]:
        if gpio_link[gpio]["gpio_obj"] is None:
            gpio_link[gpio]["gpio_obj"] = MotionSensor(gpio, pin_factory=factory)

        elif aid in gpio_link[gpio]["binded_actions"]:
            try: gpio_link[gpio]["gpio_obj"].off()
            except: pass
            gpio_link[gpio]["gpio_obj"].close()
            del gpio_link[gpio]["gpio_obj"]
            gpio_link[gpio]["gpio_obj"] = MotionSensor(gpio, pin_factory=factory)
            log.logger(["terminal"], f"GPIO {gpio} restarted")

        if not aid in gpio_link[gpio]['binded_actions']:
            gpio_link[gpio]['binded_actions'].append(aid)

    else:
        gpio_link[gpio]["gpio_obj"] = MotionSensor(gpio, pin_factory=factory)

    while not aid in stop_actions_list:
        if gpio_link[gpio]["gpio_obj"].is_active:
            eval_action(action["actions_on"], meta)
        elif "actions_off" in action:
            eval_action(action["actions_off"], meta)
        mysleep(action, meta)


def gpio_watch(action, meta):
    global stop_actions_list
    aid = meta["action_id"]

    if not "factory" in action:
        return 0
    if not "gpio" in action:
        return 0

    gpio = convert(action["gpio"], prefix='gpio_watch: ', meta=meta)
    if not isinstance(gpio, int): return False

    if not action["factory"] in rpif.factory_dict:
        return 0

    gpio_link = rpif.factory_dict[action["factory"]]["gpio_link"]

    while not aid in stop_actions_list:
        if "gpio_obj" in gpio_link[gpio]:
            if not meta["action_id"] in gpio_link[gpio]['binded_actions']:
                gpio_link[gpio]['binded_actions'].append(meta["action_id"])
            
            if gpio_link[gpio]["gpio_obj"] is not None:
                if gpio_link[gpio]["gpio_obj"].value:
                    eval_action(action["actions_on"], meta)
                else:
                    eval_action(action["actions_off"], meta)
            else:
                eval_action(action["actions_none"], meta)
        else:
            eval_action(action["actions_none"], meta)
        sleep(action["sleep"])


def ir_sensor_only(action, meta):
    if not "factory" in action:
        return 0
    if not "gpio" in action:
        return 0

    gpio = convert(action["gpio"], prefix='ir_sensor_only: ', meta=meta)
    if not isinstance(gpio, int): return False

    if not action["factory"] in rpif.factory_dict:
        return 0
    selected_factory = rpif.factory_dict[action["factory"]]
    factory = selected_factory["factory"]

    # TODO: Dodaj action_id jako binded w slowniku gpio

    gpio_link = selected_factory["gpio_link"]

    if "gpio_obj" in gpio_link[gpio]:
        if not meta["action_id"] in gpio_link[gpio]['binded_actions']:
            gpio_link[gpio]['binded_actions'].append(meta["action_id"])

        if gpio_link[gpio]["gpio_obj"] is None:
            gpio_link[gpio]["gpio_obj"] = Button(gpio, pin_factory=factory)
    else:
        gpio_link[gpio]["gpio_obj"] = Button(gpio, pin_factory=factory)


def gpio_switch(action, meta):
    if not "factory" in action:
        return 0
    if not "gpio" in action:
        return 0

    gpio = convert(action["gpio"], prefix='gpio_switch: ', meta=meta)
    if not isinstance(gpio, int): return False

    if not action["factory"] in rpif.factory_dict:
        return 0
    selected_factory = rpif.factory_dict[action["factory"]]
    factory = selected_factory["factory"]

    gpio_link = selected_factory["gpio_link"]

    if "gpio_obj" in gpio_link[gpio]:
        if not meta["action_id"] in gpio_link[gpio]['binded_actions']:
            gpio_link[gpio]['binded_actions'].append(meta["action_id"])

        if gpio_link[gpio]["gpio_obj"] is None:
            if action["state"] == "0":
                gpio_link[gpio]["gpio_obj"] = LED(gpio, pin_factory=factory)
                gpio_link[gpio]["gpio_obj"].off()
            if action["state"] == "1":
                gpio_link[gpio]["gpio_obj"] = LED(gpio, pin_factory=factory)
                gpio_link[gpio]["gpio_obj"].on()

        else:
            if action["state"] == "1" and gpio_link[gpio]["gpio_obj"].value == 0:
                gpio_link[gpio]["gpio_obj"].on()
            elif action["state"] == "0" and gpio_link[gpio]["gpio_obj"].value == 1:
                gpio_link[gpio]["gpio_obj"].off()
            elif action["state"] == "-1":
                try: gpio_link[gpio]["gpio_obj"].off()
                except: pass
                gpio_link[gpio]["gpio_obj"].close()
                del gpio_link[gpio]["gpio_obj"]
                gpio_link[gpio]["gpio_obj"] = None
    else:
        if action["state"] == "0":
            gpio_link[gpio]["gpio_obj"] = LED(gpio, pin_factory=factory)
            gpio_link[gpio]["gpio_obj"].off()
        elif action["state"] == "1":
            gpio_link[gpio]["gpio_obj"] = LED(gpio, pin_factory=factory)
            gpio_link[gpio]["gpio_obj"].on()


def gpio_servo(action, meta):
    if not "factory" in action:
        return 0
    if not "gpio" in action:
        return 0

    aid = meta["action_id"]
    gpio = convert(action["gpio"])
    frame_width = convert(action["frame_width"])
    max_pulse_width = convert(action["max_pulse_width"])
    
    gpio = convert(action["gpio"], prefix='gpio_servo: ', meta=meta)
    if not isinstance(gpio, int): return False

    frame_width = convert(action["frame_width"], prefix='gpio_servo: ', meta=meta)
    if not isinstance(frame_width, int): return False

    max_pulse_width = convert(action["max_pulse_width"], prefix='gpio_servo: ', meta=meta)
    if not isinstance(max_pulse_width, int): return False

    if not action["factory"] in rpif.factory_dict:
        return 0
    selected_factory = rpif.factory_dict[action["factory"]]
    factory = selected_factory["factory"]

    working_actions[aid]["binded_gpio"].append(
        {"factory_alias": action["factory"], "gpio": gpio})

    gpio_link = selected_factory["gpio_link"]

    def newServo():
        return Servo(gpio, pin_factory=factory, min_pulse_width=1/1000, max_pulse_width=max_pulse_width/1000, frame_width=frame_width/1000)

    if "gpio_obj" in gpio_link[gpio]:
        if gpio_link[gpio]["gpio_obj"] is None:
            gpio_link[gpio]["gpio_obj"] = newServo()
            if not aid in gpio_link[gpio]['binded_actions']:
                gpio_link[gpio]['binded_actions'].append(aid)

    else:
        gpio_link[gpio]["gpio_obj"] = newServo()
        if not aid in gpio_link[gpio]['binded_actions']:
            gpio_link[gpio]['binded_actions'].append(aid)

    if aid in gpio_link[gpio]["binded_actions"]:
        if 'angle' in action:
            angle = translate_str(action, meta, action['angle'])
            try:
                if type(angle) == type(""): angle = float(angle)
            except:
                angle = -1

            if angle > 1: angle = 1
            elif angle < -1: angle = -1
            gpio_link[gpio]["gpio_obj"].value = angle

            if 'sleep' in action:
                mysleep(action, meta)

            if 'release' in action:
                rel = action['release']
                if rel in [1, '1']: gpio_release(action, meta)


def gpio_release(action, meta):
    factory_alias = action['factory']
    gpio_nr = action['gpio']
    gpio_link = rpif.factory_dict[factory_alias]["gpio_link"]
    if "gpio_obj" in gpio_link[gpio_nr]:
        try: gpio_link[gpio_nr]["gpio_obj"].off()
        except: pass
        gpio_link[gpio_nr]["gpio_obj"].close()
        if meta['action_id'] in gpio_link[gpio_nr]["binded_actions"]:
            gpio_link[gpio_nr]["binded_actions"].remove(meta['action_id'])
        del gpio_link[gpio_nr]["gpio_obj"]
        gpio_link[gpio_nr]["gpio_obj"] = None
        log.logger(['terminal', 'log', 'inf'], f'gpio_release: Release GPIO {gpio_nr}')


def getFactorysForSelect():
    factorysList = []
    for fac in rpif.host_ip_list:
        factorysList.append([fac, fac])
    return factorysList

# ________________________________________________________________________
#
# FUNCTION DICTIONARY FOR ACTIONS QUEUE
#


def fns_dict(): 
    return {
    "loop": {"fn": loop,
             "tip": "zapętlenie",
             "desc": "Wybierz while by pętla powtarzała zaimplementowane w niej akcje bez ograniczeń lub for by wykonać je określoną ilość razy.",
             "rules": [{"prop": "type",
                        "label": "Typ",
                        "component": "select",
                        "options": [["while", "While"], ["for", "For"]],
                        "default": "while",
                        "required": True},
                       {"prop": "sleep",
                        "label": "Sleep",
                        "component": "inputNumber",
                        "min": 0.1,
                        "default": 1,
                        "required": True},
                       {"prop": "range",
                        "label": "Ile pętli",
                        "component": "inputNumber",
                        "default": 0,
                        "min": 0,
                        "placeholder": "ID pętli",
                        "required": False},
                       {"prop": "actions",
                        "label": "Kolejka akcji",
                        "component": "actionQueue",
                        "default": [],
                        "required": False}]},

    "ifvar": {"fn": ifvar,
              "tip": "warunek",
              "desc": "Instrukcja warunkowa pozwalająca wybrać kolejkę akcji na podstawie innych parametrów.",
              "rules": [{"prop": "value1",
                        "label": "Wartość A",
                         "component": "inputText",
                         "default": "",
                         "placeholder": "Wartość A",
                         "required": True},
                        {"prop": "cond",
                        "label": "Warunek",
                         "component": "select",
                         "options": [["<", "mniejszy"], [">", "większy"], ["==", "równy"]],
                         "default": "<",
                         "required": True},
                        {"prop": "value2",
                        "label": "Wartość B",
                         "component": "inputText",
                         "default": "",
                         "placeholder": "Wartość B",
                         "required": True},
                        {"prop": "iftrue",
                        "label": "Kolejka akcji na True",
                         "component": "actionQueue",
                         "default": [],
                         "required": False},
                        {"prop": "iffalse",
                        "label": "Kolejka akcji na False",
                         "component": "actionQueue",
                         "default": [],
                         "required": False}]},

    "gpio_motion_detect": {"fn": gpio_motion_detect,
                      "tip": "czujnik ruchu",
                      "desc": "Wykonaj akcje na wykrycie ruchu bądź zaprzestanie go.",
                      "rules": [{"prop": "factory",
                                "label": "Factory alias",
                                "component": "select",
                                "options": getFactorysForSelect(),
                                "default": getFactorysForSelect()[0][0] if getFactorysForSelect() else '',
                                "required": True},
                                {"prop": "gpio",
                                 "label": "Nr GPIO",
                                 "component": "inputNumber",
                                 "min":  2,
                                 "max":  27,
                                 "default": "21",
                                 "required": True},
                                {"prop": "sleep",
                                 "label": "Sleep",
                                 "component": "inputNumber",
                                 "min": 0.1,
                                 "default": 1,
                                 "required": True},
                                {"prop": "actions_on",
                                 "label": "Kolejka akcji na ruch",
                                 "component": "actionQueue",
                                 "default": [],
                                 "required": False},
                                {"prop": "actions_off",
                                 "label": "Kolejka akcji na bezruch",
                                 "component": "actionQueue",
                                 "default": [],
                                 "required": False}]},

    "gpio_watch": {"fn": gpio_watch,
                   "tip": "czujnik ruchu",
                   "desc": "Wykonaj akcje na wykrycie ruchu bądź zaprzestanie go.",
                   "rules": [{"prop": "factory",
                                "label": "Factory alias",
                                "component": "select",
                                "options": getFactorysForSelect(),
                                "default": getFactorysForSelect()[0][0] if getFactorysForSelect() else '',
                                "required": True},
                             {"prop": "gpio",
                                 "label": "Nr GPIO",
                                 "component": "inputNumber",
                                 "min":  2,
                                 "max":  27,
                                 "default": "21",
                                 "required": True},
                             {"prop": "sleep",
                                 "label": "Sleep",
                                 "component": "inputNumber",
                                 "min": 0.1,
                                 "default": 1,
                                 "required": True},
                             {"prop": "actions_none",
                                 "label": "Kolejka akcji gdy GPIO nieaktywny",
                                 "component": "actionQueue",
                                 "default": [],
                                 "required": False},
                             {"prop": "actions_on",
                                 "label": "Kolejka akcji gdy GPIO wysoki",
                                 "component": "actionQueue",
                                 "default": [],
                                 "required": False},
                             {"prop": "actions_off",
                                 "label": "Kolejka akcji gdy GPIO niski",
                                 "component": "actionQueue",
                                 "default": [],
                                 "required": False}]},

    "print": {"fn": myprint,
              "tip": "console print",
              "desc": "Wypisz tekst w konsoli na serwerze.",
              "rules": [{"prop": "text",
                         "label": "Tekst",
                         "component": "inputText",
                         "default": "",
                         "placeholder": "Some text",
                         "required": False}]},

    "sleep": {"fn": mysleep,
              "tip": "wstrzymaj akcję",
              "desc": "Wstrzymaj akcję na pewien czas (sleep 1 == 1 sekunda).",
              "rules": [{"prop": "sleep",
                         "label": "Sleep",
                                 "component": "inputNumber",
                                 "min": 0.1,
                                 "default": 1,
                                 "required": True}]},

    "setvar": {"fn": set_var,
               "tip": "ustaw wartość",
               "desc": "Wstaw wartość do banku pamięci.",
               "rules": [{"prop": "path",
                          "label": "Var Path",
                                  "component": "inputText",
                                  "default": "",
                                  "placeholder": "/action_id/varid or /varid",
                                  "required": True},
                         {"prop": "value",
                          "label": "Wartość",
                                  "component": "inputText",
                                  "default": "",
                                  "placeholder": "Wstaw wartość (opcjonalnie)",
                                  "required": False}]},

    "set_to_list": {"fn": set_to_list,
               "tip": "dopnij następną",
               "desc": "Dodaj nową wartość do listy. Jeśli wartość istnieje bez listy, wstaw ją jako pierwszą w nowej liście i dodaj przekazaną. Wzór: {varid : [value1, vlaue2, ...]}",
               "rules": [{"prop": "varid",
                          "label": "Var ID",
                                  "component": "inputText",
                                  "default": "",
                                  "placeholder": "action_id/varid or /varid",
                                  "required": True},
                         {"prop": "value",
                          "label": "Wartość",
                                  "component": "inputText",
                                  "default": "",
                                  "placeholder": "Wstaw wartość",
                                  "required": True}]},

    "add_value": {"fn": add_value,
            "tip": "dodaj do var",
            "desc": "Użyj by dodać liczbę (lub odjąć podając ujemną) do istniejącej wartości w słowniku zmiennych.",
            "rules": [{"prop": "path",
                       "label": "Var path",
                       "component": "inputText",
                       "default": "",
                       "placeholder": "/action_id/varid or /varid",
                       "required": True},
                      {"prop": "value",
                       "label": "Wartość",
                        "component": "inputNumber",
                       "default": "0",
                       "placeholder": "Domyślnie +1",
                       "required": False}]},

    "action_start": {"fn": fn_start_action,
                     "tip": "uruchom akcję",
                     "desc": "Uruchom wcześniej przygotowaną kolejkę akcji podając jej action_id.",
                     "rules":  [{"prop": "action_id",
                                "label": "ID Akcji",
                                 "component": "inputText",
                                 "default": "",
                                 "placeholder": "action_id",
                                 "required": True}]},

    "action_stop": {"fn": fn_stop_action,
                    "tip": "zatrzymaj akcję",
                    "desc": "Zatrzymaj uruchomioną kolejkę akcji podając jej action_id.",
                    "rules": [{"prop": "action_id",
                               "label": "ID Akcji",
                               "component": "inputText",
                               "default": "",
                                            "placeholder": "action_id",
                                            "required": True}]},

    "gpio_check": {"fn": gpio_check,
              "tip": "sprawdź GPIO",
              "desc": "Sprawdź stan GPIO i wykonaj akcję. Funkcja dodatkowo zrwaca stan.",
              "rules": [{"prop": "factory",
                            "label": "Factory alias",
                            "component": "select",
                            "options": getFactorysForSelect(),
                            "default": getFactorysForSelect()[0][0] if getFactorysForSelect() else '',
                            "required": True},
                        {"prop": "gpio_nr",
                            "label": "Nr GPIO",
                            "component": "inputNumber",
                            "min":  2,
                            "max":  27,
                            "default": "21",
                            "required": True},
                        {"prop": "actions_none",
                            "label": "Kolejka akcji gdy GPIO nieaktywny",
                            "component": "actionQueue",
                            "default": [],
                            "required": False},
                        {"prop": "actions_on",
                            "label": "Kolejka akcji gdy GPIO wysoki",
                            "component": "actionQueue",
                            "default": [],
                            "required": False},
                        {"prop": "actions_off",
                            "label": "Kolejka akcji gdy GPIO niski",
                            "component": "actionQueue",
                            "default": [],
                            "required": False}]},

    "gpio_switch": {"fn": gpio_switch,
                    "tip": "przełącz stan gpio",
                    "desc": "Zmień stan wybranego pinu (GPIO).",
                    "rules": [{"prop": "factory",
                                "label": "Factory alias",
                                "component": "select",
                                "options": getFactorysForSelect(),
                                "default": getFactorysForSelect()[0][0] if getFactorysForSelect() else '',
                                "required": True},
                              {"prop": "gpio",
                               "label": "Nr GPIO",
                               "component": "inputNumber",
                               "min":  2,
                               "max":  27,
                               "default": "21",
                                       "required": True},
                              {"prop": "state",
                               "label": "Stan GPIO",
                               "component": "select",
                               "options": [["-1", "Nieaktywny", ], ["0", "Niski"], ["1", "Wysoki"]],
                               "default": "-1",
                               "required": True}]},

    "gpio_ir_sensor": {"fn": ir_sensor_only,
                       "tip": "Bezakcyjny czujnik odbicia IR",
                       "desc": "Podłącz do GPIO czujnik odbicia IR (bez wywoływania akcji).",
                       "rules": [{"prop": "factory",
                                "label": "Factory alias",
                                "component": "select",
                                "options": getFactorysForSelect(),
                                "default": getFactorysForSelect()[0][0] if getFactorysForSelect() else '',
                                "required": True},
                                 {"prop": "gpio",
                                 "label": "Nr GPIO",
                                  "component": "inputNumber",
                                  "min":  2,
                                  "max":  27,
                                  "default": "21",
                                  "required": True}]},

    "gpio_servo": {"fn": gpio_servo,
                       "tip": "Steruj serwem",
                       "desc": "Steruj serwem podając zakres od -1.0 do 1.0. Kąt serwa to od 0 do 180 stopni. Servo powinno być zasilane osobnym źródłem niż raspberry.",
                       "rules": [{"prop": "factory",
                                "label": "Factory alias",
                                "component": "select",
                                "options": getFactorysForSelect(),
                                "default": getFactorysForSelect()[0][0] if getFactorysForSelect() else '',
                                "required": True},
                                 {"prop": "gpio",
                                 "label": "Nr GPIO",
                                  "component": "inputNumber",
                                  "min":  2,
                                  "max":  27,
                                  "default": "21",
                                  "required": True},
                                 {"prop": "angle",
                                 "label": "Kąt [-1 : 1]",
                                  "component": "inputNumber",
                                  "default": "0",
                                  "min": -1,
                                  "max": 1,
                                  "required": True},
                                 {"prop": "frame_width",
                                 "label": "frame_width",
                                  "component": "inputNumber",
                                  "default": "160",
                                  "min": 0,
                                  "max": 1000,
                                  "required": True},
                                 {"prop": "max_pulse_width",
                                 "label": "max_pulse_width",
                                  "component": "inputNumber",
                                  "default": "4",
                                  "min": 0,
                                  "max": 1000,
                                  "required": True},
                                {"prop": "sleep",
                                    "label": "Sleep",
                                    "component": "inputNumber",
                                    "min": 0.1,
                                    "default": 0.1,
                                    "required": True},
                                  {"prop": "release",
                                    "label": "Zwolnij GPIO",
                                    "component": "select",
                                    "options": [[0, "Nie"], [1, "Tak"]],
                                    "default": 0,
                                    "required": True},]},

    "gpio_release": {"fn": gpio_release,
                       "tip": "Zwolnij GPIO",
                       "desc": "Zwolnij zajęte GPIO.",
                       "rules": [{"prop": "factory",
                                "label": "Factory alias",
                                "component": "select",
                                "options": getFactorysForSelect(),
                                "default": getFactorysForSelect()[0][0] if getFactorysForSelect() else '',
                                "required": True},
                                 {"prop": "gpio",
                                 "label": "Nr GPIO",
                                  "component": "inputNumber",
                                  "min":  2,
                                  "max":  27,
                                  "default": "21",
                                  "required": True}]},

    "setStorage": {"fn": setStorage,
                       "tip": "Zapisz do bazy",
                       "desc": "Zapisz dane do bazy podając nazwę jako identyfikator i wartość do zapisu.",
                       "rules": [{"prop": "name",
                                 "label": "Nazwa",
                                  "component": "inputText",
                                  "default": "",
                                  "required": True},
                                  {"prop": "save_mode",
                                 "label": "Tryb",
                                  "component": "select",
                                  "options":[['a', 'Dopisz'], ['w', 'Nadpisz']],
                                  "default": "w",
                                  "required": True},
                                  {"prop": "content",
                                 "label": "Wartość",
                                  "component": "inputText",
                                  "default": "",
                                  "required": True},
                                  {"prop": "separator",
                                 "label": "Separator",
                                  "component": "inputText",
                                  "default": ";",
                                  "required": True}]},
}


def getSimpleFnsDict():
    dictCopy = copy.deepcopy(fns_dict())

    for key, dic in dictCopy.items():
        del dic['fn']

    return dictCopy
