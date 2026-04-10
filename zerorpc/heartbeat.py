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


import time
import gevent.pool
import gevent.queue
import gevent.event
import gevent.local
import gevent.lock

from .exceptions import LostRemote, TimeoutExpired
from .channel_base import ChannelBase


class HeartBeatOnChannel(ChannelBase):

    def __init__(self, channel, freq=5, passive=False):
        self._closed = False
        self._channel = channel
        self._heartbeat_freq = freq
        self._input_queue = gevent.queue.Channel()
        self._remote_last_hb = None
        self._lost_remote = False
        self._recv_task = gevent.spawn(self._recver)
        self._heartbeat_task = None
        self._parent_coroutine = gevent.getcurrent()
        self._compat_v2 = None
        if not passive:
            self._start_heartbeat()

    @property
    def recv_is_supported(self):
        pass

    @property
    def emit_is_supported(self):
        pass

    def close(self):
        self._closed = True
        if self._heartbeat_task is not None:
            self._heartbeat_task.kill()
            self._heartbeat_task = None
        if self._recv_task is not None:
            self._recv_task.kill()
            self._recv_task = None
        if self._channel is not None:
            self._channel.close()
            self._channel = None

    def _heartbeat(self):
        pass

    def _start_heartbeat(self):
        pass

    def _recver(self):
        pass

    def _lost_remote_exception(self):
        return LostRemote('Lost remote after {0}s heartbeat'.format(
            self._heartbeat_freq * 2))

    def new_event(self, name, args, header=None):
        if self._compat_v2 and name == u'_zpc_more':
            name = u'_zpc_hb'
        return self._channel.new_event(name, args, header)

    def emit_event(self, event, timeout=None):
        if self._lost_remote:
            raise self._lost_remote_exception()
        self._channel.emit_event(event, timeout)

    def recv(self, timeout=None):
        if self._lost_remote:
            raise self._lost_remote_exception()
        try:
            return self._input_queue.get(timeout=timeout)
        except gevent.queue.Empty:
            raise TimeoutExpired(timeout)

    @property
    def channel(self):
        pass

    @property
    def context(self):
        pass
