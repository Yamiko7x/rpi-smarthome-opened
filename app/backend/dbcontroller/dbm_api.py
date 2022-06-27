from flask import Blueprint, request, jsonify
from dbcontroller.dbtemplate import User
import os

import extensions.globals as g
import extensions.sessionlink as sl
import dbcontroller.dbmanager as dbm

dbm_api = Blueprint("dbm_api", __name__)


def valid_empty(params, params_name=None):
    for idx, p in enumerate(params):
        if p == "" or p is None:
            if params_name is None:
                return False
            else:
                return [False, f"Empty valu on {params_name[idx]}"]
    return True


@dbm_api.route("/adduser", methods=["POST"])
@sl.auth
def adduser():
    """Recreate database
       Create new user
    """
    
    # TODO: valid acctype
    params_name = ["r_acctype", "r_uname", "r_fname", "r_lname", "r_email", "r_password"]
    newUserDict = request.get_json()
    newuser = [ newUserDict["r_acctype"],
                newUserDict["r_uname"],
                newUserDict["r_fname"],
                newUserDict["r_lname"],
                newUserDict["r_email"],
                newUserDict["r_password"] ]

    print(f'NewUser: {newuser}')
    if valid_empty(newuser, params_name) is not True: return jsonify({"auth":True, 'msg': f'Datas are not complete {newuser}.'})

    if not dbm.userexist(newuser[1]):
        dbm.adduser(newuser)
        return jsonify({"auth":True, 'msg': f'Added new user.'})

    return jsonify({"auth":True, 'msg': f'User name is unavailable.'})


@dbm_api.route("/userslist", methods=["POST"])
@sl.auth
def listusers():
    """Recreate database
       Return info about users
    """
    users = []
    for user in User.query.all(): users.append(eval(str(user)))
    return jsonify({"auth":True, 'msg': f'Completed users data.', 'users':users})
    

@dbm_api.route("/deluser", methods=["POST"])
@sl.auth
def deluser():
    """Delete user by uname"""
    uname = request.get_json()["uname"]
    if not uname or not dbm.userexist(uname): return jsonify({"auth":True, 'msg':'User not found.'})
    
    rmuser = dbm.remove_user(uname)
    return jsonify({"auth":True, 'msg': f'User {uname} deleted.'})


@dbm_api.route("/blockuser", methods=["POST"])
@sl.auth
def blockuser():
    """Delete user by uname"""
    uname = request.get_json()["uname"]
    if not uname or not dbm.userexist(uname): return jsonify({"auth":True, 'msg':'User not found.'})
    
    user = User.query.filter_by(uname=uname).first()
    user.active = not user.active
    g.db.session.commit()
    active = 'active' if user.active else 'unactive'
    return jsonify({"auth":True, 'msg': f'User {uname} is {active}.'})


@dbm_api.route("/loginuser", methods=["POST"])
def loginuser():
    """Login user"""

    login_data = [request.get_json()["uname"], request.get_json()["password"]]
    if valid_empty(login_data) is not True: 
        return jsonify({"auth":False, 'msg':'Wrong login or password.'})

    user = dbm.tryPassword(login_data[0], login_data[1])
    if user and user.active == 1:
        dbm.loadSettings(user.uname)
        return jsonify({"auth":True, 
                        "token": sl.create_sessionlink(user.uname),
                        "uname": user.uname,
                        "menu" : user.available_menu.split(';'),
                        "account_type": user.account_type,
                        "edit_widgets": user.edit_widgets,
                        "edit_actions": user.edit_actions,
                        "refresh_widget_delay" : g.refresh_widget_delay,
                        })
    elif user and not user.active == 1:
        return jsonify({"auth":False, "msg": "You account is blocked."})

    return jsonify({"auth":False, 'msg':'Wrong login or password.'})


@dbm_api.route("/logout", methods=["POST"])
@sl.auth
def logout():
    """Logout user by removing sessionlink"""
    if request.method == "POST":
        uname = request.get_json()["user"]
        if uname in sl.tokensDict: 
            sl.rm_sessionlink(uname)
            return jsonify({"auth":True, 'msg':'Logout success'})
    return jsonify({"auth":True, 'msg':'User not found'})


@dbm_api.route("/isloggedin", methods=["POST"])
@sl.auth
def isloggedin():
    """Return if user is logged in"""
    return jsonify({"auth":True, 'type':'success', 'msg':'user is logged in'})


@dbm_api.route("/changePassword", methods=["POST"])
@sl.auth
def changePassword():
    """Check if user is loggedin"""
    uname = request.get_json()["uname"]
    passwd = request.get_json()["passwd"]

    dbm.newUserPassword(uname, passwd)

    return jsonify({"auth":True, 'msg':'Password changed'})


@dbm_api.route("/saveSetting", methods=["POST"])
@sl.auth
def saveSetting():
    """Save setting in DB"""
    uname = request.get_json()["user"]
    setting = request.get_json()["setting"]
    value = request.get_json()["value"]

    dbm.saveSettingInDB(uname, setting, value)

    return jsonify({"auth":True, 'msg':'Saved', 'type':'success'})
