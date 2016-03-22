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
        # unsure of order of agi/men/luk
        Struct('stats',
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
        ),

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
