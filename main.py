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
		data['auth'] = True
		self.response.write(json.dumps(data))

	def main(self, action = None):
		self.createSmsObject()
		response = {
			'auth': self.sms.isLoggedIn(),
			'action': action}
		if self.sms.isLoggedIn():
			response['data'] = {
				'account_info': self.sms.getAccountInfo(),
				'credits': self.sms.getCredits(),
			}.get(action, 'undefined action')
		self.dumpJson(response)
		

# let the magic happen
app = webapp2.WSGIApplication([
	webapp2.Route('/<action:\w+>', handler=SmsHandler, handler_method='main')
], debug = True)