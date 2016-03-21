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

from .structs import CharStats
from .file_io import FileInFile

# The format of the packed file container. Nearly all game files are stored
# in side this container format. Note that the compression method is not yet
# known and all observed files are compressed so extracting the files is possible
# but not useful since they can't be decompressed
PACFormat = Struct('pac',
    Struct('header',
        Magic('DW_PACK\0'),
        # this is a guess based on minor_id
        Const(ULInt32('major_id'), 0x00),
        ULInt32('entry_count'),
        # this seems to correlate to the sequential files, eg:
        # GAME00000.pac has 0 here
        # GAME00001.pac has 1 here
        ULInt32('minor_id'),
    ),
    Array(lambda ctx: ctx.header.entry_count,
        Struct('entries',
            Magic('\x00\x00\x00\x00'),
            ULInt32('id'),
            String('name', 260, padchar='\x00'),
            Magic('\x00\x00\x00\x00'),
            ULInt32('stored_size'),
            ULInt32('real_size'),
            # all files are compressed
            Const(ULInt32('compression_flag'), 1),
            ULInt32('offset'),

            Value('v_data_handle', lambda ctx: lambda handle:
                FileInFile(handle, ctx._.a_entry_list_end + ctx.offset, ctx.stored_size)),
        )
    ),
    Anchor('a_entry_list_end'),
)

# The format of the string storage format (the *.gstr files). This is where
# the bulk of localization efforts would go, though there are localized strings
# in other files as well.
GSTLFormat = Struct('gstl',
    Struct('header',
        Magic('GSTL'),

        Magic('\x01\x00\x00\x00'),
        Magic('\x10\x00\x00\x00'),
        Magic('\x04\x00\x00\x00'),
        Magic('\x01\x00\x00\x00'),
        Magic('\x40\x00\x00\x00'),

        # number of str labels (ex: IDS_SOMETHING_OR_OTHER)
        # @0x18
        ULInt32('label_count'),

        # these are always observed to be 12, and 3 (respectively), use is
        # unknown (year and month of creation maybe?)
        Magic('\x0C\x00\x00\x00'),
        Magic('\x03\x00\x00\x00'),

        # end of header maybe, of end of label list
        ULInt32('end'),
        # total count of labels and strings
        ULInt32('str_count'),
        # @0x2c
        ULInt32('str_offset'),

        # 0x04 then zeros till @0x44
        Magic('\x04\x00\x00\x00'),
        Padding(16),
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
            # valid for the last item
            Value('v_length', lambda ctx: ctx.end_offset - ctx.start_offset),
        )
    ),
    Padding(8),
    Array(lambda ctx: ctx.header.str_count,
        CString('strings')
    )
)

def GBNLFormat(row_model=None):
    return Struct('gbnl',
        # note, footer struct size is 64
        Pointer(lambda ctx: -64,
            Struct('footer',
                Anchor('a_start'),
                Magic('GBNL'),

                # # 0x01 00 00 00
                # Const(ULInt32('const_00'), 0x01),
                # # 0x10 00 00 00
                # Const(ULInt32('const_01'), 0x10),
                # # 0x04 00 00 00
                # Const(ULInt32('const_02'), 0x04),
                # # 0x01 00 00 00
                # Const(ULInt32('const_03'), 0x01),
                # # 0x00 00 00 00
                # Const(ULInt32('const_04'), 0x00),
                # Padding(20),

                Magic('\x01\x00\x00\x00'),
                Magic('\x10\x00\x00\x00'),
                Magic('\x04\x00\x00\x00'),
                # this is 1 if there are strings at the end of the file, and 0
                # otherwise. not sure why since there is also a str_count field
                ULInt32('has_strings_flag'),
                Magic('\x00\x00\x00\x00'),

                # @0x18
                # possible string count?
                ULInt32('row_count'),
                # @0x1c
                # seems to be row size
                ULInt32('row_size'),
                # @0x20
                # this is the id of the model to use for the rows
                ULInt32('row_model_id'),
                # @0x24
                # some other kind of offset
                ULInt32('data_end_offset'),
                # @0x28
                # also possible string count
                # almost certainly string count
                ULInt32('str_count'),
                # @0x2c
                # string offset start
                ULInt32('str_offset'),

                Value('v_offset_diff', lambda ctx: ctx.str_offset - ctx.data_end_offset),
                Value('v_expected_data_size', lambda ctx: ctx.row_count * ctx.row_size),
                Value('v_data_size_diff', lambda ctx: ctx.data_end_offset - ctx.v_expected_data_size),

                # # @0x30
                # Const(ULInt32('const_05'), 0x04),
                Padding(4),

                # all 0x00
                Padding(12),
            )
        ),

        Array(lambda ctx: ctx.footer.row_count,
            Struct('rows',
                Embedded(row_model),
                Padding(lambda ctx: max(0, ctx._.footer.row_size - row_model.sizeof()))
            ) if row_model is not None else Padding(lambda ctx: ctx.footer.row_size)
        ),

        # this seems to be garbage data between the end of the data and start of the
        # strings
        Padding(lambda ctx: max(0, ctx.footer.v_offset_diff + ctx.footer.v_data_size_diff)),

        Anchor('a_strings_start'),
        Array(lambda ctx: ctx.footer.str_count,
            # CString('strings')
            Struct('strings',
                Anchor('start_offset'),
                Value('v_relative_offset', lambda ctx: ctx.start_offset - ctx._.a_strings_start),
                CString('value'),
                Anchor('end_offset'),
            )
        ),
        Anchor('a_strings_end'),
        # this seems to be garbage data between the end of the strings and the start
        # of the footer
        Padding(lambda ctx: ctx.footer.a_start - ctx.a_strings_end),

        Anchor('a_expected_footer_start'),
        # the footer struct would go here if we didn't need to parse it first
    )

