import web
import json
from aux import get_input


NOTFOUND     = 10
NOTALLOWED   = 20
BADPARAMS    = 30
BADFILTERS   = 40
NORESULT     = 50
FATAL        = 60
UNAUTHORIZED = 70
FORBIDDEN    = 80
BADAUTH      = 90
DEFAULT      = NOTFOUND

_level_messages = {
    NOTFOUND:     'Not Found.',
    NOTALLOWED:   'Not Allowed.',
    BADPARAMS:    'Invalid parameters provided.',
    BADFILTERS:   'Invalid filters supplied.',
    NORESULT:     'No records have matched your search criteria.',
    FATAL:        'Something terrible has happened.',
    UNAUTHORIZED: 'Authentication is needed.',
    FORBIDDEN:    'You do not have permissions to access this resource.',
    BADAUTH:      'Wrong credentials provided.'
}

_level_statuses = {
    NOTFOUND:     '404 Not Found',
    NOTALLOWED:   '405 Method Not Allowed',
    BADPARAMS:    '400 Bad Request',
    BADFILTERS:   '400 Bad Request',
    NORESULT:     '404 Not Found',
    FATAL:        '500 Internal Server Error',
    UNAUTHORIZED: '401 Unauthorized',
    FORBIDDEN:    '403 Forbidden',
    BADAUTH:      '401 Unauthorized'
}

_level_codes = {
    NOTFOUND:     404,
    NOTALLOWED:   405,
    BADPARAMS:    400,
    BADFILTERS:   400,
    NORESULT:     404,
    FATAL:        500,
    UNAUTHORIZED: 401,
    FORBIDDEN:    403,
    BADAUTH:      401
}


class Error(web.HTTPError):
    """Exception handler in the form of http errors"""

    def __init__(self, level=DEFAULT, msg='', data=[]):
        self.httpstatus = self.get_status(level)
        self.httpcode = self.get_code(level)
        self.headers = {'Content-Type': 'application/json'}
        self.message = self.get_message(level)
        self.description = msg
        self.parameters = get_input()

        output = self.make_output(data)
        web.HTTPError.__init__(self, self.httpstatus, self.headers, output)

    def get_status(self, level):
        return _level_statuses.get(level)

    def get_code(self, level):
        return _level_codes.get(level)

    def get_message(self, level):
        return _level_messages.get(level)

    def make_output(self, data):
        return json.dumps({
            'status': 'error',
            'code': self.httpcode,
            'message': self.message,
            'description': self.description,
            'parameters': self.parameters,
            'count': len(data),
            'data': data
        })


def not_found():
    raise Error(NOTFOUND)


def internal_error():
    raise Error(FATAL)