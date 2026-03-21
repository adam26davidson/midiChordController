import copy
import itertools
import json


class VoicingPatternGenerator:

    def __init__(self, max_notes, max_voice_count, max_octaves, file_name):
        self.voicing_patterns = {}
        self.max_notes = max_notes
        self.max_voice_count = max_voice_count
        self.max_octaves = max_octaves
        self.file_name = file_name

    def generate_voicings(self):
        for n in range(2, self.max_notes + 1):
            print("generating voicings for chords with "
                  + str(n) + " notes")
            vps = {}
            for voice_count in range(2, self.max_voice_count + 1):
                vcps = [[]]
                for degree in range(voice_count):
                    vcps[0].append(degree)
                max_spread: int = 0
                if voice_count < n:
                    max_spread = ((n-1) * self.max_octaves) + (n - voice_count)
                    voicings_finder = self.__generate_small_voicings
                elif voice_count == n:
                    max_spread = (n-1) * self.max_octaves
                    voicings_finder = self.__generate_normal_voicings
                else:  # voice_count > n
                    max_spread = (n*self.max_octaves + 1) - (voice_count - n)
                    voicings_finder = self.__generate_big_voicings
                for spread in range(1, max_spread + 1):
                    vcps.append(voicings_finder(n, voice_count, spread))
                vps[voice_count] = vcps
            self.voicing_patterns[n] = vps
        self.__write_file()

    def __generate_small_voicings(self, n, voice_count, spread):
        top_voice, top_octave = self.__get_top_voice(spread, n, voice_count)
        voicing_choices = self.__find_choices(top_voice, top_octave, n)
        all_voicings = self.__find_small_voicings(
            voicing_choices, voice_count, top_voice, n)
        return self.__find_best_voicing(all_voicings, n)

    def __generate_normal_voicings(self, n, voice_count, spread):
        top_voice, top_octave = self.__get_top_voice(spread, n, voice_count)
        voicing_choices = self.__find_choices(top_voice, top_octave, n)
        all_voicings = self.__find_voicings(voicing_choices)
        return self.__find_best_voicing(all_voicings, n)

    def __generate_big_voicings(self, n, voice_count, spread):
        top_voice, top_octave = self.__get_top_voice(spread, n, voice_count)
        voicing_choices = self.__find_big_choices(top_voice, top_octave, n)
        all_voicings = self.__find_big_voicings(
            voicing_choices, voice_count, top_voice, 0)
        all_voicings = self.__process_big_voicings(
            all_voicings, top_voice, top_octave)
        return self.__find_best_voicing(all_voicings, n)

    def __write_file(self):
        final_object = {
            "maxNotes": self.max_notes,
            "maxVoiceCount": self.max_voice_count,
            "maxOctaves": self.max_octaves,
            "voicingPatterns": self.voicing_patterns
        }
        with open(self.file_name, "w") as outfile:
            json.dump(final_object, outfile)

    def __get_top_voice(self, spread, n, voice_count):
        adjusted_spread = spread - (n - voice_count)
        if voice_count > n:
            top_voice = (adjusted_spread - 1) % n
            top_octave = ((adjusted_spread - 1) // n) + 1
            return top_voice, top_octave
        top_voice = (adjusted_spread % (n - 1))
        if top_voice == 0:
            top_voice = n - 1
        top_octave = ((adjusted_spread - 1) // (n - 1)) + 1
        return top_voice, top_octave

    def __find_voicings(self, choices):
        voicings = []
        if len(choices) == 1:
            for octave in choices[0]:
                voicings.append([octave])
            return voicings
        first_voice_choices = choices.pop(0)
        sub_voicings = self.__find_voicings(choices)
        for octave in first_voice_choices:
            for sub_voicing in sub_voicings:
                voicings.append([octave, *sub_voicing])
        return voicings

    def __find_small_voicings(self, choices, voice_count, top_voice, n):
        voicings = []
        inner_voices = []
        for voice in range(1, n):
            if voice != top_voice:
                inner_voices.append(voice)
        num_inner_voices = voice_count - 2
        combinations = itertools.combinations(inner_voices, num_inner_voices)
        for comb in combinations:
            comb_choices = []
            for voice in range(n):
                if voice == 0 or voice == top_voice or voice in comb:
                    comb_choices.append(choices[voice].copy())
                else:
                    comb_choices.append([None])
            voicings = voicings.copy() + self.__find_voicings(comb_choices)
        return voicings

    def __process_big_voicings(self, voicings, top_voice, top_octave):
        new_voicings = copy.deepcopy(voicings)
        for voicing in new_voicings:
            voicing[0].append(0)
            voicing[top_voice].append(top_octave)
        return new_voicings

    def __find_big_voicings(self, choices, voice_count, top_voice, voice):
        if len(choices) > 1:
            voicings = []
            min_multiplicity = voice_count // len(choices)
            max_multiplicity = 0
            if (voice_count % len(choices) == 0):
                max_multiplicity -= 1
            if (voice == 0):
                min_multiplicity -= 1
                voice_count -= 1
            if (voice == top_voice):
                min_multiplicity -= 1
                voice_count -= 1
            max_multiplicity += min_multiplicity + 1
            if (min_multiplicity < 0):
                min_multiplicity = 0
            for multiplicity in range(min_multiplicity, max_multiplicity + 1):
                list_combinations = [[]]
                reduced_choices = copy.deepcopy(choices)
                first_choices = reduced_choices.pop(0)
                if (multiplicity > 0):
                    combinations = itertools.combinations(
                        first_choices, multiplicity)
                    list_combinations = [list(c) for c in combinations]
                reduced_voice_count = voice_count - multiplicity
                sub_voicings = self.__find_big_voicings(
                    reduced_choices, reduced_voice_count, top_voice, voice+1)
                for c in list_combinations:
                    for s in sub_voicings:
                        voicings.append([copy.deepcopy(c), *copy.deepcopy(s)])
            return voicings
        if (voice == 0):
            voice_count -= 1
        if (voice == top_voice):
            voice_count -= 1
        if voice_count == 0:
            return([[[]]])
        combinations = itertools.combinations(choices[0], voice_count)
        return [[list(c)] for c in combinations]

    def __find_big_choices(self, top_voice, top_octave, n):
        voicing_choices = []
        for voice in range(n):
            choices = []
            octave = 0
            while (voice + (octave * n)) < (top_voice + (top_octave * n)):
                if (not (top_voice == voice and octave == top_octave)):
                    choices.append(octave)
                octave += 1
            voicing_choices.append(choices)
        voicing_choices[0].remove(0)
        return voicing_choices

    def __find_choices(self, top_voice, top_octave, n):
        voicing_choices = [[0]]
        for voice in range(1, n):
            if voice != top_voice:
                choices = []
                octave = 0
                while (voice + (octave * n)) < (top_voice + (top_octave * n)):
                    choices.append(octave)
                    octave += 1
                voicing_choices.append(choices)
            else:
                voicing_choices.append([top_octave])
        return voicing_choices

    def __get_real_big_voicing_values(self, voicing, n):
        real_voicing = []
        for voice in range(len(voicing)):
            for octave in range(len(voicing[voice])):
                if voicing[voice] is not None:
                    real_voicing.append(voice + (voicing[voice][octave] * n))
        real_voicing.sort()
        return real_voicing

    def __get_real_voicing_values(self, voicing, n):
        if (type(voicing[0]) is list):
            return self.__get_real_big_voicing_values(voicing, n)
        real_voicing = []
        for i in range(len(voicing)):
            if voicing[i] is not None:
                real_voicing.append(i + (voicing[i] * n))
        real_voicing.sort()
        return real_voicing

    def __find_best_voicing(self, voicings, n):
        top_voicing = self.__get_real_voicing_values(voicings[0], n)
        top_score = 0
        for voicing in voicings:
            score = 1
            real_voicing = self.__get_real_voicing_values(voicing, n)
            for i in range(len(real_voicing) - 1):
                score = score * (real_voicing[i+1] - real_voicing[i])
            if score > top_score:
                top_voicing = real_voicing
                top_score = score
        return top_voicing
