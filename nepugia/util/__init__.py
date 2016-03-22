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

import os
import logging
try:
    # py2
    from cStringIO import StringIO
except ImportError:
    try:
        # py2 on some platform without cStringIO
        from StringIO import StringIO
    except ImportError:
        # py3k
        from io import StringIO

from construct import Union, ULInt32, Struct, ULInt16

def FourByteUnion(name):
    return Union(name,
        ULInt32('u32'),
        Struct('u16',
            ULInt16('a'),
            ULInt16('b'),
        ),
    )

def format_container(cntr):
    return ' '.join('{}={:24s}'.format(k, _pprint_value(v)) for k, v in cntr.iteritems())

def _pprint_value(value):
    if hasattr(value, 'keys'):
        return '{%s}' % format_container(value)
    if hasattr(value, 'sort'):
        return '[%s]' % ','.join(_pprint_value(i) for i in value)
    return str(value)

# NullHandler was added in py2.7
if hasattr(logging, 'NullHandler'):
    NullHandler = logging.NullHandler
else:
    class NullHandler(logging.Handler):
        def handle(self, record):
            pass

        def emit(self, record):
            pass

        def createLock(self):
            self.lock = None

LOG_FORMAT = logging.Formatter('[%(asctime)s] %(levelname)8s - %(name)s: %(message)s')

NEPUGIA_DEBUG = bool(os.environ.get('NEPUGIA_DEBUG', False))
