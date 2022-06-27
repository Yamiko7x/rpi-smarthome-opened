from time import sleep
import threading

from flask import Blueprint, jsonify, render_template, request

import dbcontroller.dbmanager as dbm
import extensions.globals as g
import extensions.sessionlink as sl
import extensions.logger  as log
import rpi.actions_system as ras
import rpi.rpi_factorys   as rpif

#________________________________________________________________________
#
# START VARS
#

command_bus = ''
active_smart_home_api_thread = None
rescan_thread = None


#________________________________________________________________________
#
# Comunicate with Smart Home API
#

def close_thread():
    global active_smart_home_api_thread

    ras.close_loops()
    ras.gpio_close()
    
    ras.vars_dict    = {}
    ras.actions_dict = {}
    ras.working_actions = {}
    
    rpif.factory_dict = {}

    log.logger(["terminal"], f'Cleared vars')
    active_smart_home_api_thread = None
    log.logger(["terminal"], f'Smart home api thread is stoped')

def api_pass(command : list):
    pass

def api_check_gpio_state(factoryAlias=None, gpioNr=None, path=None):
    gpioState = -1
    try:
        if path is not None:
            splited = path.split(' ')
            if len(splited) > 1: gpioState = rpif.factory_dict[splited[0]]['gpio_link'][int(splited[1])]['gpio_obj']
        else: 
            gpioState = rpif.factory_dict[factoryAlias]['gpio_link'][int(gpioNr)]['gpio_obj']
        if gpioState is not None:
            gpioState = gpioState.value
    except:
        pass
    return gpioState

def api_active_gpio(command : list):
    if rpif.factory_dict:
        if len(command) == 3: 
            gpioState = rpif.api_check_gpio_state(command[1], command[2])    
            log.logger(["terminal"], gpioState)
            return gpioState
        for factory, dict in rpif.factory_dict.items():
            active_gpio_list = []
            for gpio_num, pin in dict["gpio_link"].items():
                if pin["gpio_obj"] is not None:
                    active_gpio_list.append(f'Active GPIO: factory: {factory}, pin: {pin["pin"]}, gpio: {gpio_num}, binded to: {pin["binded_actions"]}')

            if active_gpio_list:
                for activepin in active_gpio_list:
                    log.logger(["terminal"], activepin)
            else:
                log.logger(["terminal"], f'Active GPIO not found.')
    else:
        log.logger(["terminal"], f'Active GPIO not found.')
        log.logger(["terminal"], f'Active factorys not found.')

def api_end(command : list):
    global run_api
    run_api = False

def api_status(command : list):
    log.logger(["terminal"], "Active api")

def api_get_var(action_id=None, varName=None, path=None):
    try:
        if path is not None:
            splited = path.split(' ')
            if len(splited) > 1: return ras.vars_dict[splited[0]][splited[1]]
        else:
            return ras.vars_dict[action_id][varName]
    except:
        return None

def api_vars(command : list):
    if ras.vars_dict:
        varValue = None
        if len(command) == 1: 
            for aid, dic in ras.vars_dict.items(): log.logger(["terminal"], f'\n{aid} : {dic}')
            return ras.vars_dict
        if len(command) == 2: varValue = api_get_var(command[1])
        if len(command) == 3: varValue = api_get_var(command[1], command[2])
        log.logger(["terminal"], varValue)
        return varValue
    else:
        log.logger(["terminal"], f'Vars storage is empty.')

def api_check_action_state(action_id):
    try:
        ras.working_actions[action_id]
        return True
    except:
        return False

def api_in_work(command : list):
    if ras.working_actions:
        if len(command) == 2:
            actionState = api_check_action_state(command[1])
            log.logger(["terminal"], actionState)
            return actionState
        for wa, dic in ras.working_actions.items():
            log.logger(["terminal"], f'\n{wa}')
    else:
        log.logger(["terminal"], f'Working actions not found.')

def api_actions(command : list):
    if ras.actions_dict:
        for aid, dic in ras.actions_dict.items():
            log.logger(["terminal"], f'\n{aid} : {dic["meta"]["name"]}')
    else:
        log.logger(["terminal"], f'Actions not found.')

def api_factorys(command : list):
    if rpif.factory_dict:
        for fac, dic in rpif.factory_dict.items():
            log.logger(["terminal", "log"], f'{fac} : {dic.keys()}')
    else:
        log.logger(["terminal"], f'Active factorys not found.')

def api_stop(command : list):
    # Stop available action by action_id
    if len(command) > 1: ras.stop_action(command[1])

def api_start(command : list):
    # Start available action by action_id
    if len(command) > 1: ras.start_action(command[1])

