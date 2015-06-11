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
__version__         = '0.0.1'
__author__          = 'Alex Headley'
__author_email__    = 'aheadley@waysaboutstuff.com'
__license__         = 'The MIT License (MIT)'
__copyright__       = 'Copyright 2015 Alex Headley'
__url__             = 'https://github.com/aheadley/python-nepugia'
__description__     = """
Library for reading data from the Neptunia games
""".strip()

from construct import *


# The format of the packed file container. Nearly all game files are stored
# in side this container format. Note that the compression method is not yet
# known and all observed files are compressed so extracting the files is possible
# but not useful since they can't be decompressed
PACFormat = Struct('pac',
    Struct('header',
        Magic('DW_PACK\0'),
        Padding(4),
        ULInt32('entry_count'),
        Padding(4)
    ),
    Array(lambda ctx: ctx.header.entry_count,
        Struct('entries',
            Padding(4),
            ULInt32('id'),
            String('name', 260, padchar='\0'),
            Padding(4),
            ULInt32('stored_size'),
            ULInt32('real_size'),
            # all files are compressed
            Const(ULInt32('compression_flag'), 1),
            ULInt32('offset')
        )
    )
)

# CPKFormat = Struct('cpk')

# The format of the string storage format (the *.gstr files). This is where
# the bulk of localization efforts would go, though there are localized strings
# in other files as well.
GSTLFormat = Struct('gstl',
    Struct('header',
        Magic('GSTL'),
        # set of 5 32bit ints [0x01 0x01 0x04 0x01 0x40]
        # seems constant
        Padding(20),
        # number of str labels (ex: IDS_SOMETHING_OR_OTHER)
        # @0x18
        ULInt32('label_count'),
        # these are always observed to be 12, and 3 (respectively), use is
        # unknown (year and month of creation maybe?)
        Const(ULInt32('always12'), 12),
        Const(ULInt32('always3'), 3),
        # end of header maybe, of end of label list
        ULInt32('end'),
        # total count of labels and strings
        ULInt32('str_count'),
        # @0x2c
        ULInt32('str_offset'),
        # 0x04 then zeros till @0x44
        Padding(20)
    ),
    # @0x44
    Array(lambda ctx: ctx.header.label_count,
        Struct('labels',
            ULInt32('id'),
            # starting offset of string
            ULInt32('start_offset'),
            # ending offset of string
            # the final value will be 5 as a sentinal value or something
            ULInt32('end_offset'),
            # note that this is a computed value and not present in the
            # on-disk structure, and because of the above note will not be
            # valid for the final value
            Value('length', lambda ctx: ctx.end_offset - ctx.start_offset)
        )
    ),
    Padding(8),
    Array(lambda ctx: ctx.header.str_count,
        CString('strings')
    )
)


GBNLFormat = Struct('gbnl',
    Struct('footer',
        Magic('GBNL'),
        Padding(60)
    )
)

# SAVFormat = Struct('sav')
# SAVSlotFormat = Struct('savslot')
