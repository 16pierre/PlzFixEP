"""
PlzFixEP is an open-source helper to import data into Engine Prime
Copyright (C) 2020  Quentin PIERRE

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import sqlite3
import json
import PyQt5.QtCore as qtcore
from beat_data import BeatData

NAME_TABLE_PERFORMANCE_DATA = "PerformanceData"
NAME_TABLE_TRACK = "Track"
NAME_COL_ID = "id"
NAME_COL_BEAT_DATA = "beatData"
NAME_COL_FILENAME = "filename"

def get_all_beat_data(path_performance_db, path_master_db):
    perf_conn = sqlite3.connect(path_performance_db)
    perf_c    = perf_conn.cursor()

    results = []

    query_str = "SELECT %s,%s FROM %s" % (NAME_COL_ID, NAME_COL_BEAT_DATA, NAME_TABLE_PERFORMANCE_DATA)
    error_count = 0
    not_analysed_tracks = []
    for row in perf_c.execute(query_str):
        try:
            if not row[1]:
                not_analysed_tracks.append(row[0])
            else:
                results.append(BeatData(uncompress(row[1]), row[0]))
        except Exception:
            error_count += 1
    if error_count:
        print("Database: Number of corrupted tracks: %s" % error_count)
    perf_conn.close()
    if not_analysed_tracks:
        print("The following tracks were not analysed by Engine Prime and therefore skipped:")
        id_to_filename_dict = get_track_id_to_filename_dict(path_master_db)
        for track_id in not_analysed_tracks:
            if track_id in id_to_filename_dict:
                print("- %s" % id_to_filename_dict[track_id])
        print("Total number of tracks not analysed: %d" % len(not_analysed_tracks))
    print("Tracks correctly loaded from Engine Prime: %d" % len(results))
    return results

def get_track_filename_to_id_dict(path_master_db):
    master_conn = sqlite3.connect(path_master_db)
    master_c    = master_conn.cursor()

    results = {}

    query_str = "SELECT %s,%s FROM %s" % (NAME_COL_ID, NAME_COL_FILENAME, NAME_TABLE_TRACK)
    for row in master_c.execute(query_str):
        results[row[1]] = row[0]
    master_conn.close()
    return results

def get_track_id_to_filename_dict(path_master_db):
    return {v: k for k, v in get_track_filename_to_id_dict(path_master_db).items()}

def update_beat_database(path_performance_db, beat_datas):
    perf_conn = sqlite3.connect(path_performance_db)
    perf_c    = perf_conn.cursor()

    for beat_data in beat_datas:
        query_str = "UPDATE %s SET %s=? WHERE %s=?" % (NAME_TABLE_PERFORMANCE_DATA, NAME_COL_BEAT_DATA, NAME_COL_ID)
        perf_c.execute(query_str, (compress(beat_data.to_bytes()), beat_data.id))
    perf_conn.commit()
    perf_conn.close()

def uncompress(raw_beat_data_from_db):
    uncompressed = qtcore.QByteArray()
    uncompressed = uncompressed.append(raw_beat_data_from_db)
    uncompressed = qtcore.qUncompress(uncompressed)
    return uncompressed.toHex().data().decode('ascii')

def compress(bytes_data):
    compressed = qtcore.QByteArray()
    compressed = compressed.append(bytes_data)
    compressed = qtcore.qCompress(compressed)
    return compressed.data()

if __name__ == "__main__":
    DEFAULT_PATH_PERFORMANCE_DB = "~/Music/Engine Library/p.db"
    DEFAULT_PATH_MASTER_DB = "~/Music/Engine Library/m.db"
    for b in get_all_beat_data(DEFAULT_PATH_PERFORMANCE_DB, DEFAULT_PATH_MASTER_DB):
        if (len(b.custom_anchors)) > 2:
            print(json.dumps(b, indent=4, default=lambda o: getattr(o, '__dict__', str(o))))

    print(get_track_filename_to_id_dict(DEFAULT_PATH_MASTER_DB))

