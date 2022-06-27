import extensions.globals as g
from datetime import datetime
from flask import jsonify


class User(g.db.Model):
    id = g.db.Column(g.db.Integer, primary_key=True)
    uname = g.db.Column(g.db.String(40), unique=True, nullable=False)
    fname = g.db.Column(g.db.String(40))
    lname = g.db.Column(g.db.String(80))
    email = g.db.Column(g.db.String(120))
    password = g.db.Column(g.db.String(255), nullable=False)
    account_type = g.db.Column(g.db.String(10), nullable=False)
    available_menu = g.db.Column(g.db.String(), nullable=False)
    available_widgets = g.db.Column(g.db.String(), nullable=False)
    edit_widgets = g.db.Column(g.db.Integer, nullable=False)
    edit_actions = g.db.Column(g.db.Integer, nullable=False)
    active = g.db.Column(g.db.Boolean)
    created_date = g.db.Column(g.db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        resp = {'account_type': self.account_type,
                'uname': self.uname,
                'fname': self.fname,
                'lname': self.lname,
                'email': self.email,
                'active': self.active,
                'available_menu': self.available_menu}
        return f'{resp}'


class Widget(g.db.Model):
    id = g.db.Column(g.db.Integer, primary_key=True)
    meta = g.db.Column(g.db.String(), nullable=False)

    def __repr__(self):
        resp = {'id': self.id,
                'meta': self.meta}
        return f'{resp}'


class Actions(g.db.Model):
    id = g.db.Column(g.db.Integer, primary_key=True)
    action_id = g.db.Column(g.db.String(), nullable=False)
    meta = g.db.Column(g.db.String(), nullable=False)
    actions = g.db.Column(g.db.String(), nullable=False)

    def __repr__(self):
        resp = {'id': self.id,
                'meta': self.meta,
                'actions': self.actions}
        return f'{resp}'


class Settings(g.db.Model):
    id = g.db.Column(g.db.Integer, primary_key=True)
    setting = g.db.Column(g.db.String(100), nullable=False)
    value = g.db.Column(g.db.String(), nullable=False)
    uname = g.db.Column(g.db.String(), nullable=False)

    def __repr__(self):
        resp = {'id': self.id,
                'setting': self.setting,
                'value': self.value,
                'uname': self.uname}
        return f'{resp}'


class Devices(g.db.Model):
    id = g.db.Column(g.db.Integer, primary_key=True)
    alias = g.db.Column(g.db.String(100), nullable=False)
    ip = g.db.Column(g.db.String(20), nullable=False)
    enable = g.db.Column(g.db.Integer(), nullable=False)

    def __repr__(self):
        resp = {'id': self.id,
                'alias': self.alias,
                'ip': self.ip,
                'enable': self.enable}
        return f'{resp}'


class Storage(g.db.Model):
    id = g.db.Column(g.db.Integer, primary_key=True)
    name = g.db.Column(g.db.String(100), nullable=False)
    value = g.db.Column(g.db.String(), nullable=False)

    def __repr__(self):
        resp = {'id': self.id,
                'name': self.name,
                'value': self.value}
        return f'{resp}'