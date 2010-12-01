URLreq
======

URLreq is an [AppEngine](http://code.google.com/appengine/) service that functions as a simple HTTP proxy. The service expects a definition of a HTTP request message int the URL of a request to the service itself. The service decodes the HTTP request defined in the URL, performs the decoded HTTP request and returns the received response as the response of calling the service. In essence, the service translates the definition of a HTTP request encoded in the URL to a real HTTP request. Furthermore, the service sets the [cross-origin resource sharing](http://www.w3.org/TR/cors/) headers so that the it may be invoked from a Web applications executing in browsers.

Motivation
----------

The purpose of the service is to help in two situations:
1) a Web service exposes an interface for calling webhooks on certain events, but the interface allows that only the URL be specified while the body is usually predefined (e.g. the GitHub generic post-commit webhook). Since the URLreq service is a proxy that reads a full HTTP request from the requesting URL, specifying that HTTP request in the URL of the webhook interface is all you need to make any kind of HTTP request. 
2) a Web application executing in the browser must make cross-origin request to an API which does not currently implement CORS headers and is therefore inacessible. Since the URLreq service always enables cross-origin calls, the service may be used as a proxy for invoking such APIs.

API
---

The API defines the how HTTP should be encoded in the service request URLs. Element of a HTTP request are encoded as URL query parameters:
* HTTP method - "method" query parameter (e.g. `method=GET`)
* destination URL - "url" query parameter (e.g. `url=http://www.google.com`)
* (optional) body - "body" parameter (e.g. `body=HelloWorld`)
* (optional multiple) HTTP headers - multiple query parameters specified as headerName=headerValue (e.g. `Content-Type=text/plain`)
* (optional) debugMode - specifies debug mode and the response will be send as the body in text/plain (e.g. `debugMode=1`
Furthermore, the parameter names and values must be url encoded.

The service is available at `http://urlreq.appspot.com/req` so a full service call would look like this:

    http://urlreq.appspot.com/req?method=POST&url=http%3A//www.postbin.org/zrki0r&body='Hello%20World'&Content-Type=text/plain

which makes a `POST` HTTP request to the postbin url `http://www.postbin.org/zrki0r` with the body `Hello World` and a HTTP header setting the `Content-Type` to `text/plain`

PSHBping
--------

PSHBping is an special case of the URLreq service which enables a simplified API for specifying a HTTP request for notifying an a [PubSubHubbub](http://pubsubhubbub.googlecode.com) hub. 

The PSHBping API has the following parameters: 
* hub URL - "hub" query parameter (e.g. `hub=http://pubsubhubbub.appspot.com`)
* topic URLs - list of "topic" parameters (e.g. `topic=http://www.feed1.org/atom&topic=http://www.feed2.org/atom`)

The service is available at http://urlreq.appspot.com/pshbping so a full service call would look like this:

    http://urlreq.appspot.com/pshbping?hub=http%3A//pubsubhubbub.appspot.com&topic=http%3A//www.feed1.org/atom&topic=http%3A//www.feed2.org/atom

which makes a `POST` HTTP request to `http://pubsubhubbub.appspot.com` with a HTTP header setting the `Content-Type` to `application/x-www-form-urlencoded` and has the body: `hub.mode=publish&hub.url=http%3A//www.feed1.org/atom&hub.url=http%3A//www.feed2.org/atom`.

License
-------

[Apache 2.0](https://github.com/izuzak/urlreq/blob/master/LICENSE)
