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


This script syncs tracks to a USB drive.
My EP is broken: I can't drag and drop playlists or tracks to a flashdrive...
"""

import os
import sys
import json
import threading
import multiprocessing
from pathlib import Path
from shutil import copy

import database
from files_config import KEY_REKORDBOX_PATH, KEY_TRAKTOR_PATH, KEY_ENGINE_PRIME_PATH, DEFAULT_PATH_FOR_JSON_FILE

def get_files(path):
    """
    Walks files in the specified directory
    """

    files = []
    if os.path.isdir(path):
        for r, d, fs in os.walk(os.path.dirname(path)):
            files.extend([os.path.join(r, f) for f in fs])
        return files
    else:
        raise Exception("%s is not a folder" % path)

def copy_files(sources, dests):
    for i in range(len(sources)):
        Path(dests[i]).parent.mkdir(parents=True, exist_ok=True)
        print("Copying %s to %s" % (sources[i], dests[i]))
        copy(sources[i], dests[i])

def chunks(sources, dests, n):
    for i in range(0, len(sources), n):
        yield sources[i:i + n], dests[i:i + n]

def multi_thread_copy_files(sources, dests, nb_threads):

    if len(sources) < nb_threads:
        copy_files(sources, dests)
        return

    chunk_size = int(len(sources) / nb_threads)
    threads = []
    for chunked_sources, chunked_dests in chunks(sources, dests, chunk_size):
        t = threading.Thread(target=copy_files, args=(chunked_sources, chunked_dests))
        t.daemon = True
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


def sources_to_targets(base_dir, target_dir, sources):
    return [str(Path(target_dir).joinpath(Path(s).relative_to(base_dir)).resolve().absolute()) for s in sources]

def sources_to_flattened_targets(target_dir, sources):
    return [str(Path(target_dir).joinpath(Path(s).name).resolve().absolute()) for s in sources]

if __name__ == "__main__":

    if len(sys.argv) < 2:
        raise Exception("Usage: python3 copy_utils.py /path_your_flash_drive")

    """
    By default, flash drive structure looks like:
    /flash_drive/Engine Library/*.db
    /flash_drive/Engine Library/Music/{Artist}/{Album}/{TRACK}
    
    We can override the music paths though: we'll use a flattened music directory here
    """
    flash_drive_root = sys.argv[1]
    flash_drive_ep_root = os.path.join(flash_drive_root, "Engine Library")
    flash_drive_music_dir = os.path.join(flash_drive_ep_root, "Music")

    config_path = DEFAULT_PATH_FOR_JSON_FILE
    with open(config_path) as json_file:
        config = json.load(json_file)

    if not config.get(KEY_ENGINE_PRIME_PATH):
        print("Missing %s path in %s" % (KEY_ENGINE_PRIME_PATH, config_path))
        exit(1)
    ep_root = config.get(KEY_ENGINE_PRIME_PATH)

    database_files = get_files(ep_root)
    copy_files(database_files, sources_to_targets(ep_root, flash_drive_ep_root, database_files))

    ep_master_db = os.path.join(ep_root, "m.db")
    flash_drive_ep_master_db = os.path.join(flash_drive_ep_root, "m.db")

    tracks_to_id = database.get_track_absolute_filepaths_to_id_dict(ep_master_db)
    tracks_to_id = database.cleanup_missing_tracks_from_db_and_return_valid_tracks(flash_drive_ep_master_db, tracks_to_id)

    music_sources = list(tracks_to_id.keys())
    music_absolute_targets = sources_to_flattened_targets(flash_drive_music_dir, music_sources)
    music_relative_targets = [str(Path(m).relative_to(flash_drive_ep_root)) for m in music_absolute_targets]

    id_to_new_music_paths = dict()
    for i in range(len(music_sources)):
        id_to_new_music_paths[tracks_to_id[music_sources[i]]] = music_relative_targets[i]

    tracks = list(id_to_new_music_paths.values())
    for i in range(len(tracks)):
        for j in range(i+1, len(tracks)):
            if tracks[i] == tracks[j]:
                print("duplicate: %s" % tracks[i])

    database.override_music_paths(flash_drive_ep_master_db, id_to_new_music_paths)

    multi_thread_copy_files(music_sources, music_absolute_targets, multiprocessing.cpu_count())
    print("Done !")
