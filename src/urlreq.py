import webapp2
import urllib
import cgi
import time

from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class BaseHandler(webapp2.RequestHandler):
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

    parsedQs = cgi.parse_qs(self.request.query_string)

    if parsedQs.has_key('delay'):
      sleep_secs = int(parsedQs['delay'][0])
      if 0 <= sleep_secs <= 30:
        time.sleep(sleep_secs)
      else:
        raise ValueError('Delay parameter value must be >= 0 and <= 30 seconds.')

    if (params['success']):
      result = urlfetch.fetch(params['url'], payload=params['body'], headers=params['headers'], method=params['method'], deadline=10)
      result = { 'status_code' : result.status_code,
                 'headers' : result.headers,
                 'content' : result.content }
    else:
      result = self.setupParsingErrorResponse(method, params)

    if cgi.parse_qs(self.request.query_string).has_key('debugMode'):
      debugHeaders = {}
      debugHeaders.update(self.response.headers)
      if result.has_key('headers'):
        debugHeaders.update(result['headers'])
      debugHeaders.update( { 'Access-Control-Allow-Origin' : '*' } )
      self.response.set_status(200)
      self.response.headers['Content-Type'] = 'text'
      self.response.headers['Access-Control-Allow-Origin'] = '*'
      self.response.out.write("Response received:\n\n")
      self.response.out.write("Status code:\n%s\n\n" % (result['status_code']))
      self.response.out.write("Headers:\n%s\n\n" % "\n".join( item[0] + ": " + item[1] for item in debugHeaders.items()))
      self.response.out.write("Content:\n%s" % result['content'])
    else:
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

  def setupParsingErrorResponse(self, method, params):
    result = {}
    result['status_code'] = 400
    result['headers'] = { 'Content-Type' : "text/plain" }
    result['content'] = "Request must include method and url string parameters."
    return result

class PSHBSubHandler(BaseHandler):
  def setupRequest(self, method):
    qs = self.request.query_string
    parsedQs = cgi.parse_qs(qs)

    params = {}

    if parsedQs.has_key('hub') and parsedQs.has_key('topic') and parsedQs.has_key('callback') and parsedQs.has_key('mode') and parsedQs.has_key('verify'):
      params['success'] = True
      params['url'] = urllib.unquote(parsedQs['hub'][0])
      params['method'] = "POST"

      pshbParams = { "hub.mode" : parsedQs['mode'][0], "hub.topic" : parsedQs['topic'][0], "hub.callback" : urllib.unquote(parsedQs['callback'][0]), "hub.verify" : parsedQs['verify'][0]}

      if parsedQs.has_key('lease_seconds'):
        pshbParams['hub.lease_seconds'] = parsedQs['lease_seconds'][0]

      if parsedQs.has_key('secret'):
        pshbParams['hub.secret'] = urllib.unquote(parsedQs['secret'][0])

      if parsedQs.has_key('verify_token'):
        pshbParams['hub.verify_token'] = urllib.unquote(parsedQs['verify_token'][0])

      params['body'] = urllib.urlencode( pshbParams, True )
      params['headers'] = { "Content-Type" : "application/x-www-form-urlencoded" }

      return params
    else:
      params['success'] = False
      return params

  def setupParsingErrorResponse(self, method, params):
    result = {}
    result['status_code'] = 400
    result['headers'] = { 'Content-Type' : "text/plain" }
    result['content'] = "Request must include hub, topic, callback, mode and verify url query string parameters and optionally lease_seconds, secret, verify_token url query parameters."
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

  def setupParsingErrorResponse(self, method, params):
    result = {}
    result['status_code'] = 400
    result['headers'] = { 'Content-Type' : "text/plain" }
    result['content'] = "Request must include hub and topic url query string parameters"
    return result

class RedirectToGithubHandler(webapp2.RequestHandler):
  def get(self):
    self.redirect('http://github.com/izuzak/urlreq')

class PSHBAppenginePingHandler(BaseHandler):
  def setupRequest(self, method):
    qs = self.request.query_string
    parsedQs = cgi.parse_qs(qs)

    params = {}

    params['success'] = True
    params['url'] = 'http://pubsubhubbub.appspot.com/'
    params['method'] = "POST"
    params['body'] = urllib.urlencode( { "hub.mode" : "publish", "hub.url" : urllib.unquote(self.request.path[13:])}, True )
    params['headers'] = { "Content-Type" : "application/x-www-form-urlencoded" }
    return params

app = webapp2.WSGIApplication([('/req.*', UrlReqHandler),
                                      ('/pshbpinggae.*', PSHBAppenginePingHandler),
                                      ('/pshbping.*', PSHBPingHandler),
                                      ('/pshbsub.*', PSHBSubHandler),
                                      ('/.*', RedirectToGithubHandler)], debug=True)
