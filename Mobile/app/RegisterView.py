from flask import render_template, flash, redirect
from app import app
from flask import request,jsonify
from .models import *
import twilio.twiml
import json
import urllib2

base_url = "http://demo.engineerinme.com:5000"

@app.route('/register_get_voice_transcribe/<option>/<number>/<ChineseID>/<pin>', methods=['GET','POST'])
@app.route('/register_get_voice_transcribe/<option>/<number>/<ChineseID>/<pin>/', methods=['GET','POST'])
def register_get_voice_transcribe(option =0, number = 0, ChineseID = 0, pin = 0):
	option = int(option)
	Chinese_id = str(ChineseID)
	pin = str(pin)
	status = request.form['TranscriptionStatus']
	TranscriptionText = "unable to transcribe"
	if status != "completed" : 
		RecordingUrl = request.form['RecordingUrl']
	else:
		RecordingUrl = request.form['RecordingUrl']
		TranscriptionText = request.form['TranscriptionText']

	response = urllib2.urlopen(RecordingUrl)
	localFile = open('audio/'+str(Chinese_id)+".mp3", 'w')
	localFile.write(response.read())
	localFile.close()

	c = Customer()
	c.chineseID = Chinese_id
	c.pin = pin
	c.phoneNumber = number
	c.location = "Doomed"
	c.maxThreshold =1000
	c.voiceURL = "http://demo.engineerinme.com/Mobile-IVRS/Mobile/audio/"+str(Chinese_id)+".mp3"
	db.session.add(c)
	db.session.commit()

	print "\t\t\t\t",option , Chinese_id , pin , RecordingUrl , TranscriptionText, number,"\n"
	return "Success!!"

@app.route('/register_get_pin/<option>/<number>/<ChineseID>', methods=['GET','POST'])
@app.route('/register_get_pin/<option>/<number>/<ChineseID>/', methods=['GET','POST'])
def register_get_pin(option = 0 , number = 0,ChineseID = 0 ):
	option = int(option)
	Chinese_id = str(ChineseID)
	pin = str(request.form['Digits'])
	end_url = base_url +"/exit/"
	transcribed_called = base_url +"/register_get_voice_transcribe/"+str(option) +"/"+str(number)+"/"+str(Chinese_id)+"/"+str(pin) +"/"  
	stri = '<?xml version="1.0" encoding="UTF-8"?><Response>\
<Say voice="woman">Please clearly state your name and adress after the beep for further vocal authentication then press the star key to terminate.</Say>\
<Record transcribe="true" transcribeCallback="'+transcribed_called+'" action="'+end_url+'" maxLength="10" finishOnKey="*"/></Response>'
	return stri

@app.route('/register_get_id/<option>/<number>', methods=['GET','POST'])
@app.route('/register_get_id/<option>/<number>/', methods=['GET','POST'])
def register_get_id(option = 0 , number = 0 ):
	Chinese_id = request.form['Digits']
	url_next = base_url + "/register_get_pin/"+str(option) +"/"+str(number)+"/" + str(Chinese_id)+"/"
	print number 
	stri='<?xml version="1.0" encoding="UTF-8"?>\
<Response>\
<Gather action="'+url_next+'" numDigits="5">\
<Say voice="woman">Please enter a 5 digit pin .</Say>\
</Gather>\
</Response>'
	return stri