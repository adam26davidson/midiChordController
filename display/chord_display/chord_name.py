
from music21 import chord as m21_chord

from display.display_constants import COLORS, FONTS


class ChordName:
    def __init__(self, master):
        self.master = master
        self.chord_name = ""
        self.past_chord_names = {}
        self.text_object = self.create_text_element()

    def create_text_element(self):
        x = self.master.width / 2
        y = self.master.height - x
        return self.master.create_text(
            x, y, fill=COLORS["chord"], text=self.chord_name, font=FONTS["big"], justify="center"
        )

    def set(self, chord_types, root_type):
        all_types = list(chord_types)
        all_types.sort()
        name_key = str(root_type) + " " + "-".join([str(t) for t in all_types])

        if not all_types.count(root_type) > 0:
            all_types.append(root_type)
        all_types.sort()

        text = ""
        if (name_key in self.past_chord_names):
            text, font_size = self.past_chord_names[name_key]
        else:
            text, font_size = self.generate_name(all_types, root_type)
            self.past_chord_names[name_key] = (text, font_size)

        self.master.itemconfigure(self.text_object, text=text, font=("sans serif", font_size))

    def generate_name(self, all_types, root_type):
        chord = m21_chord.Chord(all_types)
        # try:
        #     chord.root(m21Pitch.Pitch(self.master.noteNames[root_type]))
        # except:
        #     pass

        chord_name = chord.pitchedCommonName
        chord_name = chord_name.replace("-", " ")

        # deal with the enharmonic equivalent to stuff
        if (chord_name.find("enharmonic equivalent to") != -1 or chord_name.find("enharmonic to") != -1):
            chord_name = chord_name.replace("enharmonic to ", "")
            chord_name = chord_name.replace("enharmonic equivalent to ", "")
            chord_name = chord_name.replace("above ", "")
            words = chord_name.split(" ")
            key_name = words[len(words) - 1]
            words.remove(key_name)
            words.insert(0, key_name + "")
            chord_name = " ".join(words)

        chord_name = chord_name.replace("chord", "")
        chord_name = chord_name.replace("seventh", "7")
        chord_name = chord_name.replace("major", "maj")
        chord_name = chord_name.replace("minor", "min")
        chord_name = chord_name.replace("diminished", "dim")
        chord_name = chord_name.replace("augmented", "aug")
        chord_name = chord_name.replace("half-diminished", "h-dim")
        chord_name = chord_name.replace("dominant", "dom")
        chord_name = chord_name.replace("suspended", "sus")
        chord_name = chord_name.replace("ninth", "9")
        max_chars_per_line = 15

        if len(chord_name) > max_chars_per_line:
            lines = []
            words = chord_name.split(" ")
            while len(words) > 0:
                if len(words[0]) > max_chars_per_line: # to prevent infinite loop
                    lines.append(words.pop(0))
                else:
                    line = ""
                    while len(words) > 0 and (len(line) + len(words[0]) <= max_chars_per_line):
                        line += words.pop(0) + " "
                    lines.append(line)
            font_size = (int) ((self.master.radius * 1.65) / (max([len(line) for line in lines])))
        else:
            lines = [chord_name]
            font_size = (int) ((self.master.radius * 1.65) / (len(chord_name)))

        self.chord_name = chord_name
        text = "\n".join(lines)

        return text, font_size
