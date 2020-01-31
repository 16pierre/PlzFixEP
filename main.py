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

import database
import traktor
import rekordbox
import sys
import json
import os
from files_config import KEY_REKORDBOX_PATH, KEY_TRAKTOR_PATH, KEY_ENGINE_PRIME_PATH, DEFAULT_PATH_FOR_JSON_FILE

if __name__ == "__main__":

    if len(sys.argv) < 2 or sys.argv[1] not in ["rekordbox", "traktor"]:
        print("Usage: python3 main.py [required: rekordbox|traktor] [optional: 'json path']")
        exit(1)

    if len(sys.argv) < 3:
        config_path = DEFAULT_PATH_FOR_JSON_FILE
    else:
        config_path = sys.argv[1]

    with open(config_path) as json_file:
        config = json.load(json_file)

    soft = sys.argv[1]
    if not config.get(KEY_ENGINE_PRIME_PATH):
        print("Missing %s path in %s" % (KEY_ENGINE_PRIME_PATH, config_path))
        exit(1)
    if soft == "traktor" and not config.get(KEY_TRAKTOR_PATH):
        print("Missing %s path in %s" % (KEY_TRAKTOR_PATH, config_path))
        exit(1)
    if soft == "rekordbox" and not config.get(KEY_REKORDBOX_PATH):
        print("Missing %s path in %s" % (KEY_REKORDBOX_PATH, config_path))
        exit(1)
    
    EP_MASTER_DB = os.path.join(config.get(KEY_ENGINE_PRIME_PATH), "m.db")
    EP_PERF_DB = os.path.join(config.get(KEY_ENGINE_PRIME_PATH), "p.db")

    if soft == "traktor":
        tracks_in_traktor = traktor.get_tracks(config.get(KEY_TRAKTOR_PATH))
    else:
        tracks_in_traktor = rekordbox.get_tracks(config.get(KEY_REKORDBOX_PATH))

    filename_to_id_dict = database.get_track_filename_to_id_dict(EP_MASTER_DB)
    print("Number of tracks found in %s: %s" % (soft, len(tracks_in_traktor)))
    print("Number of tracks found in Engine Prime: %s" % len(filename_to_id_dict))
    common_tracks = [t for t in tracks_in_traktor if t.filename in filename_to_id_dict]
    print("Number of tracks in Engine Prime && %s: %s" % (soft, len(common_tracks)))

    print("Fetching beat datas from Engine Prime...")
    beat_datas = database.get_all_beat_data(EP_PERF_DB, EP_MASTER_DB)

    print("Writing data to Engine Prime...")
    engine_id_to_traktor_track = {}

    beat_datas_by_id = {}
    for beat_data in beat_datas:
        beat_datas_by_id[beat_data.id] = beat_data

    for traktor_track in common_tracks:
        if filename_to_id_dict[traktor_track.filename] in beat_datas_by_id:
            engine_id_to_traktor_track[filename_to_id_dict[traktor_track.filename]] = traktor_track


    for track_id, traktor_track in engine_id_to_traktor_track.items():
        beat_datas_by_id[track_id].override_with_external(traktor_track)

    database.update_beat_database(EP_PERF_DB, beat_datas_by_id.values())
    print("Done !")