RB2_SAVFormat = Struct('rb2_sav',
    Struct('header',
        ULInt16('game_id'),
        ULInt16('save_slot_id'),

        Padding(8),

        ULInt32('save_count'),
        Padding(4),
        Magic('\xD0\xB0\x0C\x00'),
        # only seems to be 3, 7, or 10
        ULInt32('unknown_01'),
        LFloat32('cursor_pos_x'),
        LFloat32('cursor_pos_y'),

        # Padding(3784),
        Padding(3548),
        # @3584

        Struct('game_stats',
            Padding(60),

            ULInt32('battle_count'),
            ULInt32('kill_count'),
            # suspect one of these is per-cycle
            ULInt32('cycle_kill_count'),
            ULInt32('ko_count'),
            ULInt32('escape_count'),
            ULInt32('hdd_activation_count'),
            ULInt32('max_damage_dealt'),
            ULInt32('max_combo_dealt'),

            # always seems to be 0
            Padding(4),

            ULInt32('total_damage_dealt'),

            Padding(4),

            ULInt32('total_damage_taken'),

            Padding(12),
            Array(4, SLInt32('unknown_12')),

            ULInt32('jump_count'),

            Padding(4),
            ULInt32('unknown_14'),

            ULInt32('rush_attack_count'),
            ULInt32('power_attack_count'),
            ULInt32('break_attack_count'),

            Array(5, SLInt32('unknown_15')),

            ULInt32('credits_spent'),
            # Array(4, SLInt16('unknown_18')),
            Padding(8),
            ULInt32('credits_gained'),
            Padding(4),
            ULInt32('credits_spent2'),

            Padding(16),
            ULInt32('quests_completed_count'),
            Padding(12),
        ),
        # Array(59, SLInt32('unknown_10')),

        # @3820
        CString('chapter_title'),
        Padding(lambda ctx: max(48 - (len(ctx.chapter_title)+1), 0)),
    ),

    Padding(20),

    # @3888
    Array(22, Struct('characters',
        # struct total = 1288 bytes

        # this probably means something but i have no idea what
        # Array(4, ULInt16('unknown_10')),
        Padding(8),
        String('name', 32, padchar='\x00'),

        ULInt32('xp_total'),
        ULInt16('unknown_22'),
        ULInt16('level'),
        # Array(4, ULInt16('unknown_12')),
        Padding(8),
        # this is some kind of id, maybe in stcharaplayer
        ULInt32('unknown_20'),
        ULInt32('unknown_21'),
        # this and the sp seem to be the current values (i.e. could be lower
        # if saved in a dungeon, could be higher if at full health since it
        # includes equipment bonuses)
        ULInt32('current_hp'),
        # seems to always be 0
        # ULInt32('unknown_23'),
        Padding(4),
        ULInt32('current_sp'),
        # seems to always be 100 so not going to record it
        # ULInt32('unknown_25'),
        Padding(4),

        # these seem to be the base stats before equipment bonuses
        CharStats,

        Padding(20),
        Struct('equipment',
            ULInt32('unknown_30'),

            ULInt32('weapon_id'),
            ULInt32('armor_id'),
            ULInt32('bracelet_id'),
            ULInt32('clothing_id'),
            ULInt32('accessory_id'),

            ULInt32('cpu_c_id'),
            ULInt32('cpu_h_id'),
            ULInt32('cpu_b_id'),
            ULInt32('cpu_s_id'),
            ULInt32('cpu_w_id'),
            ULInt32('cpu_l_id'),
        ),

        Padding(1072),
    )),
    # @32224

    Padding(19564),
    # @51788
    Struct('inventory',
        ULInt32('filled_slot_count'),
        Array(3000, Struct('slots',
            ULInt16('item_id'),
            ULInt8('count'),
            BitStruct('flags',
                Padding(5),
                # this one seems exclusive to plans, but not all plans have it
                Flag('bitflag_00'),
                # this seems to be related to dlc content
                Flag('bitflag_01'),
                # all plans seem to have this, but is not exclusive to plans
                Flag('bitflag_02'),
            ),
        )),

        # @63792
        ULInt32('current_credits'),
    ),


    Padding(492532),

    # @556328
    # Array(2420, ULInt16('unknown_80')),
    Padding(4840),

    Padding(249432),

    # @810600
    # Array(334, ULInt16('unknown_70')),
    Padding(668),

    Padding(20396),

    # @831664
    Struct('footer',
        Magic('\x01\x00\x00\x00'),
        Magic('\x12\x32'),
        Magic('\x50\x46'),
        Padding(8),
        Magic('\xFF\xCB\xE5\x00'),
        Array(4, ULInt16('unknown_99')),
    ),

    Padding(4),
)

SAVSlotFormat = Struct('savslot',
    Magic('SAVE0001'),

    # there might be some meaning to this, but is probably specific to ps3/vita
    # maybe CRCs?
    Padding(32),
    Padding(4),

    String('title', 64, padchar='\x00', encoding='shift-jis'),
    String('progress', 128, padchar='\x00'),
    String('status', 128, padchar='\x00'),

    Padding(384),

    String('save_icon_path', 64, padchar='\x00'),
    Padding(8),

    Struct('timestamp',
        ULInt16('year'),
        ULInt16('month'),
        ULInt16('day'),

        ULInt16('hour'),
        ULInt16('minute'),
        ULInt16('second'),

        ULInt32('unknown_00'),
    ),
)

FORMATS = {
    'gstl':     GSTLFormat,
    'gbnl':     GBNLFormat,
    'pac':      PACFormat,
    'rb2sav':   RB2_SAVFormat,
    'savslot':  SAVSlotFormat,
}
