#!/bin/env python
# -*- coding: utf-8 -*-

import zlib

from construct import *

#NULL_PAD = Magic('\0' * 4)
NULL_PAD = Padding(4)

PACFile = Struct('pacfile',
    Struct('header',
        Magic('DW_PACK\0'),
        NULL_PAD,
        ULInt32('file_count'),
        NULL_PAD,
        Anchor('end')
    ),
    Struct('file_list',
        Array(lambda ctx: ctx._.header.file_count,
            Struct('file',
                NULL_PAD,
                ULInt32('id'),
                String('name', 260, padchar='\0'),
                NULL_PAD,
                ULInt32('compressed_size'),
                ULInt32('size'),
                ULInt32('compressed'),
                ULInt32('offset')
            )
        ),
        Anchor('end')
    )
)

GSTLFile = Struct('strfile',
    Struct('header',
        Magic('GSTL'),
        Padding(20),                # set of 5 32bit ints [0x01 0x01 0x04 0x01 0x40]
        ULInt32('label_count'),       # @0x18
        ULInt32('always12'),       #
        ULInt32('always3'),       #
        ULInt32('end_of_header'),       # end of header maybe
        ULInt32('str_count'),       # some kind of count
        ULInt32('str_offset'),      # @0x2c
        Padding(20),                # 0x04 then zeros till @0x44
        Array(lambda ctx: ctx.label_count,   # @0x44
            Struct('label',
                ULInt32('str_id'),
                ULInt32('start'),
                ULInt32('end')
            )
        ),
        Padding(8)
    ),
    # Probe('here'),
    Array(lambda ctx: ctx.header.str_count,
        CString('the_string')
    )
)

if __name__ == '__main__':
    import sys
    import os.path


    with open(sys.argv[1]) as file_handle:

        f = GSTLFile.parse_stream(file_handle)

        print f

        # pacfile = PACFile.parse_stream(file_handle)

        # print 'Found %d files...' % pacfile.header.file_count

        # if len(sys.argv) == 2:
        #     #print '\n'.join(f.name for f in pacfile.file_list.file)
        #     print pacfile.header
        #     sys.exit(0)

        # for fstruct in pacfile.file_list.file:
        #     print fstruct
        #     target_path = lambda p: os.path.join(sys.argv[2], p.replace('\\', '/'))
        #     target_fname = target_path(fstruct.name)
        #     print 'extracting %s -> %s' % (fstruct.name, target_fname)
        #     try:
        #         os.makedirs(os.path.dirname(target_fname))
        #     except OSError:
        #         pass
        #     file_handle.seek(pacfile.file_list.end + fstruct.offset)
        #     if not fstruct.compressed:
        #         print 'file not compressed!'
        #         continue

        #     with open(target_fname, 'w') as target_handle:
        #         target_handle.write(file_handle.read(fstruct.compressed_size))
