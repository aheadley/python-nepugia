#!/bin/env python
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

__title__           = 'nepugia'
__version__         = '0.0.2'
__author__          = 'Alex Headley'
__author_email__    = 'aheadley@waysaboutstuff.com'
__license__         = 'The MIT License (MIT)'
__copyright__       = 'Copyright 2015 Alex Headley'
__url__             = 'https://github.com/aheadley/python-nepugia'
__description__     = """
Library for reading data from the Neptunia games
""".strip()

import logging
import os

from nepugia.formats import *
from nepugia.util import LOG_FORMAT, NullHandler, NEPUGIA_DEBUG

logger = logging.getLogger(__name__)

if NEPUGIA_DEBUG:
    _log_handler = logging.StreamHandler()
    _log_handler.setFormatter(LOG_FORMAT)
    _log_level = logging.DEBUG
else:
    _log_handler = NullHandler()
    _log_level = logging.INFO

logger.setLevel(_log_level)
logger.addHandler(_log_handler)
