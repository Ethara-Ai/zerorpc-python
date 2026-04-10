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


from __future__ import absolute_import
from future.utils import tobytes

import uuid
import random

from . import gevent_zmq as zmq


class Context(zmq.Context):
    _instance = None

    def __init__(self):
        super(zmq.Context, self).__init__()
        self._middlewares = []
        self._hooks = {
            'resolve_endpoint': [],
            'load_task_context': [],
            'get_task_context': [],
            'server_before_exec': [],
            'server_after_exec': [],
            'server_inspect_exception': [],
            'client_handle_remote_error': [],
            'client_before_request': [],
            'client_after_request': [],
            'client_patterns_list': [],
        }
        self._reset_msgid()

    # NOTE: pyzmq 13.0.0 messed up with setattr (they turned it into a
    # non-op) and you can't assign attributes normally anymore, hence the
    # tricks with self.__dict__ here

    @property
    def _middlewares(self):
        pass

    @_middlewares.setter
    def _middlewares(self, value):
        pass

    @property
    def _hooks(self):
        pass

    @_hooks.setter
    def _hooks(self, value):
        pass

    @property
    def _msg_id_base(self):
        pass

    @_msg_id_base.setter
    def _msg_id_base(self, value):
        pass

    @property
    def _msg_id_counter(self):
        pass

    @_msg_id_counter.setter
    def _msg_id_counter(self, value):
        pass

    @property
    def _msg_id_counter_stop(self):
        pass

    @_msg_id_counter_stop.setter
    def _msg_id_counter_stop(self, value):
        pass

    @staticmethod
    def get_instance():
        pass

    def _reset_msgid(self):
        pass

    def new_msgid(self):
        pass

    def register_middleware(self, middleware_instance):
        pass

    #
    # client/server
    #
    def hook_resolve_endpoint(self, endpoint):
        for functor in self._hooks['resolve_endpoint']:
            endpoint = functor(endpoint)
        return endpoint

    def hook_load_task_context(self, event_header):
        pass

    def hook_get_task_context(self):
        pass

    #
    # Server-side hooks
    #
    def hook_server_before_exec(self, request_event):
        """Called when a method is about to be executed on the server."""
        pass

    def hook_server_after_exec(self, request_event, reply_event):
        """Called when a method has been executed successfully.

        This hook is called right before the answer is sent back to the client.
        If the method streams its answer (i.e: it uses the zerorpc.stream
        decorator) then this hook will be called once the reply has been fully
        streamed (and right before the stream is "closed").

        The reply_event argument will be None if the Push/Pull pattern is used.

        """
        pass

    def hook_server_inspect_exception(self, request_event, reply_event, exc_infos):
        """Called when a method raised an exception.

        The reply_event argument will be None if the Push/Pull pattern is used.

        """
        pass

    #
    # Client-side hooks
    #
    def hook_client_handle_remote_error(self, event):
        pass

    def hook_client_before_request(self, event):
        """Called when the Client is about to send a request.

        You can see it as the counterpart of ``hook_server_before_exec``.

        """
        pass

    def hook_client_after_request(self, request_event, reply_event, exception=None):
        """Called when an answer or a timeout has been received from the server.

        This hook is called right before the answer is returned to the client.
        You can see it as the counterpart of the ``hook_server_after_exec``.

        If the called method was returning a stream (i.e: it uses the
        zerorpc.stream decorator) then this hook will be called once the reply
        has been fully streamed (when the stream is "closed") or when an
        exception has been raised.

        The optional exception argument will be a ``RemoteError`` (or whatever
        type returned by the client_handle_remote_error hook) if an exception
        has been raised on the server.

        If the request timed out, then the exception argument will be a
        ``TimeoutExpired`` object and reply_event will be None.

        """
        pass

    def hook_client_patterns_list(self, patterns):
        pass
