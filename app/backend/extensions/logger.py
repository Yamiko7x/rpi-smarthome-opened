
from datetime import date, datetime
from flask import jsonify
import traceback

#________________________________________________________________________
#
# Logger
#

# Logs storage
logs = []
terminal_history = []

def logger(groups : list, message : str):
    global logs
    global terminal_history

    now   = datetime.now()
    today = date.today()
    current_time = now.strftime("%H:%M:%S")
    current_date = today.strftime("%d/%m/%Y")
    time = f'{current_date} {current_time}'

    if 'err' in groups: message = f'[ x ] {message}\n{traceback.format_exc()}{"-"*40}'
    if 'run' in groups: message = f'[>_ ] {message}'
    if 'inf' in groups: message = f'[ ? ] {message}'
    if 'war' in groups: message = f'[ ! ] {message}'
    if 'suc' in groups: message = f'[ + ] {message}'
    if 'evo' in groups: message = f'[ _<] {message}'

    if "terminal" in groups:
        mess = message
        if "addtime" in groups: mess = f'{current_date} {current_time} >> {message}'
        terminal_history.append(f"{mess}")

    logs.append({"log" : message, "groups" : groups, "time" : time})
    
    if 'log' in groups: # and not 'run' in groups:
        with open("logs.log",'a',encoding = 'utf-8') as f:
            nextline = '\n' if 'nextline' in groups else ''
            f.write(f"{nextline}{time} >> {message}\n")

    print(message)

def get_all_terminal_history():
    global terminal_history
    all_terminal_history = []
    for logline in logs:
        if "terminal" in logline["groups"]:
            terminal_log = logline["log"]
            if "addtime" in logline["groups"]: terminal_log = f'{logline["time"]} >> {logline["log"]}'
            all_terminal_history.append(f'{terminal_log}')
    return all_terminal_history

def get_terminal_history():
    global terminal_history
    t_history = terminal_history
    terminal_history = []
    return t_history

def unauthorized_request_log(req, autoreturn = True):
    logger(["terminal", "log", "addtime"], f'Registred unauthorized request: {req}')
    if autoreturn: return jsonify({"auth":False, 'msg':"Unauthorized request"})
