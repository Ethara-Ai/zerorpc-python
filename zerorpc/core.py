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
from builtins import str
from builtins import zip
from future.utils import iteritems

import sys
import traceback
import gevent.pool
import gevent.queue
import gevent.event
import gevent.local
import gevent.lock

from . import gevent_zmq as zmq
from .exceptions import TimeoutExpired, RemoteError, LostRemote
from .channel import ChannelMultiplexer, BufferedChannel
from .socket import SocketBase
from .heartbeat import HeartBeatOnChannel
from .context import Context
from .decorators import DecoratorBase, rep
from . import patterns
from logging import getLogger

logger = getLogger(__name__)


class ServerBase(object):

    def __init__(self, channel, methods=None, name=None, context=None,
            pool_size=None, heartbeat=5):
        self._multiplexer = ChannelMultiplexer(channel)

        if methods is None:
            methods = self

        self._context = context or Context.get_instance()
        self._name = name or self._extract_name()
        self._task_pool = gevent.pool.Pool(size=pool_size)
        self._acceptor_task = None
        self._methods = self._filter_methods(ServerBase, self, methods)

        self._inject_builtins()
        self._heartbeat_freq = heartbeat

        for (k, functor) in iteritems(self._methods):
            if not isinstance(functor, DecoratorBase):
                self._methods[k] = rep(functor)

    @staticmethod
    def _filter_methods(cls, self, methods):
        pass

    @staticmethod
    def _extract_name(methods):
        pass

    def close(self):
        self.stop()
        self._multiplexer.close()

    def _format_args_spec(self, args_spec, r=None):
        pass

    def _zerorpc_inspect(self):
        pass

    def _inject_builtins(self):
        pass

    def __call__(self, method, *args):
        if method not in self._methods:
            raise NameError(method)
        return self._methods[method](*args)

    def _print_traceback(self, protocol_v1, exc_infos):
        pass

    def _async_task(self, initial_event):
        pass

    def _acceptor(self):
        pass

    def run(self):
        pass

    def stop(self):
        if self._acceptor_task is not None:
            self._acceptor_task.kill()
            self._acceptor_task = None


class ClientBase(object):

    def __init__(self, channel, context=None, timeout=30, heartbeat=5,
            passive_heartbeat=False):
        self._multiplexer = ChannelMultiplexer(channel,
                ignore_broadcast=True)
        self._context = context or Context.get_instance()
        self._timeout = timeout
        self._heartbeat_freq = heartbeat
        self._passive_heartbeat = passive_heartbeat

    def close(self):
        self._multiplexer.close()

    def _handle_remote_error(self, event):
        pass

    def _select_pattern(self, event):
        pass

    def _process_response(self, request_event, bufchan, timeout):
        pass

    def __call__(self, method, *args, **kargs):
        # here `method` is either a string of bytes or an unicode string in
        # Python2 and Python3. Python2: str aka a byte string containing ASCII
        # (unless the user explicitly provide an unicode string). Python3: str
        # aka an unicode string (unless the user explicitly provide a byte
        # string).
        # zerorpc protocol requires an utf-8 encoded string at the msgpack
        # level. msgpack will encode any unicode string object to UTF-8 and tag
        # it `string`, while a bytes string will be tagged `bin`.
        #
        # So when we get a bytes string, we assume it to be an UTF-8 string
        # (ASCII is contained in UTF-8) that we decode to an unicode string.
        # Right after, msgpack-python will re-encode it as UTF-8. Yes this is
        # terribly inefficient with Python2 because most of the time `method`
        # will already be an UTF-8 encoded bytes string.
        if isinstance(method, bytes):
            method = method.decode('utf-8')

        timeout = kargs.get('timeout', self._timeout)
        channel = self._multiplexer.channel()
        hbchan = HeartBeatOnChannel(channel, freq=self._heartbeat_freq,
                passive=self._passive_heartbeat)
        bufchan = BufferedChannel(hbchan, inqueue_size=kargs.get('slots', 100))

        xheader = self._context.hook_get_task_context()
        request_event = bufchan.new_event(method, args, xheader)
        self._context.hook_client_before_request(request_event)
        bufchan.emit_event(request_event)

        # In python 3.7, "async" is a reserved keyword, clients should now use
        # "async_": support both for the time being
        if (kargs.get('async', False) is False and
            kargs.get('async_', False) is False):
            return self._process_response(request_event, bufchan, timeout)

        async_result = gevent.event.AsyncResult()
        gevent.spawn(self._process_response, request_event, bufchan,
                timeout).link(async_result)
        return async_result

    def __getattr__(self, method):
        return lambda *args, **kargs: self(method, *args, **kargs)


