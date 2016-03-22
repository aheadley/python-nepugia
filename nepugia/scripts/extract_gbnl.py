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

import sys
import os.path

from nepugia.formats import GBNLFormat

def main():
    gbnl_fn = sys.argv[1]
    target_dir = sys.argv[2]
    extract_gbnl_rows(gbnl_fn, target_dir)

def extract_gbnl_rows(src_file, dest_dir):
    with open(src_file) as src_handle:
        gbnl_data = GBNLFormat().parse_stream(src_handle)
        src_handle.seek(0)

        for r in range(gbnl_data.footer.row_count):
            row_fn = os.path.join(dest_dir,
                '{}-{:05d}.row'.format(os.path.basename(src_file).split('.')[0], r))
            with open(row_fn, 'w') as row_handle:
                row_handle.write(src_handle.read(gbnl_data.footer.row_size))

if __name__ == '__main__':
    main()
