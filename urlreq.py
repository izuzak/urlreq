import cgi
import urllib

from django.utils import simplejson 
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError 
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class BaseHandler(webapp.RequestHandler):
  def options(self):
    if self.request.headers.has_key('Access-Control-Request-Method'):
      self.response.set_status(200)
      self.response.headers['Access-Control-Allow-Origin'] = self.request.headers['Origin']
      self.response.headers['Access-Control-Max-Age'] = 3600
      self.response.headers['Access-Control-Allow-Methods'] = self.request.headers['Access-Control-Request-Method']
    else:
      self.processRequest("OPTIONS")
    return
  
  def get(self):
    self.processRequest("GET")
    return
  
  def put(self):
    self.processRequest("PUT")
    return
  
  def post(self):
    self.processRequest("POST")
    return
  
  def delete(self):
    self.processRequest("DELETE")
    return
  
  def head(self):
    self.processRequest("HEAD")
    return
    
  def processRequest(self, method):
    params = self.setupRequest(method)
    result = 1
    
    if (params['success']):
      result = urlfetch.fetch(params['url'], payload=params['body'], headers=params['headers'], method=params['method'], deadline=10)
      result = self.setupResponse(result, method)
    else:
      result = self.setupParsingErrorResponse(method, params)
    
    self.response.set_status(result['status_code'])
    for header in result['headers'].keys():
      self.response.headers[header] = result['headers'][header]
      
    self.response.headers['Access-Control-Allow-Origin'] = '*'
    
    self.response.out.write(result['content'])
    
    return
    
class UrlReqHandler(BaseHandler):
  def setupRequest(self, method):
    qs = self.request.query_string
    parsedQs = cgi.parse_qs(qs)
    params = {}
    
    if parsedQs.has_key('url') and parsedQs.has_key('method'):
      params['success'] = True
      params['headers'] = {}
      params['body'] = None
      
      for header in parsedQs:
         if header == "url":
           params['url'] = urllib.unquote(parsedQs['url'][0])
         elif header == "method":
           params['method'] = urllib.unquote(parsedQs['method'][0])
         elif header == 'body':
           params['body'] = urllib.unquote(parsedQs['body'][0])
         else:
           params['headers'][urllib.unquote(header)] = urllib.unquote(parsedQs[header][0])
      
      return params
    
    params['success'] = False
    return params
  
  def setupResponse(self, result, method):
    return {'status_code' : result.status_code,
            'headers' : result.headers,
            'content' : result.content }
  
  def setupParsingErrorResponse(self, method, params):
    result = {}
    result['status_code'] = 400
    result['headers'] = { 'Content-Type' : "text/plain" }
    result['content'] = "Request must include method and url string parameters."
    return result

class PSHBPingHandler(BaseHandler):
  def setupRequest(self, method):
    qs = self.request.query_string
    parsedQs = cgi.parse_qs(qs)
    
    params = {}
    
    if parsedQs.has_key('hub') and parsedQs.has_key('topic'):
      params['success'] = True
      params['url'] = urllib.unquote(parsedQs['hub'][0])
      params['method'] = "POST"
      params['body'] = urllib.urlencode( { "hub.mode" : "publish", "hub.url" : parsedQs['topic']}, True )
      params['headers'] = { "Content-Type" : "application/x-www-form-urlencoded" }
      return params
    else:
      params['success'] = False
      return params
      
  def setupResponse(self, pingResult, method):
    if method == "POST":
      return {'status_code' : pingResult.status_code,
              'headers' : pingResult.headers,
              'content' : pingResult.content }
    else:
      result = {}
      result['status_code'] = 200
      result['headers'] = { 'Content-Type' : "text/plain" }
      result['content'] = str(pingResult.status_code) + "\n"
      
      for header in pingResult.headers.keys():
        result['content'] += header + ": " + pingResult.headers[header] + "\n"

      result['content'] += "\n" + pingResult.content
      return result
   
  def setupParsingErrorResponse(self, method, params):
    result = {}
    result['status_code'] = 400
    result['headers'] = { 'Content-Type' : "text/plain" }
    result['content'] = "Request must include hub and topic url query string parameters"
    return result

class PSHBSubHandler(BaseHandler):
  pass
#  def setupRequest(self, method):
#  def setupResponse(self, method, pingResult):
#  def setupParsingErrorResponse(self, method, params):
  
class RedirectToGithubHandler(webapp.RequestHandler):
  def get(self):
    self.redirect('http://github.com/izuzak/urlreq')


application = webapp.WSGIApplication([('/req.*', UrlReqHandler), 
                                      ('/pshbping.*', PSHBPingHandler),
                                      ('/pshbsub.*', PSHBSubHandler),
                                      ('/.*', RedirectToGithubHandler)], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
