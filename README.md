Overview
--------

URL Req is an HTTP proxy service that makes a HTTP request based on parameters defined in the URL of the request it received, and returns the response.

The service expects a definition of a HTTP request message in the URL of a request to the service. The service decodes the HTTP request defined in the URL, performs the decoded HTTP request and returns the received response as the response of calling the service. In essence, the service translates the definition of a HTTP request encoded in the URL to a real HTTP request. Furthermore, the service sets the [cross-origin resource sharing](http://www.w3.org/TR/cors/) headers so that it may be invoked from a Web applications executing in browsers.

The URL Req service is implemented and provided as public, open-source and free to use [AppEngine](http://code.google.com/appengine/) service.

Service API
-----------

The service is available at `http://urlreq.appspot.com/req`.

The API defines how a HTTP request should be encoded in the service request URLs. Element of a HTTP request are encoded as URL query parameters:

* (mandatory) HTTP method - `method` query parameter (e.g. `method=GET`)
* (mandatory) destination URL - `url` query parameter (e.g. `url=https://api.github.com/markdown/raw`)
* (optional) body - `body` parameter (e.g. `body=**Hello** _World_`)
* (optional, multiple) HTTP headers - multiple query parameters specified as `headerName=headerValue` (e.g. `Content-Type=text/plain`)
* (optional) debugMode - specifies debug mode and the response will be send as the body in text/plain (e.g. `debugMode=1`

Furthermore, the parameter names and values must be URL-encoded.

A full service call would look like this:

    http://urlreq.appspot.com/req?method=POST&url=https%3a//api.github.com/markdown/raw&body=**Hello**%20_World_&Content-Type=text/plain

which makes a `POST` HTTP request to the [GitHub markdown API](http://developer.github.com/v3/markdown/) url `https://api.github.com/markdown/raw` with the body `**Hello** _World_` and a HTTP header setting the `Content-Type` to `text/plain`. This response is HTML rendering of the input Markdown text.

URL builder
-----------

A simple URL builder for URL Req is available at: [http://izuzak.github.com/urlreq](http://izuzak.github.com/urlreq).

Motivation
----------

The purpose of the service is to assist developers in two situations:

* a Web service exposes an interface for calling [webhooks](http://en.wikipedia.org/wiki/Webhook) on certain events, but the interface allows that only the URL be specified while the body is usually predefined (e.g. the GitHub generic post-commit webhook). Since the URL Req service is a proxy that reads a full HTTP request from the requesting URL, specifying that HTTP request in the URL of the webhook interface is all you need to make any kind of HTTP request.
* a Web application executing in the browser must make cross-origin request to an API which does not currently implement CORS headers and is therefore inaccessible. Since the URL Req service always enables cross-origin calls, the service may be used as a proxy for invoking such APIs.

PSHBping
--------

PSHBping is a special case of the URL Req service which enables a simplified API for specifying a HTTP request for notifying a [PubSubHubbub](http://pubsubhubbub.googlecode.com) hub.

The PSHBping API has the following parameters, as defined in the [PSHB protocol spec](http://pubsubhubbub.googlecode.com/svn/trunk/pubsubhubbub-core-0.3.html):

* (mandatory) hub URL - `hub` query parameter (e.g. `hub=http://pubsubhubbub.appspot.com`)
* (mandatory) topic URLs - list of `topic` parameters (e.g. `topic=http://www.feed1.org/atom&topic=http://www.feed2.org/atom`)

The service is available at `http://urlreq.appspot.com/pshbping`, so a full service call would look like this:

    http://urlreq.appspot.com/pshbping?hub=http%3A//pubsubhubbub.appspot.com&topic=http%3A//www.feed1.org/atom&topic=http%3A//www.feed2.org/atom

which makes a `POST` HTTP request to `http://pubsubhubbub.appspot.com` with a HTTP header setting the `Content-Type` to `application/x-www-form-urlencoded` and has the body: `hub.mode=publish&hub.url=http%3A//www.feed1.org/atom&hub.url=http%3A//www.feed2.org/atom` (which is the required request format for notifying a PSHB hub that the feeds `http://www.feed1.org/atom` and `http://www.feed2.org/atom` have new content).

PSHBsub
--------

PSHBsub is a special case of the URLreq service which enables a simplified API for specifying a HTTP request for subscribing to and unsubscribing from a topic on a [PubSubHubbub](http://pubsubhubbub.googlecode.com) hub.

The PSHBsub API has the following parameters, as defined in the [PSHB protocol spec](http://pubsubhubbub.googlecode.com/svn/trunk/pubsubhubbub-core-0.3.html):

* (mandatory) hub URL - `hub` query parameter (e.g. `hub=http://pubsubhubbub.appspot.com`)
* (mandatory) topic URL - `topic` query parameters (e.g. `topic=http://www.feed1.org/atom`)
* (mandatory) callback URL - `callback` query parameter (e.g. `callback=http://requestb.in/p3quq4p3`)
* (mandatory) mode - `mode` query parameter (e.g. `mode=subscribe`)
* (mandatory) verify - `verify` query parameter (e.g. `verify=async`)
* (optional) lease_seconds - `lease_seconds` query parameter (e.g. `lease_seconds=3600`)
* (optional) secret - `secret` query parameter (e.g. `secret=319e59f6d0a60141bad685934223bb4522e24805`)
* (optional) verify_token - `verify_token` query parameter (e.g. `verify_token=testtoken`)

The service is available at http://urlreq.appspot.com/pshbsub so a full service call would look like this:

    http://urlreq.appspot.com/pshbsub?hub=http://pubsubhubbub.appspot.com&topic=http%3A//www.feed1.org/atom&callback=http%3a//requestb.in/p3quq4p3&mode=subscribe&verify=async

which makes a `POST` HTTP request to `http://pubsubhubbub.appspot.com` with a HTTP header setting the `Content-Type` to `application/x-www-form-urlencoded` and has the body: `hub.mode=subscribe&hub.topic=http%3A//www.feed1.org/atom&hub.callback=http%3a//requestb.in/p3quq4p3&hub.verify=async`.

Credits
-------

URL Req is developed by [Ivan Zuzak](http://ivanzuzak.info) [&lt;izuzak@gmail.com&gt;](mailto:izuzak@gmail.com).

License
-------

Licensed under the [Apache 2.0 License](https://github.com/izuzak/urlreq/blob/master/LICENSE).

[![gaugestracking alpha](https://secure.gaug.es/track.gif?h[site_id]=5162c1ce108d7b323800000e&h[resource]=http%3A%2F%2Fgithub.com%2Fizuzak%2Furlreq&h[title]=urlreq%20%28GitHub%29&h[unique]=1&h[unique_hour]=1&h[unique_day]=1&h[unique_month]=1&h[unique_year]=1 "ivanzuzak.info")](http://ivanzuzak.info/)
