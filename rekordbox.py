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


import xml.etree.ElementTree as ET
import json
import sys
import os
from beat_data import ExternalTrack
from urllib.parse import unquote

"""
Traktor XML format:
DJ_PLAYLISTS:
   COLLECTION:
      TRACK:
          {Location="fullpath"}
          TEMPO {Inizio="float s", Bpm}
"""

def get_tracks(xml_path):
    xml_root = ET.parse(xml_path).getroot()
    tracks = []
    unparsable_entries_counter = 0
    for entry in xml_root.findall("COLLECTION/TRACK"):
        location = entry.attrib.get("Location")
        if (entry is None or entry.find("TEMPO") is None or location is None):
            # TODO: make the debug better
            unparsable_entries_counter += 1
            continue
        bpm = entry.find("TEMPO").attrib['Bpm']
        filename = unquote(os.path.basename(location))

        firstBeat = float(entry.find("TEMPO").attrib['Inizio']) * 1000
        tracks.append(ExternalTrack(filename, bpm, firstBeat))
    if unparsable_entries_counter:
        print("Rekordbox, warning: couldn't import data for %s tracks." % unparsable_entries_counter)
    return tracks

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: rekordbox.py [XML filepath]")
    else:
        path = sys.argv[1]
        print(json.dumps(get_tracks(path), indent=4, default=lambda o: getattr(o, '__dict__', str(o))))
