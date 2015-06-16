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

# row_size=292
ItemModel = Struct('item',
    # looks like some kind of bit field/flags
    ULInt32('type'),
    # almost certainly some kind of id, maybe correlates to something else
    # like a foreign key
    ULInt32('id'),
    # str offset? seems to start at 0 and increase every time
    ULInt32('name_offset'),

    # observed as all 0x00
    Padding(134),
    # Magic('\0' * 134),

    # @0x92
    # yes, 3 of the exact same values in a row
    ULInt32('flags_00'),
    ULInt32('flags_01'),
    ULInt32('flags_02'),
    ULInt32('flags_03'),

    # always 0
    Magic('\x00\x00'),
    # small numbers, possibly levels
    ULInt16('game_effect_00'),

    # only seems to be 0, 1, or 99
    ULInt16('max_count'),
    # large numbers, buy price maybe?
    ULInt16('game_effect_01'),

    # possibly a character/use mask, usually 0, sometimes small (odd) numbers
    ULInt16('game_effect_02'),
    # large numbers, seems to always be less than game_effect_01
    ULInt16('game_effect_03'),

    # observed as all 0x00
    Padding(110),
    # Magic('\0' * 110),

    # seems to usually be 0, otherwise is less than 10
    ULInt16('dynamic_05'),
    # possibly label ids
    ULInt16('dynamic_06'),
    # possibly string offsets
    ULInt32('desc_offset'),

    Pass
)

AbilityModel = ItemModel

CharaMonsterModel = Struct('charamonster',
    # flag field, use unknown
    ULInt32('flag_00'),
    # this isn't certain, it seems to be unique but unconfirmed, and the rows
    # are completely in this order, it jumps around
    ULInt16('id'),
    # use unknown, but numbers all seem to be low, generally less than 20
    ULInt16('dynamic_01'),

    String('name', 32, padchar='\x00'),

    # always 0, except for CPUs/CPU candidate entries, where is small number
    ULInt32('dynamic_10'),
    ULInt16('flag_20'),
    # use unknown, numbers start small and increase slowly
    ULInt16('dynamic_11'),
    Padding(2),
    # larger numbers, generally 300-400 ish, small variance
    ULInt16('dynamic_12'),
    # very small numbers, less than 10
    ULInt16('dynamic_13'),
    # usually 0, sometimes larger 200ish
    ULInt16('dynamic_14'),

    # @56
    # observed as all 0x00
    Padding(24),

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
        ULInt32('unknown_stat'),
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
    ),
    Padding(20),

    # @168
    # only cpus/candidates have these, possibly voice/event data? or something
    # with the cpu form
    ULInt32('flag_10'),
    Array(11, ULInt32('dynamic_50')),

    Padding(152),

    # @368
    # this is not actually empty, just haven't decoded it yet
    Padding(116),

    # @484
    # observed as all 0x00 in ~10 samples
    Padding(736),

    # @1220
    # these always seem to be 0.07 and 0.15 respectively
    # not sure what the use is
    LFloat32('fp_00'),
    LFloat32('fp_01'),

    ULInt32('dynamic_20'),
    ULInt32('dynamic_21'),
    ULInt32('dynamic_22'),
    ULInt32('dynamic_23'),
    ULInt32('stat_guard_points'),

    ULInt32('drop_exp'),
    # @1252
    ULInt32('drop_credits'),

    # these are a total guess/gut feeling, should be x/100
    ULInt32('drop_chance_any'),
    ULInt32('drop_chance_item_00'),
    ULInt32('drop_chance_item_01'),
    ULInt32('drop_chance_item_02'),

    # @0x04f8
    ULInt32('drop_item_00'),
    ULInt32('drop_item_01'),
    ULInt32('drop_item_02'),
    Magic('\x00' * 4),

    # Value('v_drop_exp_bonus', lambda ctx: ctx.drop_exp * 1.3),

    Pass
)

