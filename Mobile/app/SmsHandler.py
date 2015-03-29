#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect
from app import app
from flask import request,jsonify
from .models import *
import twilio.twiml
import json
from models import *
import datetime

value_key ={
    u'123123' : 500,
    u'123124' : 5000,
    u'123125' : 1000,
    u'123126' : 100,
    u'123127' : 10

}
@app.route("/deliver", methods=['GET','POST'])
@app.route("/deliver/", methods=['GET','POST'])
def delivered_sms():
    return "Done"

@app.route("/incoming", methods=['GET','POST'])
@app.route("/incoming/", methods=['GET','POST'])
def receive_sms():
    body =  request.form['Body']
    number  = request.form['From']

    ChineseId , key = body.split("**")
    T = Transaction()
    T.customer_id = ChineseId
    try:
        T.amount = value_key[key]
    except:
        T.amount = 0
    amount = T.amount
    T.date = datetime.datetime.utcnow()
    T.approval = "approved"
    T.type_of_trans = "deposit"
    db.session.add(T)
    db.session.commit()
    return '<?xml version="1.0" encoding="UTF-8"?><Response>\
<Message>\
<Body>Thanks your deposit request has been recorded :'+str(ChineseId)+', Amount '+str(amount)+'</Body>\
</Message>\
</Response>'