# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2015 Alex Headley <aheadley@waysaboutstuff.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
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

import functools
import os
import logging

logger = logging.getLogger('naabal.util.file_io')

def only_if_open(orig_func):
    @functools.wraps(orig_func)
    def new_func(self, *pargs, **kwargs):
        if self.closed:
            raise IOError('I/O operation on closed file')
        else:
            return orig_func(self, *pargs, **kwargs)
    return new_func

def only_if_writable(orig_func):
    @functools.wraps(orig_func)
    def new_func(self, *pargs, **kwargs):
        if 'w' not in self.mode:
            raise IOError('File not open for writing')
        else:
            return orig_func(self, *pargs, **kwargs)
    return new_func

def chunked_copy(read_func, write_func, chunk_size=4 * 1024):
    bytes_copied = 0
    read = lambda: read_func(chunk_size)
    chunk = read()
    while chunk:
        write_func(chunk)
        bytes_copied += len(chunk)
        chunk = read()
    return bytes_copied

class FileInFile(object):
    _handle = None
    _mode = None
    _name = None
    _closed = True
    softspace = 0

    @property
    def closed(self):
        return self._closed and self._handle.closed

    @property
    def encoding(self):
        return None

    @property
    def mode(self):
        if self._writeable:
            return self._handle.mode
        else:
            return self._mode

    @property
    def name(self):
        return self._name

    @property
    def newlines(self):
        return None

    def __init__(self, parent_handle, offset=0, size=None, writeable=False, name=None):
        self._handle        = parent_handle
        self._writeable     = writeable and ('w' in self._handle.mode)
        if self._writeable:
            self._mode      = self._handle.mode
        else:
            self._mode      = 'rb'
        self._closed        = self._handle.closed
        if name is None:
            self._name      = self._handle.name
        else:
            self._name      = name
        self._offset        = offset
        if size is None:
            self._size      = os.fstat(self._handle.fileno()).st_size - offset
        else:
            self._size      = size
        self._position      = 0

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()

    def __repr__(self):
        return '<{state} {cls} \'{fn}\', mode \'{mode}\'>'.format(
            state='closed' if self.closed else 'open',
            cls=self.__class__.__name__,
            fn=self.name,
            mode=self.mode,
            )

    @only_if_open
    def tell(self):
        return self._position

    @only_if_open
    def seek(self, pos, mode=os.SEEK_SET):
        if mode == os.SEEK_SET:
            self._position = pos
        elif mode == os.SEEK_CUR:
            self._position += pos
        elif mode == os.SEEK_END:
            self._position = self._size + pos
        self._position = self._constrain_position(self._position)

    @only_if_open
    def read(self, size=None):
        size = self._normalize_size(size)
        self._handle.seek(self._offset + self._position)
        self._position += size
        return self._handle.read(size)

    @only_if_open
    @only_if_writable
    def write(self, data):
        if len(data) > self._normalize_size(len(data)):
            raise IOError('Attempted to write bytes beyond end of FileInFile')
        else:
            self._handle.seek(self._offset + self._position)
            self._position += len(data)
            self._handle.write(data)

    @only_if_open
    def flush(self):
        return self._handle.flush()

    @only_if_open
    def close(self):
        self.flush()
        self._name = None
        self._mode = None
        self._closed = True

    @only_if_open
    @only_if_writable
    def truncate(self, size=None):
        if size is None:
            size = self.tell()
        self._size = self._normalize_size(size)
        if self._position > self._size:
            self._position = self._size

    def fileno(self):
        if self.closed:
            return None
        else:
            return self._handle.fileno()

    def _normalize_size(self, size):
        if size is None:
            size = self._size - self._position
        return min(size, self._size - self._position)

    def _constrain_position(self, pos):
        pos = min(pos, self._size)
        pos = max(pos, 0)
        return pos
