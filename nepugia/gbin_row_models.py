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

from construct import *

def FourByteUnion(name):
    return Union(name,
        ULInt32('u32'),
        Struct('u16',
            ULInt16('a'),
            ULInt16('b')
        )
    )

# row_size=292
ItemModel = Struct('item',
    # looks like some kind of bit field/flags
    ULInt32('type'),
    # almost certainly some kind of id, maybe correlates to something else
    # like a foreign key
    ULInt32('id'),
    # unknown
    ULInt32('dynamic_00'),

    # observed as all 0x00
    Padding(134),
    # Magic('\0' * 134),

    # @0x92
    # yes, 3 of the exact same values in a row
    FourByteUnion('const_00'),
    FourByteUnion('const_01'),
    FourByteUnion('const_02'),
    FourByteUnion('const_03'),

    FourByteUnion('dynamic_01'),
    # probably some kind of bitfield/flag
    FourByteUnion('dynamic_02'),

    # possibly a gameplay field (500, 2000, etc)
    FourByteUnion('dynamic_03'),

    # observed as all 0x00
    Padding(110),
    # Magic('\0' * 110),

    FourByteUnion('dynamic_05'),
    FourByteUnion('dynamic_06')
)

# note: ability model is very similar to item model
# row_size=292
AbilityModel = ItemModel

ROW_MODELS = {
    'none':         None,
    # 'blob':         BlobModel,

    'ability':      AbilityModel,
    'item':         ItemModel,
}
