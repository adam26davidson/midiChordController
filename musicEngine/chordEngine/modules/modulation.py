class Modulation():

    def __init__(self, scale, setting):
        self.scale = scale
        if setting["type"] == "modal":
            self.map = self.findModalMap(setting["map"])
        else:
            self.map = setting["map"]
        self.offsets = self.findOffsets()

    def findModalMap(self, map):
        scalePattern = []  # will be something like [T,F,T,F,T,T,F,T,F,T,F,T]
        for i in range(0, 12):
            if (self.scale.count(i) == 0):
                scalePattern.append(False)
            else:
                scalePattern.append(True)
        cycles = ((self.scale[map[0]] - self.scale[map[1]]) + 12) % 12
        for c in range(0, cycles):
            val = scalePattern.pop(0)
            scalePattern.append(val)
        explicitMap = []
        for i in range(0, 12):
            if scalePattern[i]:
                explicitMap.append(i)
        return explicitMap

    def findOffsets(self):
        offsets = []
        for i in range(0, len(self.scale)):
            offsets.append(self.map[i] - self.scale[i])
        return offsets

    def apply(self, notes, scale):
        modNotes = []
        for note in notes:
            modNotes.append(self.applyOne(note, scale))
        return modNotes

    def applyOne(self, note, scale):
        index = scale.index(note % 12)
        return note + self.offsets[index]

    def applyToScale(self):
        newScale = []
        for i in range(0, len(self.scale)):
            newScale.append((self.scale[i] + self.offsets[i]) % 12)
        return newScale
