#! /usr/bin/python

from wsgiref.simple_server import make_server
from wsgiref.util import FileWrapper
import os
import mimetypes

DEFAULT_PORT = 8001

NEW_MIME_TYPES = {
    '.manifest': 'text/cache-manifest',
    '.webm': 'video/webm'
}

ROOT = os.path.abspath(os.path.dirname(__file__))

def make_app(options):
    
    for ext, mimetype in NEW_MIME_TYPES.items():
        mimetypes.add_type(mimetype, ext)
    
    def app(environ, start_response):
        path = environ['PATH_INFO']

        if path.endswith('/'):
            path = '%sindex.html' % path
        fileparts = path[1:].split('/')
        fullpath = os.path.join(ROOT, *fileparts)
        fullpath = os.path.normpath(fullpath)
        (mimetype, encoding) = mimetypes.guess_type(fullpath)
        if (fullpath.startswith(ROOT) and
            not '.git' in fullpath and
            os.path.isfile(fullpath) and
            mimetype):
            if mimetype == 'text/cache-manifest' and options.ignore_manifests:
                print "cache manifest exists, but pretending it doesn't."
                start_response('404 Not Found', [('Content-Type', 'text/plain')])
                return ['The manifest at ', path, 'exists, but this server ',
                        'is returning 404 because --ignore-cache-manifests is ',
                        'enabled.']
            else:
                print "returning existing cache manifest file."

            filesize = os.stat(fullpath).st_size
            start_response('200 OK', [('Content-Type', mimetype),
                                      ('Content-Length', str(filesize))])
            return FileWrapper(open(fullpath, 'rb'))

        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['Not Found: ', path]

    return app

if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option("-p", "--port", type="int", dest="port",
                      default=DEFAULT_PORT,
                      help="port to serve on")
    parser.add_option("-i", "--ignore-cache-manifests",
                      action="store_true", dest="ignore_manifests",
                      default=False,
                      help="ignore any .manifest files")

    (options, args) = parser.parse_args()

    server = make_server('127.0.0.1', options.port, make_app(options))
    print "serving on port %d" % options.port
    server.serve_forever()
