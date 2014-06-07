#!/usr/bin/env python

import webapp2
import json

import magtifun

class SmsHandler(webapp2.RequestHandler):

	sms = None

	def get(self):
		self.sms = Magtifun()

		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(obj))

# let the magic happen
app = webapp2.WSGIApplication([

	webapp2.Route('/',		handler = 'handlers.SmsHandler:index',	schemes = ['https']),
	webapp2.Route('/send',	handler = 'handlers.SmsHandler:send',	schemes = ['https'])

], debug = True)