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

from bitarray import bitarray

from ..util import StringIO
from ..util.file_io import chunked_copy

class HuffmanNode(object):
    SEGMENT_SIZE = 8

    @classmethod
    def build_tree(cls, bitstream, cursor=0, root_node=None):
        if root_node is None:
            root_node = cls()

        working_node = root_node.find_first_active()
        while working_node is not None:
            left_depth = cursor
            try:
                while bitstream[cursor]:
                    cursor += 1
            except IndexError as err:
                raise ValueError('Tree parsing aborted at bit: 0x%08X' % cursor, err)

            left_depth = cursor - left_depth
            cursor += 1

            value = bitstream[cursor:cursor+cls.SEGMENT_SIZE].tobytes()
            cursor += cls.SEGMENT_SIZE

            for _ in range(left_depth):
                working_node = working_node.expand_node()
            working_node.value = value

            working_node = root_node.find_first_active()

        return (root_node, cursor)

    def __init__(self):
        self.L = None
        self.R = None

        self.is_leaf = False
        self.is_active = True
        self._value = '\x00'

    def __repr__(self):
        return '{cls}(value={v})[{L},{R}]'.format(
            cls=self.__class__.__name__,
            v=repr(self._value),
            L=self.L,
            R=self.R,
        )

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self.is_active = False
        self.is_leaf = True
        self._value = new_value

    @property
    def children(self):
        return (self.L, self.R)

    def bilateral_expand(self):
        self.is_active = False
        self.is_leaf = False
        self.L = self.__class__()
        self.R = self.__class__()
        return self.children

    def expand_node(self):
        return self.bilateral_expand()[0]

    def find_first_active(self):
        if self.is_leaf:
            return None
        if self.is_active:
            return self

        if self.L.is_active:
            return self.L
        left = self.L.find_first_active()
        if left is not None:
            return left

        if self.R.is_active:
            return self.R
        right = self.R.find_first_active()
        if right is not None:
            return right

        return None

class HuffmanCoding(object):
    def __init__(self, node_cls=HuffmanNode):
        self._node_class = node_cls

    def compress_stream(self, input_buffer, output_buffer):
        raise NotImplemented

    def compress(self, input_data):
        output_handle = StringIO()
        self.compress_stream(StringIO(input_data), output_handle)
        return output_handle.getvalue()

    def decompress_stream(self, input_buffer, output_buffer, output_size):
        input_bits = bitarray(endian='big')
        chunked_copy(input_buffer.read, input_bits.frombytes)
        output_head = output_buffer.tell()

        root_node, cursor = self._node_class.build_tree(input_bits)

        while (output_buffer.tell() - output_head) < output_size:
            working_node = root_node
            while not working_node.is_leaf:
                try:
                    chu = input_bits[cursor]
                except IndexError as err:
                    raise ValueError('Data parsing aborted at bit: 0x%08X' % cursor, err)

                cursor += 1
                working_node = working_node.R if chu else working_node.L

                if working_node is None:
                    raise ValueError('Data parsing aborted, invalid working node')

            output_buffer.write(working_node.value)

    def decompress(self, input_data, output_size):
        output_handle = StringIO()
        self.decompress_stream(StringIO(input_data), output_handle, output_size)
        return output_handle.getvalue()

def compress(data):
    return HuffmanCoding().compress(data)

def decompress(data, data_size):
    return HuffmanCoding().decompress(data, data_size)
