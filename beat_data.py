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


import converter as co
import json

class ExternalTrack:
    def __init__(self, filename, bpm, firstDownBeatMs):
        self.filename = filename
        self.bpm = float(bpm)
        self.firstDownBeatMs = float(firstDownBeatMs)

class BeatData:

    def __init__(self, string, id=0):
        self.anchors = []
        self.custom_anchors = []

        sample_rate, string           = co.read_bytes_from_hexstring(string, 8)
        sample_length, string         = co.read_bytes_from_hexstring(string, 8)
        unknown, string               = co.read_bytes_from_hexstring(string, 1)
        # -> Always 0x01
        unknown_bytes, string         = co.read_bytes_from_hexstring(string, 4)
        # -> Always 0x00000000
        nb_anchors_reset, string      = co.read_bytes_from_hexstring(string, 4)
        nb_anchors_reset              = co.bin_to_sint_big_endian(nb_anchors_reset)

        for i in range(nb_anchors_reset):
            anchor, string = BeatAnchor.read_anchor(string)
            self.anchors.append(anchor)

        unknown_bytes2, string        = co.read_bytes_from_hexstring(string, 4)
        # -> Always 0x00000000
        nb_anchors_custom, string     = co.read_bytes_from_hexstring(string, 4)
        nb_anchors_custom             = co.bin_to_sint_big_endian(nb_anchors_custom)

        for i in range(nb_anchors_custom):
            anchor, string = BeatAnchor.read_anchor(string)
            self.custom_anchors.append(anchor)

        self.sample_rate              = co.bin_to_double_big_endian(sample_rate)
        self.sample_length            = co.bin_to_double_big_endian(sample_length)
        self.unknown = unknown
        self.unknown_bytes = unknown_bytes
        self.unknown_bytes2 = unknown_bytes2
        self.id = id

    def to_bytes(self):
        hex_bytes  = co.float_to_double_big_endian(self.sample_rate)
        hex_bytes += co.float_to_double_big_endian(self.sample_length)
        hex_bytes += b'\x01'
        hex_bytes += b'\x00\x00\x00\x00'
        hex_bytes += co.sint_to_big_endian(len(self.anchors))
        for anchor in self.anchors:
            hex_bytes += anchor.to_bytes()
        hex_bytes += b'\x00\x00\x00\x00'
        hex_bytes += co.sint_to_big_endian(len(self.custom_anchors))
        for anchor in self.custom_anchors:
            hex_bytes += anchor.to_bytes()
        return hex_bytes

    def override_with_external(self, external_track):
        central_sample = external_track.firstDownBeatMs / 1000.0 * self.sample_rate
        first_sample = central_sample
        samples_per_bar = 4.0 * self.sample_rate / external_track.bpm * 60.0
        beats_between_start_and_central = 0
        while(first_sample > 0):
            first_sample -= samples_per_bar
            beats_between_start_and_central += 4

        end_sample = central_sample
        beats_between_central_and_end = 0
        while(end_sample < self.sample_length):
            end_sample += samples_per_bar
            beats_between_central_and_end += 4
        
        central_anchor = BeatAnchor(central_sample, 0, 0, beats_between_central_and_end, 24576)
        first_anchor = BeatAnchor(first_sample, -beats_between_start_and_central, -1, beats_between_start_and_central, 0)
        last_anchor = BeatAnchor(end_sample, beats_between_central_and_end, 0, beats_between_central_and_end, 32767)
        self.custom_anchors = [first_anchor, central_anchor, last_anchor]

    def export_to_external_track(self):
        samples_per_beat = (self.custom_anchors[1].bits_to_anchor - self.custom_anchors[0].bits_to_anchor) / float(self.custom_anchors[0].beats_to_next_anchor)
        bpm = self.sample_rate / samples_per_beat * 60
        first_real_beat = self.custom_anchors[0].bits_to_anchor
        while first_real_beat < 0:
            first_real_beat += 4.0 * samples_per_beat
        return ExternalTrack("dummy", bpm, first_real_beat / self.sample_rate * 1000.0)

class BeatAnchor:

    def __init__(self, bits_to_anchor, beats_to_anchor, phase, beats_to_next_anchor, unknown2):
        self.bits_to_anchor = bits_to_anchor
        self.beats_to_anchor = beats_to_anchor
        self.phase = phase
        self.beats_to_next_anchor = beats_to_next_anchor
        self.unknown2 = unknown2

    @staticmethod
    def read_anchor(string):
        bits_to_anchor, string  = co.read_bytes_from_hexstring(string, 8)
        beats_to_anchor, string = co.read_bytes_from_hexstring(string, 4)
        phase, string           = co.read_bytes_from_hexstring(string, 4)
        beats_to_next_anchor, string        = co.read_bytes_from_hexstring(string, 4)
        unknown2, string        = co.read_bytes_from_hexstring(string, 4)

        bits_to_anchor = co.bin_to_double_little_endian(bits_to_anchor)
        beats_to_anchor = co.bin_to_sint_little_endian(beats_to_anchor)
        phase = co.bin_to_sint_little_endian(phase)
        beats_to_next_anchor = co.bin_to_sint_little_endian(beats_to_next_anchor)
        unknown2 = co.bin_to_sint_little_endian(unknown2)
        # always 0 for first anchor
        # always 32767 for second anchor if n_anchors = 2
        # always 24576 for second/third anchor if n_anchors = 3

        return BeatAnchor(bits_to_anchor, beats_to_anchor, phase, beats_to_next_anchor, unknown2), string

    def to_bytes(self):
        hex_bytes  = co.float_to_double_little_endian(self.bits_to_anchor)
        hex_bytes += co.sint_to_little_endian(self.beats_to_anchor)
        hex_bytes += co.sint_to_little_endian(self.phase)
        hex_bytes += co.sint_to_little_endian(self.beats_to_next_anchor)
        hex_bytes += co.sint_to_little_endian(self.unknown2)
        # TODO: Fix unknown with 0, 24576 etc. ?
        return hex_bytes

# Debug utils
if __name__ == "__main__":
    user_string = input()
    data = BeatData(user_string)
    print("====== ORIGINAL =====")
    print(json.dumps(data, indent=4, default=lambda o: getattr(o, '__dict__', str(o))))
    print("====== MODIFIED 1 =====")
    data.override_with_external(data.export_to_external_track())
    print(json.dumps(data, indent=4, default=lambda o: getattr(o, '__dict__', str(o))))
    print("====== MODIFIED 2 =====")
    data.override_with_external(data.export_to_external_track())
    print(json.dumps(data, indent=4, default=lambda o: getattr(o, '__dict__', str(o))))

