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

from nepugia.formats import PACFormat
from nepugia.file_io import chunked_copy, FileInFile
from nepugia.huffmanc import HuffmanCoding

if __name__ == '__main__':
    import os.path
    import sys
    import hashlib
    from StringIO import StringIO

    pac_filename = sys.argv[1]
    target_dir = sys.argv[2]

    get_target_path = lambda p: os.path.join(target_dir, p.replace('\\', '/'))
    hc = HuffmanCoding()

    with open(pac_filename) as pac_handle:
        pac_data = PACFormat.parse_stream(pac_handle)

        print pac_data.header

        for entry in pac_data.entries:
            target_path = get_target_path(entry.name)

            print '[{e.stored_size:08d}] {e.name} +> [{e.real_size:08d}] {t_path}'.format(e=entry, t_path=target_path)
            # print '%s -> %s' % (entry.name, target_path)

            try:
                os.makedirs(os.path.dirname(target_path))
            except OSError:
                pass

            with open(target_path, 'w') as target_file:
                with entry.v_data_handle(pac_handle) as entry_handle:
                    if entry.compression_flag:
                        chunk_set = entry.chunk_set.value
                        for i, chunk in enumerate(chunk_set.chunks):
                            print '++> decompressing chunk {c_id:03d} / {c_count:03d} [{c.stored_size:08d}] => [{c.real_size:08d}]'.format(
                                c_id=i+1,
                                c_count=chunk_set.header.chunk_count,
                                c=chunk)
                            with chunk.v_data_handle(entry_handle) as chunk_handle:
                                try:
                                    hc.decompress_stream(
                                        chunk_handle, target_file, chunk.real_size)
                                except Exception as err:
                                    print err
                    else:
                        chunked_copy(entry_handle.read, target_file.write)
