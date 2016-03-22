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

import logging
import sys
import os.path

from nepugia.formats import PACFormat
from nepugia.util.file_io import chunked_copy, FileInFile
from nepugia.compression.huffmanc import HuffmanCoding

logger = logging.getLogger(__name__)

def main():
    pac_filename = sys.argv[1]
    target_dir = sys.argv[2]
    extract_pac_file(pac_filename, target_dir)

def extract_pac_file(src_file, dest_dir):
    get_target_path = lambda p: os.path.join(dest_dir, p.replace('\\', '/'))

    logger.info('Opening PAC file: %s', src_file)
    with open(src_file) as pac_handle:
        pac_data = PACFormat.parse_stream(pac_handle)
        hc = HuffmanCoding()

        logger.info('Parsed %03d entries', len(pac_data.entries))

        for entry in pac_data.entries:
            target_path = get_target_path(entry.name)

            logger.debug('Found entry: id=%03d offset=0x%08X compressed=%d',
                entry.id, entry.offset, entry.compression_flag)
            logger.info('Unpacking entry "%s" @ %06d bytes to "%s" @ %06d bytes',
                entry.name, entry.stored_size, target_path, entry.real_size)

            try:
                os.makedirs(os.path.dirname(target_path))
            except OSError:
                pass

            with open(target_path, 'w') as target_file:
                with entry.vf_open(pac_handle) as entry_handle:
                    if entry.compression_flag:
                        chunk_set = entry.chunk_set.value
                        logger.info('Parsed %03d chunks of %08d bytes @ offset=0x%08X',
                            chunk_set.header.chunk_count, chunk_set.header.chunk_size, chunk_set.header.header_size)

                        for i, chunk in enumerate(chunk_set.chunks):
                            logger.info('Decompressing chunk #%03d @ %06d -> %06d bytes',
                                i, chunk.stored_size, chunk.real_size)

                            with chunk.vf_open(entry_handle) as chunk_handle:
                                try:
                                    hc.decompress_stream(
                                        chunk_handle, target_file, chunk.real_size)
                                except Exception as err:
                                    print err
                    else:
                        chunked_copy(entry_handle.read, target_file.write)

if __name__ == '__main__':
    main()

