from flask import render_template, flash, redirect
from app import app
from flask import request,jsonify
import datetime
import twilio.twiml
import json
from models import *
from .sound import *
import requests
import wget

import urllib2
from twilio.rest import TwilioRestClient


account_sid = "ACffa9e11bbcb635efa44d8af78e02db5a"
auth_token = "9ca02930711294b79a1a6cf2c0efb814"

client = TwilioRestClient(account_sid, auth_token)

base_url = "http://demo.engineerinme.com:5000"

@app.route("/manage_login_init", methods=['GET','POST'])
@app.route("/manage_login_init/", methods=['GET','POST'])
def manage_login_init():
	url_next = base_url + "/manage_authenticate_pin/"

	Cid = '<?xml version="1.0" encoding="UTF-8"?><Response>\
<Gather action="'+url_next+'" numDigits="18">\
<Say voice="woman">To authenticate yourself, please first enter your Chinese ID, 18 digits</Say>\
</Gather></Response>'
	print Cid
	return Cid


@app.route("/manage_authenticate_pin", methods=['GET','POST'])
@app.route("/manage_authenticate_pin/", methods=['GET','POST'])
def manage_authenticate_pin():
	Cid = str(request.form['Digits'])
	url_next = base_url + "/manage_authenticate/" + Cid +"/"

	pin = '<?xml version="1.0" encoding="UTF-8"?><Response>\
<Gather action="'+url_next+'" numDigits="5">\
<Say voice="woman">To authenticate yourself, please enter your 5 digits pin number</Say>\
</Gather></Response>'
	return pin

@app.route("/manage_authenticate/<Cid>", methods=['GET','POST'])
@app.route("/manage_authenticate/<Cid>/", methods=['GET','POST'])
def manage_authenticate(Cid = "0"):
	Cid = str(Cid)
	pin = str(request.form['Digits'])

	url_next = base_url +"/2/"
	customer = Customer.query.filter(Customer.chineseID == Cid).first()

	if (customer == None) or (str(customer.pin) != str(pin)):
	 	return redirect(url_next, code=302)

	url_next = base_url + "/manage_authenticated/"+str(Cid)+"/"

	return '<?xml version="1.0" encoding="UTF-8"?><Response>\
<Gather action="'+url_next+'" numDigits="1">\
<Say voice="woman">You have been authenticated please press 0 to continue </Say>\
</Gather></Response>'

@app.route("/manage_authenticated/<ChineseID>", methods=['GET', 'POST'])
@app.route("/manage_authenticated/<ChineseID>/", methods=['GET', 'POST'])
def manage_authenticated(ChineseID = 0):
	url_next =  base_url + "/manage_authenticated/" + str(ChineseID) + "/menu/"
	return '<?xml version="1.0" encoding="UTF-8"?><Response>\
<Gather action="'+ url_next+'" numDigits="1">\
<Say voice="woman">To request a loan or withdraw money, press 1 </Say>\
<Say voice="woman">To manage your account, press 2 </Say>\
</Gather></Response>'

@app.route("/manage_authenticated/<ChineseID>/menu", methods=['GET', 'POST'])
@app.route("/manage_authenticated/<ChineseID>/menu/", methods=['GET', 'POST'])
def manage_authenticated_menu(ChineseID = 0):
	option = int(request.form['Digits'])
	url_next = base_url + "/manage_authenticated/" + str(ChineseID) + "/"
	if (option == 1):
		return '<?xml version="1.0" encoding="UTF-8"?>\
<Response>\
<Gather action="'+url_next+"loan/"+'" numDigits="10" finishOnKey="*">\
<Say voice="woman">Please enter the amount you would like to withdraw and press the star key to finish</Say>\
</Gather>\
</Response>'
	if (option == 2):
		return '<?xml version="1.0" encoding="UTF-8"?>\
<Response>\
<Gather action="'+url_next+"manage_account/"+'" numDigits="1">\
<Say voice="woman">If you want to change your phone number, press 1</Say>\
<Say voice="woman">If you want to change your location, press 2</Say>\
<Say voice="woman">If you want to change your pin code, press 3</Say>\
</Gather>\
</Response>'
	return '<?xml version="1.0" encoding="UTF-8"?>\
	<Response><Say voice="woman">Thanks for Dialing to gramin Bank. Call will now terminate.</Say><Pause length="1"/><Hangup/></Response>'

@app.route("/manage_authenticated/<ChineseID>/loan", methods=['GET', 'POST'])
@app.route("/manage_authenticated/<ChineseID>/loan/", methods=['GET', 'POST'])
def manage_loan(ChineseID = 0):
	amount = request.form['Digits']
	customer = Customer.query.filter(Customer.chineseID == ChineseID).first()
	url_next = base_url + "/manage_authenticated/" + str(ChineseID) 	
	if (customer.accountAmount < amount):
		return redirect(url_next + "/loan_request/" + amount + "/")
	return redirect(url_next + "/withdraw_request/"  + amount + "/", code=302)

