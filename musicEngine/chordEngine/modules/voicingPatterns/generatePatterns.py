from voicingPatternGenerator import VoicingPatternGenerator

MAX_NOTES_LOWER_BOUND = 2
MAX_NOTES_UPPER_BOUND = 12

MAX_VOICE_COUNT_LOWER_BOUND = 2
MAX_VOICE_COUNT_UPPER_BOUND = 16

MAX_OCTAVES_LOWER_BOUND = 2
MAX_OCTAVES_UPPER_BOUND = 8


def get_input(message, min, max):
    value = int(input(message))
    value = validate_input(value, min, max)
    return value


def validate_input(value, min, max):
    while (value > max or value < min):
        prompt = "input is out of range (" + min + \
            " - " + max + "). please try again: "
        value = int(input(prompt))
    return value


if __name__ == "__main__":
    max_notes = get_input("Maximum number distinct notes in chord: ",
                        MAX_NOTES_LOWER_BOUND,
                        MAX_NOTES_UPPER_BOUND)
    max_voice_count = get_input("Maximum number voices in chord: ",
                             MAX_VOICE_COUNT_LOWER_BOUND,
                             MAX_VOICE_COUNT_UPPER_BOUND)
    max_octaves = get_input("Maximum chord spread in octaves: ",
                          MAX_OCTAVES_LOWER_BOUND,
                          MAX_OCTAVES_UPPER_BOUND)
    file_name = input("Output file name: ")
    generator = VoicingPatternGenerator(
        max_notes, max_voice_count, max_octaves, file_name)
    generator.generate_voicings()
