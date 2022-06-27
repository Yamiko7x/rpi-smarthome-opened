"""Flask server dla obsługi Smarthome"""
from flask import Flask, redirect
from dbcontroller.dbm_api import dbm_api
from webgui.pilot_api import pilot_api
from webgui.actions_api import actions_api
from flask_cors import CORS

import extensions.globals as g
import webgui.smart_home_api as wsha
import dbcontroller.dbmanager as dbm
import extensions.logger as log

# pre konfiguracja
g.loadSettingsFile()
dbm.loadUsersSalts()

# Konfiguracje
app = Flask(__name__)
app.secret_key = g.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = g.dbconnector
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
g.db.init_app(app)
CORS(app)


# Blueprinty
app.register_blueprint(dbm_api, url_prefix="/dbm_api")
app.register_blueprint(pilot_api, url_prefix="/pilot_api")
app.register_blueprint(wsha.smart_home_api, url_prefix="/smart_home_api")
app.register_blueprint(actions_api, url_prefix="/actions_api")


# Index
@app.route("/")
def index():
    return redirect("")


# App start
if __name__ == "__main__":
    g.app = app

    with app.app_context():
        log.logger(['terminal', 'log', 'nextline'], f'[ + ] Startup app{" with auth debug mode" if g.auth_debug else ""}')
        dbm.check_db_file(app)
        dbm.check_admin_exist()
        wsha.aq_panel()


    app.run(debug=True, host='0.0.0.0', use_reloader=False)