# Web terminal api available functions
api_fns_dict = {'help'      : {'fn' : api_pass,        'description' : 'Display all available commands.'},
                'run'       : {'fn' : api_pass,        'description' : 'Run smart home system.'},
                'end'       : {'fn' : api_end,         'description' : 'Stop smart home system.'},
                'status'    : {'fn' : api_status,      'description' : 'Show if api is active.'},
                'vars'      : {'fn' : api_vars,        'description' : 'Display all actions variables.'},
                'work'      : {'fn' : api_in_work,     'description' : 'Display all working actions.'},
                'actions'   : {'fn' : api_actions,     'description' : 'Display all loaded actions templates.'},
                'factorys'  : {'fn' : api_factorys,    'description' : 'Display all connected factorys (RPi devices).'},
                'stop'      : {'fn' : api_stop,        'description' : 'Stop action by action id like "stop autolight1".'},
                'start'     : {'fn' : api_start,       'description' : 'Start action by action id like "start autolight1".'},
                'gpio'      : {'fn' : api_active_gpio, 'description' : 'Display active GPIO.'}}


def watch_factorys_availability(): 
    global run_api
    global active_smart_home_api_thread
    sleep(10)
    if run_api and active_smart_home_api_thread:
        #log.logger(['terminal', 'log'], f'[ > ] Rescan devices')
        rpif.prepare_factorys(silent=True)
        threading.Thread(target=watch_factorys_availability, daemon=True).start()


def ping_devices(): 
    global run_api
    global active_smart_home_api_thread
    sleep(5)
    if run_api and active_smart_home_api_thread:
        factory_to_remove = {}
        for alias, dic in rpif.factory_dict.items():
            if not g.tryip(dic['ip']):
                sleep(3)
                if not g.tryip(dic['ip']):
                    factory_to_remove[alias] = dic['ip']
        
        for alias, ip in factory_to_remove.items():
            if not g.tryip(ip):
                log.logger(['terminal', 'log', 'war'], f'Stracono połącznie z "{alias}": {ip}')
                ras.gpio_close(factory_alias=alias)

        threading.Thread(target=ping_devices, daemon=True).start()


def start_smart_home_system():
    global command_bus
    global run_api
    global api_fns_dict
    global rescan_thread

    run_api = True
    
    # Check if can connect unavailable on startup
    threading.Thread(target=watch_factorys_availability, daemon=True).start()
    threading.Thread(target=ping_devices, daemon=True).start()

    while run_api:
        if command_bus:
            command = command_bus.split(' ')
            
            if command[0] in api_fns_dict:
                api_fns_dict[command[0]]["fn"](command)
            else:
                log.logger(["terminal", 'log', 'inf'], f'Komenda "{command_bus}" nie została znaleziona.')
            command_bus = ''
            
        else:
            sleep(0.5)
    
    log.logger(["terminal", 'log', 'war'], f'start_smart_home_system: Wywołano zatrzymanie wątku głónego dla API.')
    close_thread()
    

def aq_panel():
    global active_smart_home_api_thread

    dbm.loadDevices()
    if not rpif.factory_dict: rpif.prepare_factorys()

    if active_smart_home_api_thread is None:
        ras.loadActionsFromDB()
        active_smart_home_api_thread = threading.Thread(target=start_smart_home_system, daemon=True)
        active_smart_home_api_thread.start()
    else:
        log.logger(["terminal", 'log', 'inf'], f'aq_panel: Wątek smart home api jest uruchomiony.')
    return "Action Queue"

#________________________________________________________________________
#
# FLASK PART
#

smart_home_api = Blueprint("smart_home_api", __name__)


@smart_home_api.route("/aq_api_get_logs", methods=["POST"])
@sl.auth
def aq_api_get_logs():
    # Get terminal update
    
    first_page_load = request.get_json()["first_page_load"]
    return_history = []
    if first_page_load: return_history = log.get_all_terminal_history()
    else: return_history = log.get_terminal_history()

    return jsonify({'terminal_updates' : return_history})


@smart_home_api.route("/aq_api_request", methods=["POST"])
@sl.auth
def aq_api_request():
    # Send command
    global command_bus

    command = request.get_json()["commandline"]
    command = ras.translate_str(someStr=command)
    log.logger(["terminal"], f'[ > ] Przechwycono komendę: {command}')
    
    if command == "close_link" :
        uname = request.get_json()['user']
        sl.secret_connections.pop(uname)
        return jsonify({"auth":True, "msg":"Link closed"})

    if command == "clear" : log.history = []
    elif command == "help":
        for k, dic in api_fns_dict.items():
            log.logger(["terminal"], f'{k} : {dic["description"]}')
    elif command == "run"    : aq_panel()
    elif command == "thread" : log.logger(["terminal"], f'Smart home api thread status: {active_smart_home_api_thread}')
    elif command == "bus"    : log.logger(["terminal"], f'command_bus: {command_bus}')
    elif not command == "": 
        command_bus = command
    
    return jsonify({"auth":True, 'msg':f'Catched command: {command}', 'actionState' : True})

@smart_home_api.route("/terminal", methods=["GET"])
def aq_request():
    # Display web trminal
    # return ''
    return render_template("terminal.html", uname='admin', sessionlink=sl.create_sessionlink('admin'))

