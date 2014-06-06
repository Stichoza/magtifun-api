#!/usr/bin/env python

import webapp2
import json

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(json.dumps([14, {'as': [1,54,77]}]))

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
