from constants import MAX_NOTE, MIN_NOTE


# find all octaves of the specified array of notes
def findAllOctavesInRange(notes, min=MIN_NOTE, max=MAX_NOTE):
    completedNotes = []
    midiNotes = []
    for note in notes:
        # ensure no duplicates
        if completedNotes.count(note) == 0:
            for i in range(min, max + 1):
                if i % 12 == note:
                    midiNotes.append(i)
            completedNotes.append(note)
    midiNotes.sort()
    return midiNotes


def findClosestNote(targetNote, sortedNotes):
    upperIndex = 0
    for index in range(len(sortedNotes)):
        if sortedNotes[index] > targetNote:
            upperIndex = index
            break
        if (index == len(sortedNotes) - 1):
            return index
    if (upperIndex == 0):
        return 0
    upperDistance = abs(sortedNotes[upperIndex] - targetNote)
    lowerDistance = abs(sortedNotes[upperIndex - 1] - targetNote)
    if upperDistance < lowerDistance:
        return upperIndex
    return upperIndex - 1
