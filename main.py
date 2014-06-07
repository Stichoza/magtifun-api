#!/usr/bin/env python

import webapp2
import json

import magtifun

class MainHandler(webapp2.RequestHandler):
	def get(self):
		obj = [14, {'as': [1,54,77]}]
		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(obj))

# let the magic happen
app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/send', MainHandler)
], debug=True)