#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Usage metrics JSON API prototype. Simple web.py based API to a PostgreSQL database.

usage: python metrics.py

(c) Javier Arias, Open Book Publishers, March 2018
Use of this software is governed by the terms of the MIT license

Dependencies:
  python-dateutil==2.4.2
  psycopg2==2.6.1
  web.py==0.38
"""

import os
import web
import json
import jwt
import psycopg2
from models import Event

from errors import NotFound, NotAllowed
from logic import save_new_entry

# uniformly receive all database output in Unicode
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

# determine logging level
import logging
debug = os.environ['API_DEBUG'] == 'True'
if debug:
    logging.basicConfig(level=logging.NOTSET)
else:
    logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

jwt_key = os.getenv('JWT_KEY', '')  # Key for decoding JWT

# Define routes
urls = (
    "/metrics(/?)", "MetricsDB",
    "(.*)", "NotFound",
)

def api_response(fn):
    """Decorator to provided consistency in all responses"""
    def response(self, *args, **kw):
        data  = fn(self, *args, **kw)
        count = len(data) if data else 0
        if count > 0:
            return {'status': 'ok', 'count': count, 'data': data}
        else:
            logger.debug("No output data")
            raise NotFound()
    return response

def json_response(fn):
    """JSON decorator"""
    def response(self, *args, **kw):
        web.header('Content-Type', 'application/json')
        return json.dumps(fn(self, *args, **kw))
    return response


def get_token_from_header():
    bearer = web.ctx.env.get('HTTP_AUTHORIZATION', '')
    return bearer.replace('Bearer ', '')


def check_token(fn):  # Use token-checking logic from the translation service.
    """Decorator to act as middleware, checking authentication token"""
    def response(self, *args, **kw):
        token = get_token_from_header()
        try:
            jwt.decode(token, jwt_key)
        except (
                jwt.exceptions.DecodeError,
                jwt.ExpiredSignatureError,
                jwt.InvalidTokenError
        ) as e:  # TODO: Add more meaningful feedback for each error.
            logger.error(e)
            raise NotAllowed
        return fn(self, *args, **kw)
    return response


class RequestBroker(object):
    """Handles HTTP requests"""

    @json_response
    @api_response
    @check_token
    def GET(self, name):
        """Get Events for a given object ID"""
        logger.debug("Request: '%s'; Query: %s" % (name, web.input()))

        uri = web.input().get('uri') or web.input().get('URI')
        try:
            assert uri
        except AssertionError:
            logger.debug("Invalid URI provided")
            raise NotFound()

        results = self.get_obj_events(uri)
        data = []
        for e in results:
            event = Event(e[0], e[1], e[2], e[3], e[4], e[5], e[6])
            data.append(event.__dict__)

        web.header('Access-Control-Allow-Origin', '*')

        return data

    @json_response
    @api_response
    @check_token
    def POST(self, name=None):
        """Create a new event"""
        data = json.loads(web.data())
        return save_new_entry(data)

    def PUT(self, name):
        raise NotAllowed()

    def DELETE(self, name):
        raise NotAllowed()

    @json_response
    def OPTIONS(self, name):
        web.header('Access-Control-Allow-Methods', 'OPTIONS, GET, HEAD')
        web.header('Access-Control-Allow-Headers', 'authorization')
        web.header('Access-Control-Allow-Origin', '*')

        return {'status': 'ok'}


class MetricsDB(RequestBroker):
    """PostgesDB handler."""

    def get_obj_events(self, key):
        result = Event.get_events(str(key))
        if result is not None:
            return result
        else:
            logger.debug("No data for URI: %s" % (key))
            raise NotFound()


if __name__ == "__main__":
    logger.info("Starting API...")
    app = web.application(urls, globals())
    app.internalerror = web.debugerror
    web.config.debug = debug
    app.run()
