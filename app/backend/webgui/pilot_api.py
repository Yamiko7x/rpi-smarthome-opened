from flask import Blueprint, request, jsonify
import os
from datetime import datetime
import pprint

import extensions.globals as g
import extensions.sessionlink as sl
import extensions.logger as log
import webgui.smart_home_api as shome
import rpi.actions_system as ras
import dbcontroller.dbmanager as dbm

from dbcontroller.dbtemplate import Widget

pilot_api = Blueprint("pilotapi", __name__)


widgetsDict = { 999: {"id": "999",
                    "type": "display_info",
                    "name": "Watch some",
                    "watch_type": "vars",
                    "watch_path": "tl1 some",
                    "state": "N/A",
                    "prefix": "Some: ",
                    "sufix": "",
                    "active": False},
                1000:  {"id": "1000",
                    "type": "two_state_switch",
                    "name": "Auto switch on/off",
                    "state": "N/A",
                    "watch_type": "work",
                    "watch_path": "as21",
                    "on_action": "start onas",
                    "off_action": "start ofas",
                    "active": False},}

widgetsDictRefreshedWithDB = False

def updateWidgetsDict(clear=True, refresh=False):
    global widgetsDict
    global widgetsDictRefreshedWithDB
    if refresh or not widgetsDictRefreshedWithDB:
        if clear: widgetsDict = {}
        dbWidgets = Widget.query.all()
        for widget in dbWidgets:
            widgetsDict[widget.id] = eval(widget.meta)
        widgetsDictRefreshedWithDB = True
        log.logger(['terminal', 'log', 'inf'], "updateWidgetsDict: Odświeżono dane widgetów na podstawie DB.")

def updateWidgetsState():
    global widgetsDict
    for widget_id, widget_meta in widgetsDict.items():
        if widget_meta['active']:
            if widget_meta['watch_type'] == 'vars':
                widgetsDict[widget_id]['state'] = shome.api_get_var(path=widget_meta['watch_path'])

            elif widget_meta['watch_type'] == 'gpio':
                widgetsDict[widget_id]['state'] = shome.api_check_gpio_state(path=widget_meta['watch_path'])

            elif widget_meta['watch_type'] == 'work':
                widgetsDict[widget_id]['state'] = shome.api_check_action_state(widget_meta['watch_path'])

            elif widget_meta['watch_type'] == 'custom' and widget_meta['watch_path']:
                try:
                    widgetsDict[widget_id]['state'] = eval(widget_meta['watch_path'])
                except:
                    widgetsDict[widget_id]['state'] = widget_meta['watch_path']

            if 'prefix' in widget_meta:
                widget_meta['setprefix'] = ras.translate_str(someStr=widget_meta['prefix'])
                
            if 'sufix' in widget_meta:
                widget_meta['setsufix'] = ras.translate_str(someStr=widget_meta['sufix'])

            if 'name' in widget_meta:
                widget_meta['setname'] = ras.translate_str(someStr=widget_meta['name'])

@pilot_api.route("/load_widgets_meta", methods=["POST"])
@sl.auth
def load_widgets_meta():
    """Load components metadata and send to web"""
    global widgetsDict
    uname = request.get_json()["user"]

    updateWidgetsDict()
    updateWidgetsState()
    #pprint.PrettyPrinter().pprint(widgetsDict)

    ids_widgets = dbm.getUserWidgets(uname)
    canEdit = 0
    if ids_widgets[-1] == 1: canEdit = 1
    ids_widgets.pop()
    tosend = {}

    if ids_widgets[0] == 'all': tosend = widgetsDict
    else:
        for k in ids_widgets:
            try: tosend[k] = widgetsDict[int(k)]
            except: pass

    return jsonify({"auth": f'ok', "widgets": tosend, 'can_edit':canEdit})

def lastID():
    global widgetsDict
    maxKey = 0
    for key, val in widgetsDict.items():
        if maxKey < key: maxKey = key
    return maxKey

@pilot_api.route("/editWidget", methods=["POST"])
@sl.auth
def editWidget():
    """Edit existing widget or add new"""
    global widgetsDict
    editedWidgetDict = request.get_json()["widgetDict"]
    catchedId = int(editedWidgetDict['id'])
    
    if catchedId > -1:
        widget = Widget.query.get(catchedId)
        widget.meta = str(editedWidgetDict)
        g.db.session.commit()
        widgetsDict[catchedId] = editedWidgetDict
    elif catchedId == -1:
        widget = Widget(meta="")
        g.db.session.add(widget)
        g.db.session.flush()
        newID = widget.id
        editedWidgetDict["id"] = f'{newID}'
        widget = Widget.query.get(newID)
        widget.meta = str(editedWidgetDict)
        g.db.session.commit()
        widgetsDict[newID] = editedWidgetDict
    return jsonify({"auth": f'ok', "msg": "Widget updated"})
    

@pilot_api.route("/rmWidget", methods=["POST"])
@sl.auth
def rmWidget():
    """Remove existing widget"""
    global widgetsDict
    widgetID = int(request.get_json()["widgetID"])

    if widgetsDict[widgetID]:
        widget = Widget.query.filter(Widget.id==int(widgetID)).first()
        g.db.session.delete(widget)
        g.db.session.commit()
        widgetsDict.pop(widgetID)
    return jsonify({"auth": f'ok', "msg": "Widget deleted"})

    
@pilot_api.route("/widgetBackupsList", methods=["POST"])
@sl.auth
def widgetBackupsList():
    """"""
    path = f'{g.dbdir}'
    dir_list = os.listdir(path)
    backups = []
    for pos in dir_list:
        name = pos.split('_')
        if len(name) > 2 and name[0] == "backup" and name[1]=="widgets":
            backups.append(pos)

    return jsonify({"auth": f'ok', "backups_list": backups})
    

@pilot_api.route("/createWidgetsBackup", methods=["POST"])
@sl.auth
def createWidgetsBackup():
    """"""
    try:
        path = f'{g.dbdir}'
        allWidgets = Widget.query.all()
        print(allWidgets)
        now = datetime.now()
        dt = now.strftime("%d-%m-%Y_%H-%M-%S")
        f = open(f"{path}/backup_widgets_{dt}.bak", "w")
        f.write(f'{allWidgets}')
        f.close()
    except:
        return jsonify({"auth": f'ok', "msg": "Backup faild"})
    return jsonify({"auth": f'ok', "msg": "Backup created"})


@pilot_api.route("/restoreWidgetsBackup", methods=["POST"])
@sl.auth
def restoreWidgetsBackup():
    """"""
    backupName = request.get_json()["backup_name"]
    path = f'{g.dbdir}'
    loadWidgetBackup = open(f"{path}/{backupName}", "r")
    for widgetTmp in eval(loadWidgetBackup.read()):
        widget = Widget.query.get(widgetTmp['id'])
        if widget is None:
            widget = Widget(id=widgetTmp['id'], meta=widgetTmp['meta'])
            g.db.session.add(widget)
        else:
            widget.meta = widgetTmp['meta']
    
    g.db.session.commit()
    updateWidgetsDict(clear=True, refresh=True)
    
    return jsonify({"auth": f'ok', "msg": "Backup restored"})