RemakeModel = Struct('remake',
    ULInt32('name_offset'),
    ULInt16('id'),
    ULInt16('category_id'),
    ULInt16('plan_item_id'),
    ULInt16('result_id'),

    ULInt16('dynamic_00'),
    Padding(4),
    ULInt16('dynamic_01'),
    ULInt16('dynamic_02'),
    Padding(4),

    # @26
    ULInt16('flag_10'),
    ULInt32('flag_11'),
    Magic('\x01'), Padding(3),

    ULInt16('dynamic_10'),
    ULInt16('dynamic_11'),
    ULInt16('dynamic_12'),
    ULInt16('dynamic_13'),

    # @44
    Array(3,
        Struct('components',
            ULInt16('item_id'),
            ULInt16('count')
        )
    ),
    Padding(8),

    # @64
    ULInt32('dynamic_20'),
    ULInt32('dynamic_21'),
    ULInt32('dynamic_22'),
    ULInt32('dynamic_23'),
    Padding(16),

    # @96
    ULInt32('dynamic_30'),
    ULInt32('dynamic_31'),
    ULInt32('author_offset'),
    ULInt32('desc_offset'),

    Pass
)

TreasureModel = Struct('treasure',
    ULInt32('id'),
    Array(3, Struct('item',
        ULInt32('id'),
        ULInt32('drop_chance'),
        ULInt32('flag_00'),
        ULInt32('flag_01')
    )),

    Pass
)

DungeonModel = Struct('dungeon',
    ULInt16('id'),
    # this is related to the environment of the dungeon in some way
    ULInt16('env_effect_00'),
    Padding(6),
    # also related to the environment of the dungeon somehow, guessing the icon
    # based on what it's shared with
    ULInt16('icon_id'),
    # the world map seems to use a coordinate system of:
    #  x=left<>right [0,~1600]
    #  y=top<>bottom [0,~1600]
    ULInt32('map_pos_x'),
    ULInt32('map_pos_y'),
    # always seems to be a multiple of 100
    ULInt16('dynamic_02'),
    ULInt16('dynamic_03'),

    # @24
    ULInt32('name_offset'),

    ULInt16('dynamic_10'),
    ULInt16('dynamic_11'),
    ULInt16('dynamic_12'),
    Padding(18),

    # @52
    Array(10, ULInt32('dynamic_41')),
    Array(5, Struct('treasure_boxes',
        ULInt32('id'),
        Array(3, Struct('drops',
            ULInt32('item_id'),
            ULInt32('drop_chance'),
            ULInt32('flag_00'),
            ULInt32('flag_01'),
        ))
    )),

    # @352
    # array totals 4860 bytes
    # [0]= regular
    # [1]= +add enemies
    # [2]= +change dungeon
    Array(3, Struct('monster_spawn_sets',
        Array(15, Struct('monster_spawns',
            # always 0x01 00
            Padding(2),
            ULInt16('dynamic_23'),
            Padding(2),

            # Array(28, ULInt16('dynamic_20')),
            Padding(56),

            Array(4, Struct('monsters',
                ULInt16('id'),
                ULInt16('dynamic_21'),
                ULInt16('dynamic_22'),
                Padding(2)
            )),
            # always 0x00
            Padding(14)
        ))
    )),

    # @5212
    # array totals 2340 bytes
    Array(3, Struct('unknown_block_01',
        Array(65, ULInt32('dynamic_30')),
        Padding(520)
    )),
    ULInt32('dynamic_99'),
    Padding(16),

    Pass
)

ROW_MODELS = {
    'none':         None,
    # 'blob':         BlobModel,

    'ability':      AbilityModel,
    'item':         ItemModel,
    'charamonster': CharaMonsterModel,
    'remake':       RemakeModel,
    'treasure':     TreasureModel,
    'dungeon':      DungeonModel,
}

# MODEL_ID_MAP = {
#     2:          MuseumModel,
#     3:          SQStoneSkillModel,
#     4:          NepupediaModel,
#     6:          DiscCombiModel,
#     7:          AvatarModel,
#     9:          BattleAiModel,
#     12:         DiscItemModel,
#     14:         BlogModel,
#     15:         GalleryModel,
#     16:         MotionPortraitModel,
#     19:         HelpModel,
#     20:         AreaModel,
#     23:         CharaLevelUpModel,
#     28:         AvatarMessageModel,
#     45:         RemakeModel,
#     68:         QuestModel,
#     86:         SkillModel,
#     113:        AbilityModel,
#     341:        CharaMonsterModel,
#     666:        SQDungeonModel,
#     2533:       DungeonModel,
# }
