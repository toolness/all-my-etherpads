# Etherpad Export Proxy

This is a dead simple server that provides a cross-domain RESTful API to
retrieve Etherpad contents from any public Etherpad server on the internet.

The server only has one method, accessible at `/`, which takes a few
parameters via query string, all of which are required:

* **server** is the domain name of the server on which the Etherpad resides.

* **port** is the port number on which the Etherpad is hosted.

* **pad** is the name of the Etherpad.

* **format** is the format of the exported contents, either `txt` or `html`.

While the code runs as a Google App Engine application, it's just a
WSGI app that is loosely coupled to the `google.appengine.api.urlfetch`
package.

To run the unit tests, simply run `python etherpad_export.py`.

Running the server can be done by downloading and running the [Google App Engine SDK for Python][python-sdk].

  [python-sdk]: http://code.google.com/appengine/downloads.html#Google_App_Engine_SDK_for_Python
