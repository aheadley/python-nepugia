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

from nepugia import *

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--format', choices=FORMATS)
    parser.add_argument('-m', '--model', choices=ROW_MODELS, default='none')
    parser.add_argument('-o', '--one-line', action='store_true', default=False)
    parser.add_argument('files', nargs='+')

    args = parser.parse_args()

    for fn in args.files:
        with open(fn) as file_handle:
            if args.format == 'gbnl':
                fmt_parser = FORMATS[args.format](ROW_MODELS[args.model])
            else:
                fmt_parser = FORMATS[args.format]

            parsed_file = fmt_parser.parse_stream(file_handle)
            print fn
            if args.one_line:
                print format_container(parsed_file)
            else:
                print parsed_file
