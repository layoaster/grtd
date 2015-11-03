#!/usr/bin/env python
#
from google.appengine.ext import ndb

import webapp2
import json

# Datastore Models

class Grtd(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    ldap = ndb.StringProperty(indexed=True)
    last_code = ndb.StringProperty(indexed=False)
    timestamp = ndb.DateTimeProperty(indexed=False)
    codes = ndb.JsonProperty(indexed=False)

#HTTP handlers

class AgentStats(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

    def post(self):
    	agent = json.loads(self.request.body)
    	# Writing to Datastore
    	
        self.response.headers['Content-Type'] = "text/plain"
        self.response.out.write(self.request.body)

app = webapp2.WSGIApplication([
    ('/update', AgentStats)
], debug=False)
