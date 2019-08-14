#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import web
import logging


def debug_mode():
    trues = ('True', 'true', True, 1)
    return 'API_DEBUG' in os.environ and os.environ['API_DEBUG'] in trues


def logger_instance(name):
    level = logging.NOTSET if debug_mode() else logging.ERROR
    logging.basicConfig(level=level)
    return logging.getLogger(name)


def strtolist(data):
    if isinstance(data, str) or isinstance(data, dict):
        return [data]
    elif isinstance(data, list):
        return data


def is_get_request():
    return web.ctx.env.get('REQUEST_METHOD', '') == 'GET'


def get_input():
    return web.input() if is_get_request() else web.data().decode('utf-8')