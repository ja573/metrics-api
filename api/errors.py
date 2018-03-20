import web
import json

class NotFound(web.HTTPError):
    """404 JSON Error"""
    def __init__(self):
        status = '404 Not Found'
        headers = {'Content-Type': 'application/json'}
        data = json.dumps({'status': 'error', 'count': 0, 'data': 'Not found'})
        web.HTTPError.__init__(self, status, headers, data)

    def GET(self, name):
        raise NotFound()

    def POST(self, name):
        raise NotAllowed()

    def PUT(self, name):
        raise NotAllowed()

    def DELETE(self, name):
        raise NotAllowed()

class NotAllowed(web.HTTPError):
    """405 JSON Error"""
    def __init__(self):
        status = '405 Method Not Allowed'
        headers = {'Content-Type': 'application/json'}
        data = json.dumps({'status': 'error','count': 0,'data': 'Not Allowed'})
        web.HTTPError.__init__(self, status, headers, data)
