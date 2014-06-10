import webapp2
import json

from magtifun import Magtifun

class SmsHandler(webapp2.RequestHandler):

	sms = None # Magtifun object

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
			'action': action,
			'recipients': []}
		if self.sms.isLoggedIn():
			if (action == 'send'):
				self.sms.setMessage(self.request.get('message'))
				response['message'] = self.request.get('message')
				for number in self.request.get('to').split(','):
					self.sms.addRecipient(number)
				response['recipients'] = self.sms.recipients
				response['sent'] = self.sms.send()
				response['status'] = self.sms.msgStatus
			elif (action == 'test'):
				pass
			else:
				response['data'] = {
					'account_info': self.sms.getAccountInfo(),
					'contacts': self.sms.getContacts(),
					'credits': self.sms.getCredits(),
				}.get(action, 'undefined action')
		self.dumpJson(response)

	def index(self):
		self.dumpJson({
			'auth': self.sms.isLoggedIn(),
			'message': 'action'
		})

# let the magic happen
app = webapp2.WSGIApplication([
	webapp2.Route('/', handler=SmsHandler, handler_method='index'),
	webapp2.Route('/<action:\w+>', handler=SmsHandler, handler_method='main')
], debug = True)