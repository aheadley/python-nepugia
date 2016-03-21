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

if __name__ == '__main__':
    import os.path
    import sys

    pac_filename = sys.argv[1]
    target_dir = sys.argv[2]

    get_target_path = lambda p: os.path.join(target_dir, p.replace('\\', '/'))

    with open(pac_filename) as pac_file:
        pacfile = PACFormat.parse_stream(pac_file)

        print pacfile.header

        for entry in pacfile.entries:
            target_path = get_target_path(entry.name)
            print '%s -> %s' % (entry.name, target_path)

            try:
                os.makedirs(os.path.dirname(target_path))
            except OSError:
                pass

            with open(target_path, 'w') as target_file:
                target_file.write(entry.v_data_handle(pac_file).read())