class Server(SocketBase, ServerBase):

    def __init__(self, methods=None, name=None, context=None, pool_size=None,
            heartbeat=5):
        SocketBase.__init__(self, zmq.ROUTER, context)
        if methods is None:
            methods = self

        name = name or ServerBase._extract_name(methods)
        methods = ServerBase._filter_methods(Server, self, methods)
        ServerBase.__init__(self, self._events, methods, name, context,
                pool_size, heartbeat)

    def close(self):
        ServerBase.close(self)
        SocketBase.close(self)


class Client(SocketBase, ClientBase):

    def __init__(self, connect_to=None, context=None, timeout=30, heartbeat=5,
            passive_heartbeat=False):
        SocketBase.__init__(self, zmq.DEALER, context=context)
        ClientBase.__init__(self, self._events, context, timeout, heartbeat,
                passive_heartbeat)
        if connect_to:
            self.connect(connect_to)

    def close(self):
        ClientBase.close(self)
        SocketBase.close(self)


class Pusher(SocketBase):

    def __init__(self, context=None, zmq_socket=zmq.PUSH):
        super(Pusher, self).__init__(zmq_socket, context=context)

    def __call__(self, method, *args):
        self._events.emit(method, args,
                self._context.hook_get_task_context())

    def __getattr__(self, method):
        return lambda *args: self(method, *args)


class Puller(SocketBase):

    def __init__(self, methods=None, context=None, zmq_socket=zmq.PULL):
        super(Puller, self).__init__(zmq_socket, context=context)

        if methods is None:
            methods = self

        self._methods = ServerBase._filter_methods(Puller, self, methods)
        self._receiver_task = None

    def close(self):
        self.stop()
        super(Puller, self).close()

    def __call__(self, method, *args):
        if method not in self._methods:
            raise NameError(method)
        return self._methods[method](*args)

    def _receiver(self):
        pass

    def run(self):
        pass

    def stop(self):
        if self._receiver_task is not None:
            self._receiver_task.kill(block=False)


class Publisher(Pusher):

    def __init__(self, context=None):
        super(Publisher, self).__init__(context=context, zmq_socket=zmq.PUB)


class Subscriber(Puller):

    def __init__(self, methods=None, context=None):
        super(Subscriber, self).__init__(methods=methods, context=context,
                zmq_socket=zmq.SUB)
        self._events.setsockopt(zmq.SUBSCRIBE, b'')


def fork_task_context(functor, context=None):
    '''Wrap a functor to transfer context.

        Usage example:
            gevent.spawn(zerorpc.fork_task_context(myfunction), args...)

        The goal is to permit context "inheritance" from a task to another.
        Consider the following example:

            zerorpc.Server receive a new event
              - task1 is created to handle this event this task will be linked
                to the initial event context. zerorpc.Server does that for you.
              - task1 make use of some zerorpc.Client instances, the initial
                event context is transferred on every call.

              - task1 spawn a new task2.
              - task2 make use of some zerorpc.Client instances, it's a fresh
                context. Thus there is no link to the initial context that
                spawned task1.

              - task1 spawn a new fork_task_context(task3).
              - task3 make use of some zerorpc.Client instances, the initial
                event context is transferred on every call.

        A real use case is a distributed tracer. Each time a new event is
        created, a trace_id is injected in it or copied from the current task
        context. This permit passing the trace_id from a zerorpc.Server to
        another via zerorpc.Client.

        The simple rule to know if a task need to be wrapped is:
            - if the new task will make any zerorpc call, it should be wrapped.
    '''
    pass
