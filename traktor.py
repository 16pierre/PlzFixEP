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
from beat_data import ExternalTrack

"""
Traktor XML format:
COLLECTION:
   ENTRY:
      TEMPO {BPM="119.999985" BPM_QUALITY="100.000000"}
      LOCATION {DIR="/:Users/:16pierre/:MSI/:", FILE="..."}
      CUE_V2 {NAME="AutoGrid/Beat Marker", START="float ms"}
"""

def get_tracks(nml_path):
    xml_root = ET.parse(nml_path).getroot()
    tracks = []
    unparsable_entries_counter = 0
    for entry in xml_root.findall("COLLECTION/ENTRY"):
        if (entry is None or entry.find("TEMPO") is None or entry.find("CUE_V2") is None):
            # TODO: make the debug better
            unparsable_entries_counter += 1
            continue
        bpm = entry.find("TEMPO").attrib['BPM']
        location = entry.find("LOCATION")
        filename = location.attrib['FILE']

        firstBeat = 0
        for cue in entry.findall("CUE_V2"):
            if cue.attrib['NAME'] in ['AutoGrid', 'Beat Marker']:
                firstBeat = cue.attrib['START']

        tracks.append(ExternalTrack(filename, bpm, firstBeat))
    if unparsable_entries_counter:
        print("Traktor, warning: couldn't import data for %s tracks." % unparsable_entries_counter)
    return tracks

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: traktor.py [NML filepath]")
    else:
        path = sys.argv[1]
        print(json.dumps(get_tracks(path), indent=4, default=lambda o: getattr(o, '__dict__', str(o))))
