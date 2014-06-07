#!/usr/bin/env python

import webapp2
import json

from magtifun import Magtifun

class SmsHandler(webapp2.RequestHandler):

	sms = None

	def createSmsObject(self):
		username = self.request.get('username')
		password = self.request.get('password')
		self.sms = Magtifun(username, password)

	def dumpJson(self, data):
		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(data))

	def index(self):
		self.createSmsObject()
		self.dumpJson(self.sms.getAccountInfo())

	def send(self):
		self.createSmsObject()
		self.dumpJson(self.sms.getCredits())
		

# let the magic happen
app = webapp2.WSGIApplication([

	webapp2.Route('/',		handler = SmsHandler, handler_method='index',	schemes = ['https']),
	webapp2.Route('/send',	handler = SmsHandler, handler_method='send',	schemes = ['https'])

], debug = True)