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

import re
import os
import web
import json
import psycopg2
from models import Event
from dateutil import parser

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

# Define routes
urls = (
    "/metrics(/?)", "MetricsDB",
    "(.*)", "NotFound",
)

def api_response(fn):
    """Decorator to provided consistency in all responses"""
    def response(self, *args, **kw):
        data  = fn(self, *args, **kw)
        count = len(data)
        if count > 0:
            return {'status': 'ok', 'count': count, 'data': data}
        else:
            raise NotFound()
    return response

def json_response(fn):
    """JSON decorator"""
    def response(self, *args, **kw):
        web.header('Content-Type', 'application/json')
        return json.dumps(fn(self, *args, **kw))
    return response

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

class RequestBroker(object):
    """Handles HTTP requests"""

    @json_response
    @api_response
    def GET(self, name):
        """Get Events for a given object ID"""
        logger.debug("Request: '%s' \n Query: %s" % (name, web.input()))

        obj_uri = web.input().get('obj_uri')
        try:
            assert obj_uri
        except AssertionError:
            logger.debug("Invalid obj_uri provided")
            raise NotFound()

        results = self.get_obj_events(obj_uri)
        data = []
        for e in results:
            event = Event(e[0], e[1], e[2], e[3], e[4], e[5])
            data.append(event.__dict__)
        return data

    @json_response
    @api_response
    def POST(self, name=None):
        """Create a new event"""
        data      = json.loads(web.data())
        obj_uri   = data.get('obj_uri')
        measure   = data.get('measure')
        value     = data.get('value')
        country   = data.get('country')
        uploader  = data.get('uploader')
        timestamp = parser.parse(data.get('timestamp'))

        try:
            assert obj_uri and measure and timestamp \
                   and value and country and uploader
        except AssertionError:
            logger.debug("Invalid parameters provided: %s" % (web.data()))
            raise NotFound()

        try:
            event = Event(obj_uri, measure, timestamp, value, country, uploader)
            self.save_event(event)
            return "Metrics submitted."
        except:
            raise NotFound()

    def PUT(self, name):
        raise NotAllowed()

    def DELETE(self, name):
        raise NotAllowed()

class MetricsDB(RequestBroker):
    """PostgesDB handler."""
    host     = os.environ['POSTGRES_HOST']
    dbname   = os.environ['POSTGRES_DB']
    user     = os.environ['POSTGRES_USER']
    passwd   = os.environ['POSTGRES_PASSWORD']

    def database_handle(self):
        dbconfig = "dbname='%s' user='%s' host='%s' password='%s'" % \
                   (self.dbname, self.user, self.host, self.passwd)
        try:
            return psycopg2.connect(dbconfig)
        except:
            msg = "Could not connect to database %s on host %s" % \
                  (self.dbname, self.host)
            logger.error(msg)
            raise

    def get_obj_events(self, key):
        result = Event.get_events(self.database_handle(), str(key))
        if result is not None:
            return result
        else:
            raise NotFound()

    def save_event(self, event):
        try:
            return event.save(self.database_handle())
        except:
            raise NotFound()

if __name__ == "__main__":
    logger.info("Starting API...")
    app = web.application(urls, globals())
    app.internalerror = web.debugerror
    web.config.debug = debug
    app.run()
