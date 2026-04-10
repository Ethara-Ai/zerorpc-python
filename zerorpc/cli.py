#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Open Source Initiative OSI - The MIT License (MIT):Licensing
#
# The MIT License (MIT)
# Copyright (c) 2015 François-Xavier Bourlet (bombela+zerorpc@gmail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from __future__ import print_function
from builtins import map

import argparse
import json
import sys
import inspect
import os
import logging
from pprint import pprint

import zerorpc

try:
    # Try collections.abc for 3.4+
    from collections.abc import Iterator
except ImportError:
    # Fallback to collections for Python 2
    from collections import Iterator


parser = argparse.ArgumentParser(
    description='Make a zerorpc call to a remote service.'
)

client_or_server = parser.add_mutually_exclusive_group()
client_or_server.add_argument('--client', action='store_true', default=True,
        help='remote procedure call mode (default)')
client_or_server.add_argument('--server', action='store_false', dest='client',
        help='turn a given python module into a server')

parser.add_argument('--connect', action='append', metavar='address',
                    help='specify address to connect to. Can be specified \
                    multiple times and in conjunction with --bind')
parser.add_argument('--bind', action='append', metavar='address',
                    help='specify address to listen to. Can be specified \
                    multiple times and in conjunction with --connect')
parser.add_argument('--timeout', default=30, metavar='seconds', type=int,
                    help='abort request after X seconds. \
                    (default: 30s, --client only)')
parser.add_argument('--heartbeat', default=5, metavar='seconds', type=int,
                    help='heartbeat frequency. You should always use \
                    the same frequency as the server. (default: 5s)')
parser.add_argument('--pool-size', default=None, metavar='count', type=int,
                    help='size of worker pool. --server only.')
parser.add_argument('-j', '--json', default=False, action='store_true',
                    help='arguments are in JSON format and will be be parsed \
                    before being sent to the remote')
parser.add_argument('-pj', '--print-json', default=False, action='store_true',
                    help='print result in JSON format.')
parser.add_argument('-?', '--inspect', default=False, action='store_true',
                    help='retrieve detailed informations for the given \
                    remote (cf: command) method. If not method, display \
                    a list of remote methods signature. (only for --client).')
parser.add_argument('--active-hb', default=False, action='store_true',
                    help='enable active heartbeat. The default is to \
                    wait for the server to send the first heartbeat')
parser.add_argument('-d', '--debug', default=False, action='store_true',
                    help='Print zerorpc debug msgs, \
                    like outgoing and incomming messages.')
parser.add_argument('address', nargs='?', help='address to connect to. Skip \
                    this if you specified --connect or --bind at least once')
parser.add_argument('command', nargs='?',
                    help='remote procedure to call if --client (default) or \
                    python module/class to load if --server. If no command is \
                    specified, a list of remote methods are displayed.')
parser.add_argument('params', nargs='*',
                    help='parameters for the remote call if --client \
                    (default)')


def setup_links(args, socket):
    pass


def run_server(args):
    pass


# this function does a really intricate job to keep backward compatibility
# with a previous version of zerorpc, and lazily retrieving results if possible
def zerorpc_inspect_legacy(client, filter_method, long_doc, include_argspec):
    pass


# handle the 'python formatted' _zerorpc_inspect, that return the output of
# "getargspec" from the python lib "inspect". A monstruosity from protocol v2.
def zerorpc_inspect_python_argspecs(remote_methods, filter_method, long_doc, include_argspec):
    pass


# Handles generically formatted arguments (not tied to any specific programming language).
def zerorpc_inspect_generic(remote_methods, filter_method, long_doc, include_argspec):
    pass


def zerorpc_inspect(client, method=None, long_doc=True, include_argspec=True):
    pass


def run_client(args):
    pass


def main():
    pass
