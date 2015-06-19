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

def clean_string(value):
    return value

def lookup_string(offset, format):
    for string in format.strings:
        if offset == string.v_relative_offset:
            return string.value.strip()
    else:
        raise IndexError('String with offset [%d] not found' % offset)

def lookup_by_id(id, rows):
    for row in rows:
        if id == row.id:
            return row
    else:
        raise IndexError('Row with id [%d] not found' % id)

def uniq(values):
    return set(v for v in sorted(values) if v != 0)


if __name__ == '__main__':
    import sys
    import os.path
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--no-change-dungeon', default=False, action='store_true')
    parser.add_argument('db_dir')
    parser.add_argument('output_file')

    args = parser.parse_args()

    with open(args.output_file, 'w') as out_file:
        write = lambda line, *args: out_file.write(line.format(*args) + '\n')

        with open(os.path.join(args.db_dir, 'stitem.gbin')) as item_file:
            item_db = GBNLFormat(ItemModel).parse_stream(item_file)
        with open(os.path.join(args.db_dir, 'stcharamonster.gbin')) as monster_file:
            monster_db = GBNLFormat(CharaMonsterModel).parse_stream(monster_file)
        with open(os.path.join(args.db_dir, 'stdungeon.gbin')) as dungeon_file:
            dungeon_db = GBNLFormat(DungeonModel).parse_stream(dungeon_file)

        write('| Name | HP | Drops | XP | Credits |')
        write('|---|---|---|---|---|')
        for dungeon in dungeon_db.rows: #skip the first one and last because they are garbage
            normal_monster_ids = uniq(m.id \
                for spawn in dungeon.monster_spawn_sets[0].monster_spawns \
                    for m in spawn.monsters)
            add_monster_ids = uniq(m.id \
                for spawn in dungeon.monster_spawn_sets[1].monster_spawns \
                    for m in spawn.monsters) - normal_monster_ids
            change_monster_ids = uniq(m.id \
                for spawn in dungeon.monster_spawn_sets[2].monster_spawns \
                    for m in spawn.monsters) - normal_monster_ids

            normal_monster_ids = list(normal_monster_ids)
            add_monster_ids = list(add_monster_ids)
            change_monster_ids = list(change_monster_ids)

            if normal_monster_ids:
                write('| **{}** |---|---|---|---|', lookup_string(dungeon.name_offset, dungeon_db))

                for monster in sorted((lookup_by_id(mid, monster_db.rows) for mid in normal_monster_ids), key=lambda m: m.stats.hit_points):
                    drop_items = ['[%s]' % lookup_string(lookup_by_id(iid, item_db.rows).name_offset, item_db) \
                        for iid in uniq([monster.drop_item_00, monster.drop_item_01, monster.drop_item_02])]
                    write('| {} | {} | {} | {} | {} |',
                        monster.name, monster.stats.hit_points, ', '.join(drop_items),
                        monster.drop_exp, monster.drop_credits)

                for monster in sorted((lookup_by_id(mid, monster_db.rows) for mid in add_monster_ids), key=lambda m: m.stats.hit_points):
                    drop_items = ['[%s]' % lookup_string(lookup_by_id(iid, item_db.rows).name_offset, item_db) \
                        for iid in uniq([monster.drop_item_00, monster.drop_item_01, monster.drop_item_02])]
                    write('| *{}* | {} | {} | {} | {} |',
                        monster.name, monster.stats.hit_points, ', '.join(drop_items),
                        monster.drop_exp, monster.drop_credits)

            if change_monster_ids and not args.no_change_dungeon:
                write('| **{} (Change Dungeon)** |---|---|---|---|', lookup_string(dungeon.name_offset, dungeon_db))

                try:
                    for monster in sorted((lookup_by_id(mid, monster_db.rows) for mid in change_monster_ids), key=lambda m: m.stats.hit_points):
                        drop_items = ['[%s]' % lookup_string(lookup_by_id(iid, item_db.rows).name_offset, item_db) \
                            for iid in uniq([monster.drop_item_00, monster.drop_item_01, monster.drop_item_02])]
                        write('| {} | {} | {} | {} | {} |',
                            monster.name, monster.stats.hit_points, ', '.join(drop_items),
                            monster.drop_exp, monster.drop_credits)
                except IndexError as err:
                    sys.stderr.write(str(err) + '\n')
