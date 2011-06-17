try:
    from urlparse import parse_qsl
except ImportError:
    from cgi import parse_qsl

BASE_HEADERS = [('Access-Control-Allow-Origin', '*')]

TEXT_HEADERS = [('Content-Type', 'text/plain')]

EXPECTED_PARAMS = ['server', 'port', 'pad', 'format']

FORMAT_MIME_TYPES = {
    'txt': 'text/plain',
    'html': 'text/html'
}

def make_wsgi_app(urlfetch):
    def application(environ, raw_start_response):
        def start_response(status, headers):
            raw_start_response(status, BASE_HEADERS + headers)

        def bad_request(msg):
            start_response('400 Bad Request', TEXT_HEADERS)
            return ['Bad Request - %s' % msg]
        
        params = dict(parse_qsl(environ['QUERY_STRING']))
    
        missing_params = [param for param in EXPECTED_PARAMS
                          if param not in params]

        if missing_params:
            return bad_request('required parameters missing: %s' % ', '.join(missing_params))

        try:
            params['port'] = int(params['port'])
        except ValueError:
            return bad_request('port must be an integer')

        if params['format'] not in ['html', 'txt']:
            return bad_request('invalid format')

        url = ('http://%(server)s:%(port)d/ep/pad/export/%(pad)s/latest'
               '?format=%(format)s' % params)

        try:
            response = urlfetch.fetch(url, deadline=10)
        except urlfetch.DownloadError:
            start_response('504 Gateway Timeout', TEXT_HEADERS)
            return ['Timeout exceeded']

        if response.status_code == 200:
            mimetype = FORMAT_MIME_TYPES[params['format']]
            start_response('200 OK', [('Content-Type', mimetype)])
            return [response.content]
        elif response.status_code == 404:
            start_response('404 Not Found', TEXT_HEADERS)
            return ['Not Found']
        else:
            start_response('502 Bad Gateway', TEXT_HEADERS)
            return ['Received response %d from server' % response.status_code]

    return application

if __name__ == '__main__':
    import unittest
    from urllib import urlencode
    from wsgiref.util import setup_testing_defaults

    class Request(object):
        def __init__(self, urlfetch=None, **query):
            self.environ = {}
            setup_testing_defaults(self.environ)
            self.environ['QUERY_STRING'] = urlencode(query)
            app = make_wsgi_app(urlfetch)
            response = app(self.environ, self.start_response)
            self.text = ''.join([part for part in response])

        def start_response(self, status, headers):
            self.status = status
            self.headers = dict(headers)

    class Response(object):
        def __init__(self, status_code, content=''):
            self.status_code = status_code
            self.content = content

    class UrlFetch(object):
        class DownloadError(Exception):
            pass

        def __init__(self, response_map=None, throw_timeout=False, default_status_code=404):
            self.throw_timeout = throw_timeout
            self.response_map = response_map or {}
            self.default_status_code = default_status_code

        def fetch(self, url, deadline):
            if self.throw_timeout:
                raise self.DownloadError()
            if url in self.response_map:
                return Response(200, self.response_map[url])
            return Response(self.default_status_code)

    class Tests(unittest.TestCase):
        def test_cors_headers_are_set(self):
            response = Request()
            self.assertEqual(response.headers['Access-Control-Allow-Origin'], '*')

        def test_no_params(self):
            response = Request()
            self.assertEqual(response.status, '400 Bad Request')
            self.assertEqual(response.text, 'Bad Request - required parameters missing: server, port, pad, format')

        def test_missing_params(self):
            response = Request(server='foo.com')
            self.assertEqual(response.status, '400 Bad Request')
            self.assertEqual(response.text, 'Bad Request - required parameters missing: port, pad, format')

        def test_bad_port(self):
            response = Request(server='foo.com', port='blah', pad='foo', format='txt')
            self.assertEqual(response.status, '400 Bad Request')
            self.assertEqual(response.text, 'Bad Request - port must be an integer')

        def test_bad_format(self):
            response = Request(server='foo.com', port='80', pad='foo', format='blah')
            self.assertEqual(response.status, '400 Bad Request')
            self.assertEqual(response.text, 'Bad Request - invalid format')

        def test_timeout(self):
            response = Request(UrlFetch(throw_timeout=True), server='foo.com', port='80', pad='foo', format='txt')
            self.assertEqual(response.status, '504 Gateway Timeout')
            self.assertEqual(response.text, 'Timeout exceeded')

        def test_404(self):
            response = Request(UrlFetch(), server='foo.com', port='80', pad='foo', format='txt')
            self.assertEqual(response.status, '404 Not Found')

        def test_other_error(self):
            response = Request(UrlFetch(default_status_code=500), server='foo.com', port='80', pad='foo', format='txt')
            self.assertEqual(response.status, '502 Bad Gateway')
            self.assertEqual(response.text, 'Received response 500 from server')

        def test_normal_response(self):
            urlmap = {
                'http://foo.com:80/ep/pad/export/bar/latest?format=html': '<p>hi</p>'
            }
            response = Request(UrlFetch(urlmap), server='foo.com', port='80', pad='bar', format='html')
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.text, '<p>hi</p>')
            self.assertEqual(response.headers['Content-Type'], 'text/html')            

    unittest.main()