@app.route("/manage_authenticated/<ChineseID>/loan_request/<amount>", methods=['GET', 'POST'])
@app.route("/manage_authenticated/<ChineseID>/loan_request/<amount>/", methods=['GET', 'POST'])
def loan_request(ChineseID = 0, amount = 0):
	exit_url = base_url +"/exit/"
	next_url = "http://demo.engineerinme.com:5000/verify_audio/"
	try:
		l = Loans()
		l.customer_id = str(ChineseID)
		l.approval = "pending"
		l.amount = int(amount)
		l.date = datetime.datetime.utcnow()
		db.session.add(l)
		db.session.commit()
		loan_id = l.sno
		next_url = next_url+str(loan_id) +"/"
	except Exception as e:
		print e
		next_url = base_url
	stri = '<?xml version="1.0" encoding="UTF-8"?>\
<Response>\
<Say voice="woman">Please clearly state your name and adress after the beep for vocal authentication then press the star key to validate.</Say>\
<Record transcribe="true" transcribeCallback="'+next_url+'" action="'+exit_url+'" maxLength="10" finishOnKey="*" /></Response>'
	print stri
	return stri

@app.route("/manage_authenticated/<ChineseID>/withdraw_request/<amount>", methods=['GET', 'POST'])
@app.route("/manage_authenticated/<ChineseID>/withdraw_request/<amount>/", methods=['GET', 'POST'])
def withdraw_request(ChineseID = 0, amount = 0):
	
	exit_url = base_url +"/exit/"
	next_url = "http://demo.engineerinme.com:5000/verify_audio/"
	try:
		l = Loans()
		l.customer_id = str(ChineseID)
		l.approval = "pending"
		l.amount = int(amount)
		l.date = datetime.datetime.utcnow()
		db.session.add(l)
		db.session.commit()
		loan_id = l.sno
		next_url = next_url+str(loan_id) +"/"
	except Exception as e:
		print e
		url_next = base_url
	stri = '<?xml version="1.0" encoding="UTF-8"?>\
<Response>\
<Say voice="woman">Please clearly state your name and adress after the beep for further vocal authentication then press the star key to validate.</Say>\
<Record transcribe="true" transcribeCallback="'+next_url+'" action="'+exit_url+'" maxLength="10" finishOnKey="*" /></Response>'
	# print stri
	return stri

@app.route("/manage_authenticated/<ChineseID>/manage_account", methods=['GET', 'POST'])
@app.route("/manage_authenticated/<ChineseID>/manage_account/", methods=['GET', 'POST'])
def manage_account(ChineseID = 0):
	option = int(request.form['Digits'])
	url_next = base_url + "/exit/"
	if (option == 1):
		return '<?xml version="1.0" encoding="UTF-8"?>\
<Response>\
<Gather action="'+url_next+'" numDigits="11">\
<Say voice="woman">Please enter your new phone number</Say>\
</Gather>\
</Response>'
	if (option == 2):
		return '<?xml version="1.0" encoding="UTF-8"?>\
<Response>\
<Gather action="'+url_next+'" numDigits="6">\
<Say voice="woman">Please enter your new location</Say>\
</Gather>\
</Response>'
	if (option == 3):
		return '<?xml version="1.0" encoding="UTF-8"?>\
<Response>\
<Gather action="'+url_next+'" numDigits="5">\
<Say voice="woman">Please enter your new 5 digits pin number</Say>\
</Gather>\
</Response>'
	return '<?xml version="1.0" encoding="UTF-8"?>\
	<Response><Say voice="woman">Thanks for Dialing to gramin Bank. Call will now terminate.</Say><Pause length="1"/><Hangup/></Response>'

	return redirect(url_next, code=302)

@app.route("/verify_audio/<loanID>", methods=['GET', 'POST'])
@app.route("/verify_audio/<loanID>/", methods=['GET', 'POST'])
def verify_audio(loanID= 0 ):
	try:
		L = Loans.query.filter_by(sno = loanID).first()
		C = Customer.query.filter_by(chineseID = L.customer_id).all()[0]
	
		print C.phoneNumber

		url_2 = str(C.voiceURL)
		url_1 = str(request.form['RecordingUrl'])


		print url_2 , url_1
		response = urllib2.urlopen(url_2)
		localFile = open('1.waw', 'w')
		localFile.write(response.read())
		localFile.close()

		response = urllib2.urlopen(url_2)
		localFile = open('2.waw', 'w')
		localFile.write(response.read())
		localFile.close()

		seqx = master('2.waw')
		seqy = master('1.waw')

		cost = dynamicTimeWarp(seqx, seqy)
		match = match_test(cost)
		if match :
			L.approval = "approved"
			db.session.add(L)
			db.session.commit()
			message = client.messages.create(to=C.phoneNumber, from_="85264522712", body="We have sucessfully delivered your Request , you have been authenticated.")
			return "Done"
		message = client.messages.create(to=C.phoneNumber, from_="85264522712", body="Someone tried to access your account. The attemp was not successful.")
		return "Doomed"
	except Exception as e:
		print e
		message = client.messages.create(to=C.phoneNumber, from_="85264522712", body="Someone tried to access your account. The attemp was not successful.")
		return "Doomed"