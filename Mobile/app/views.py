from flask import render_template, flash, redirect
from app import app
from flask import request,jsonify

import twilio.twiml
import json

from .ManageView import *
from .SmsHandler import *
from .RegisterView import *
# from .SmSView import *

base_url = "http://demo.engineerinme.com:5000"

@app.route('/', methods=['GET','POST'])
@app.route('/<opt>', methods=['GET','POST'])
@app.route('/<opt>/', methods=['GET','POST'])
def index(opt= -1):

	number = str( request.args.get('From'))
	number = number.replace("+","")
	if opt != -1 :
		other_stri = "<Say voice=\"woman\"> authentication failed ... taking to main menu</Say>"
	else:
		other_stri = ""
	stri = '<?xml version="1.0" encoding="UTF-8"?><Response>'+other_stri+'\
<Gather action="http://demo.engineerinme.com:5000/manageMenu/?number='+str(number)+'/" numDigits="1">\
<Say voice="woman">Hello and welcome to the Gramin bank Phone Menu</Say>\
<Say voice="woman">To Manage your account, press 1</Say>\
<Say voice="woman">For registration, press 2 </Say>\
<Say voice="woman">To speak to a customer representative, press 9</Say>\
<Say voice="woman">To Exit, press 3</Say>\
</Gather>\
</Response>'

	return stri 

@app.route('/manageMenu', methods=['GET','POST'])
@app.route('/manageMenu/', methods=['GET','POST'])
def manageMenu():
	try:
		option = int(request.form['Digits'])
	except Exception as e:
		try:
			option = int(request.args.get('Digits'))
		except:
			return '<?xml version="1.0" encoding="UTF-8"?><Response><Say>blast</Say></Response>'
	if option == 2:
		#Register Account
		number = request.args.get('number')
		if number == "client:Anonymous":
			number = "twilio"
		url_next = base_url + "/register_get_id/"+str(option)+"/"+str(number) 
		stri = '<?xml version="1.0" encoding="UTF-8"?>\
<Response><Say voice="woman">Thank you for initiating the registration.</Say>\
<Gather action="'+str(url_next)+'" numDigits="18"><Say voice="woman">Please enter your Chinese ID, 18 digits.</Say>\
</Gather></Response>'
		print stri
		return stri

	if option == 1:
		#Manage_account 
		return redirect("http://demo.engineerinme.com:5000/manage_login_init/", code=302)

	if option == 3 :
		#Exit
		return redirect("http://demo.engineerinme.com:5000/exit/", code=302)

	if option == 9 :
		#Speak_to_customer
		return '<?xml version="1.0" encoding="UTF-8"?><Response>\
<Say voice="woman">Please wait, you will be put in relation with someone</Say>\
<Dial callerId="+85258087544"><Number>+85255086023</Number></Dial>\
<Say voice="woman">The call failed or the remote party hung up. Goodbye.</Say>\
</Response>'
	return redirect("http://demo.engineerinme.com:5000/", code=302)

@app.route('/exit', methods=['GET','POST'])
@app.route('/exit/', methods=['GET','POST'])
def exit():
	return '<?xml version="1.0" encoding="UTF-8"?>\
<Response><Say voice="woman">Thanks for Dialing to gramin Bank. Call will now terminate.</Say><Pause length="1"/><Hangup/></Response>'



