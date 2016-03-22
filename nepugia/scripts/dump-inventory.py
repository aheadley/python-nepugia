from nepugia import *
import sys
import os.path
import glob

item_db_files = glob.glob('/run/media/aheadley/16F9-2F2F/rebirth2-extracted-data/*/database/stitem*.gbin')
items = {}

for item_db_fn in item_db_files:
    print item_db_fn
    with open(item_db_fn) as f:
        item_data = GBNLFormat(ItemModel).parse_stream(f)

    item_strings = {s.v_relative_offset: s.value for s in item_data.strings}

    for item_row in item_data.rows:
        item_row.name = item_strings[item_row.name_offset]

    items.update({row.id: row for row in item_data.rows})

# items = {row.id: row for row in item_data.rows}

for fn in sys.argv[1:]:
    with open(fn) as f:
        data = RB2_SAVFormat.parse_stream(f)

    print fn
    for i, item_tuple in enumerate(data.inventory.slots):
        item_id, count = item_tuple.item_id, item_tuple.count
        try:
            print '{:04d}@{:06d}: {:3d}/{:<3d} x 0x{:04X}:[{}]'.format(i, 51792 + i * 4, count, items[item_id].max_count, item_id, items[item_id].name)
        except KeyError:
            print '{:04d}@{:06d}: {:3d}/{:<3d} x 0x{:04X}:[{}]'.format(i, 51792 + i * 4, count, 0, item_id, '**UNKNOWN**')


    # for row in sorted(data.rows, key=lambda r: r.id):
    # # for row in data.rows:
    #     print format_container(row)
    #     # print '{0:8d} [0x{0:8X}]: {1}'.format(
    #     #     row.id, format_container(row))
