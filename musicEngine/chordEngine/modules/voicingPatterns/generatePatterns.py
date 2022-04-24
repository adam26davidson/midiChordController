from voicingPatternGenerator import VoicingPatternGenerator

MAX_NOTES_LOWER_BOUND = 2
MAX_NOTES_UPPER_BOUND = 12

MAX_VOICE_COUNT_LOWER_BOUND = 2
MAX_VOICE_COUNT_UPPER_BOUND = 16

MAX_OCTAVES_LOWER_BOUND = 2
MAX_OCTAVES_UPPER_BOUND = 8


def getInput(message, min, max):
    value = int(input(message))
    value = validateInput(value, min, max)
    return value


def validateInput(value, min, max):
    while (value > max or value < min):
        prompt = "input is out of range (" + min + \
            " - " + max + "). please try again: "
        value = int(input(prompt))
    return value


if __name__ == "__main__":
    maxNotes = getInput("Maximum number distinct notes in chord: ",
                        MAX_NOTES_LOWER_BOUND,
                        MAX_NOTES_UPPER_BOUND)
    maxVoiceCount = getInput("Maximum number voices in chord: ",
                             MAX_VOICE_COUNT_LOWER_BOUND,
                             MAX_VOICE_COUNT_UPPER_BOUND)
    maxOctaves = getInput("Maximum chord spread in octaves: ",
                          MAX_OCTAVES_LOWER_BOUND,
                          MAX_OCTAVES_UPPER_BOUND)
    fileName = input("Output file name: ")
    generator = VoicingPatternGenerator(
        maxNotes, maxVoiceCount, maxOctaves, fileName)
    generator.generateVoicings()
