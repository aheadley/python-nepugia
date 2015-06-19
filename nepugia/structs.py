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
        ),
        # LFloat32('f32'),
        Pass
    )

# unsure of order of agi/men/luk
CharStats = Struct('stats',
    ULInt32('hit_points'),
    Padding(4),
    ULInt32('skill_points'),
    ULInt32('strength'),
    ULInt32('vitality'),
    ULInt32('intelligence'),
    ULInt32('mentality'),
    ULInt32('agility'),
    ULInt32('technique'),
    Padding(4),
    ULInt32('luck'),
    ULInt32('movement'),
    Padding(4),
    Struct('resist',
        SLInt32('element_00'),
        SLInt32('element_01'),
        SLInt32('element_02'),
        SLInt32('element_03')
    ),

    Pass
)
