
from music21 import chord as m21Chord

from display.displayConstants import COLORS, FONTS


class ChordName:
    def __init__(self, master):
        self.master = master
        self.chordName = ""
        self.pastChordNames = {}
        self.textObject = self.createText()

    def createText(self):
        x = self.master.width / 2
        y = self.master.height - x
        return self.master.create_text(
            x, y, fill=COLORS["chord"], text=self.chordName, font=FONTS["big"], justify="center"
        )

    def set(self, chordTypes, rootType):
        allTypes = list(chordTypes)
        allTypes.sort()
        nameKey = str(rootType) + " " + "-".join([str(t) for t in allTypes])

        if not allTypes.count(rootType) > 0:
            allTypes.append(rootType)
        allTypes.sort()

        text = ""
        if (nameKey in self.pastChordNames):
            text, fontSize = self.pastChordNames[nameKey]
        else:
            text, fontSize = self.generateName(allTypes, rootType)
            self.pastChordNames[nameKey] = (text, fontSize)

        self.master.itemconfigure(self.textObject, text=text, font=("sans serif", fontSize))

    def generateName(self, allTypes, rootType):
        chord = m21Chord.Chord(allTypes)
        # try:
        #     chord.root(m21Pitch.Pitch(self.master.noteNames[rootType]))
        # except:
        #     pass

        chordName = chord.pitchedCommonName
        chordName = chordName.replace("-", " ")

        # deal with the enharmonic equivalent to stuff
        if (chordName.find("enharmonic equivalent to") != -1 or chordName.find("enharmonic to") != -1):
            chordName = chordName.replace("enharmonic to ", "")
            chordName = chordName.replace("enharmonic equivalent to ", "")
            chordName = chordName.replace("above ", "")
            words = chordName.split(" ")
            keyName = words[len(words) - 1]
            words.remove(keyName)
            words.insert(0, keyName + "")
            chordName = " ".join(words)

        chordName = chordName.replace("chord", "")
        chordName = chordName.replace("seventh", "7")
        chordName = chordName.replace("major", "maj")
        chordName = chordName.replace("minor", "min")
        chordName = chordName.replace("diminished", "dim")
        chordName = chordName.replace("augmented", "aug")
        chordName = chordName.replace("half-diminished", "h-dim")
        chordName = chordName.replace("dominant", "dom")
        chordName = chordName.replace("suspended", "sus")
        chordName = chordName.replace("ninth", "9")
        maxCharsPerLine = 15

        if len(chordName) > maxCharsPerLine:
            lines = []
            words = chordName.split(" ")
            while len(words) > 0:
                if len(words[0]) > maxCharsPerLine: # to prevent infinite loop
                    lines.append(words.pop(0))
                else:
                    line = ""
                    while len(words) > 0 and (len(line) + len(words[0]) <= maxCharsPerLine):
                        line += words.pop(0) + " "
                    lines.append(line)
            fontSize = (int) ((self.master.radius * 1.65) / (max([len(line) for line in lines])))
        else:
            lines = [chordName]
            fontSize = (int) ((self.master.radius * 1.65) / (len(chordName)))

        self.chordName = chordName
        text = "\n".join(lines)

        return text, fontSize
