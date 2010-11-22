import cgi
import urllib

from django.utils import simplejson 
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError 
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class PSHBPingHandler(webapp.RequestHandler):
  def handlePing(self, method):
    qs = self.request.query_string
    parsedQs = cgi.parse_qs(qs)
    
    if parsedQs.has_key('hub') and parsedQs.has_key('topic'):
      hubUrl = parsedQs['hub'][0]
      topicUrls = parsedQs['topic']
      pingBody = urllib.urlencode( { "hub.mode" : "publish", "hub.url" : topicUrls}, True )
      pingHeaders = { "Content-Type" : "application/x-www-form-urlencoded" }
      
      pingResult = urlfetch.fetch(hubUrl, payload=pingBody, headers=pingHeaders, method=urlfetch.POST, deadline=10)
      
      if method == "POST":
        self.response.set_status(pingResult.status_code)
        for header in pingResult.headers.keys():
          self.response.headers[header] = pingResult.headers[header]
        self.response.out.write(pingResult.content)
      else:
        self.response.set_status(200)
        self.response.headers["Content-Type"] = "text/plain"
        self.response.out.write(str(pingResult.status_code) + "\n")
        for header in pingResult.headers.keys():
          self.response.out.write(header + ": " + pingResult.headers[header] + "\n")
        self.response.out.write(pingResult.content)
      return
    else:
      self.response.set_status(400)
      self.response.out.write("Request must include hub and topic url query string parameters")
      return 
  
  def get(self):
    self.handlePing("GET")

  def post(self):
    self.handlePing("POST")

class RedirectToGithubHandler(webapp.RequestHandler):
  def get(self):
    self.redirect('http://github.com/izuzak/pshbping')


application = webapp.WSGIApplication([('/ping.*', PSHBPingHandler), ('/.*', RedirectToGithubHandler)], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
