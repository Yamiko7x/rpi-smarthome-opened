from flask import Blueprint, request, jsonify

import extensions.globals as g
import extensions.sessionlink as sl
import rpi.actions_system as ras
import rpi.rpi_factorys as rpif

from dbcontroller.dbtemplate import Actions
import dbcontroller.dbmanager as dbm

actions_api = Blueprint("actionapi", __name__)


def getWorkingActionsIDs(action_id=None):
    working_actions_id = []
    for key in ras.working_actions.keys(): working_actions_id.append(key)
    if action_id: return action_id in working_actions_id
    return working_actions_id


@actions_api.route("/getActionDictByID", methods=["POST"])
@sl.auth
def getAllActionsDict():
    uname = request.get_json()["user"]
    if not dbm.check_permissions(uname): return jsonify({'auth':True, 'status' : 'refusal', 'msg': 'Brak uprawnień'})

    action_id = request.get_json()["action_id"]
    return jsonify({'auth':True, 
                    'action_dict' : ras.actions_dict[action_id], 
                    'working' : getWorkingActionsIDs(action_id)})


@actions_api.route("/getAllActionsIDs", methods=["POST"])
@sl.auth
def getAllActionsIDs():
    """return json {auth: True/False, all_actions_ids: [action_id_1, action_id_2 ...]}"""
    uname = request.get_json()["user"]
    if not dbm.check_permissions(uname): return jsonify({'auth':True, 'status' : 'refusal', 'msg': 'Brak uprawnień'})

    return jsonify({'auth':True, 'all_actions_ids' : list(ras.actions_dict.keys())})


@actions_api.route("/getAllActionsDict", methods=["POST"])
@sl.auth
def getActionDictByID():
    return jsonify({'auth':True, 
                    'actions_dict' : ras.actions_dict, 
                    'working_actions_ids' : getWorkingActionsIDs(), 
                    'to_stop_actions': ras.stop_actions_list,
                    'vars_dict' : ras.vars_dict,
                    'fns_dict' : {'gpio_check' : {'template' : 'gpio_check(factory="local", gpio_nr=20)', 'return':'-1/0/1', 'import':'ras'},
                                  'get_var'    : {'template' : 'get_var(path="/myvar or /global/myvar", default=0)', 'return':'value if exist or default', 'import':'ras'},
                                  'getdatetime': {'template' : 'getdatetime(format="datetime or date or time or daynrtime or daytime or custom")', 'return': 'dd/mm/rrrr hh:mm:ss', 'import':'ras'},
                                  'getStorage' : {'template' : 'getStorage(name="mySaveValue")', 'return': 'value from DB if exist', 'import':'ras'},
                                  }})


@actions_api.route("/getAllActionsShorts", methods=["POST"])
@sl.auth
def getAllActionsShorts():
    uname = request.get_json()["user"]
    if not dbm.check_permissions(uname): return jsonify({'auth':True, 'status' : 'refusal', 'msg': 'Brak uprawnień'})

    shortDict = {}
    for key, action in ras.actions_dict.items():
        shortDict[key] = action['meta']
    return jsonify({'auth':True, 'actions_dict' : shortDict, 'working_actions_ids' : getWorkingActionsIDs()})


@actions_api.route("/getVars", methods=["POST"])
@sl.auth
def getVars():
    return jsonify({'auth':True, 'vars_dict' : ras.vars_dict})


@actions_api.route("/saveActionDict", methods=["POST"])
@sl.auth
def saveActionDict():
    uname = request.get_json()["user"]
    if not dbm.check_permissions(uname): return jsonify({'auth':True, 'status' : 'refusal', 'msg': 'Brak uprawnień'})

    action_id = request.get_json()["action_id"]
    action_dict = request.get_json()["action_dict"]
    msg = 'Action edited'

    action = None
    if not action_id == -1: action = g.db.session.query(Actions).filter_by(action_id=action_id).first()
    if action is None:
        msg = 'Added new action'
        action = Actions(action_id="", meta="", actions="")
        g.db.session.add(action)
        g.db.session.flush()
        action_db_id = action.id
        g.db.session.commit()
        action = Actions.query.get(action_db_id)

    action.action_id = str(action_dict['meta']['action_id'])
    action.meta = str(action_dict['meta'])
    action.actions = str(action_dict['actions'])
    g.db.session.commit()

    ras.add_action(action_dict, update=True)

    return jsonify({'auth':True, 'msg' : msg})


@actions_api.route("/rmAction", methods=["POST"])
@sl.auth
def rmAction():
    uname = request.get_json()["user"]
    if not dbm.check_permissions(uname): return jsonify({'auth':True, 'status' : 'refusal', 'msg': 'Brak uprawnień'})
    
    action_id = request.get_json()["action_id"]

    if action_id in ras.working_actions:
        return jsonify({'auth':True, 'msg' : 'Action in working!', 'type' : 'danger'})

    removed = True if Actions.query.filter(Actions.action_id == action_id).delete() == 1 else False
    g.db.session.commit()
    
    if action_id in ras.actions_dict and removed:
        ras.actions_dict.pop(action_id)

    return jsonify({'auth':True, 'msg' : 'Action removed.', 'type':'success'})


@actions_api.route("/getSimpleFnsDict", methods=["POST"])
@sl.auth
def getSimpleFnsDict():
    return jsonify({'auth':True, 'fns_dict' : ras.getSimpleFnsDict()})


@actions_api.route("/getFullFnsDict", methods=["POST"])
@sl.auth
def getFullFnsDict():
    return jsonify({'auth':True, 'fns_dict' : ras.fns_dict})
    

@actions_api.route("/getDevicesList", methods=["POST"])
@sl.auth
def getDevicesList():
    for alias, rpiDict in rpif.host_ip_list.items():
        if alias in rpif.factory_dict and g.tryip(rpiDict['ip']): 
            rpiDict['work'] = True
        else: rpiDict['work'] = False

    return jsonify({'auth':True, 'devices' : rpif.host_ip_list})

    
@actions_api.route("/addDevice", methods=["POST"])
@sl.auth
def addDevice():
    alias = request.get_json()["alias"]
    ip = request.get_json()["ip"]
    enable = request.get_json()["enable"]
    dbm.addDevice(ip, alias, enable)
    return jsonify({'auth':True, 'msg' : 'Device added'})


@actions_api.route("/rmDevice", methods=["POST"])
@sl.auth
def rmDevice():
    alias = request.get_json()["alias"]
    removed = dbm.rmDevice(alias)
    msg = "Device removed" if removed else "Removed error"
    return jsonify({'auth':True, 'msg' : msg})


@actions_api.route("/toggleDevice", methods=["POST"])
@sl.auth
def toggleDevice():
    alias  = request.get_json()["alias"]
    toggle = request.get_json()["toggle"]
    result = dbm.toggleDevice(alias, toggle)
    running = {}
    if toggle in [1, "1", True]: 
        running = rpif.prepare_factorys(alias=alias)
        ras.reload_actions()
    elif toggle in [0, "0", False]: running = ras.close_gpios(factory_alias=alias)
    return jsonify({'auth':True, 'type': result['type'],  'msg' : result['msg'], 'running': running})


@actions_api.route("/getFactoryList", methods=["POST"])
@sl.auth
def getFactoryList():
    return jsonify({'auth':True, 'msg' : 'Prepared factory list', 'factory_list': rpif.host_ip_list})