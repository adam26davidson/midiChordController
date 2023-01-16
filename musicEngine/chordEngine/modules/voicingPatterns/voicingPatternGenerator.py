import json
import itertools
import copy


class VoicingPatternGenerator:

    def __init__(self, maxNotes, maxVoiceCount, maxOctaves, fileName):
        self.voicingPatterns = {}
        self.maxNotes = maxNotes
        self.maxVoiceCount = maxVoiceCount
        self.maxOctaves = maxOctaves
        self.fileName = fileName

    def generateVoicings(self):
        for n in range(2, self.maxNotes + 1):
            print("generating voicings for chords with "
                  + str(n) + " notes")
            vps = {}
            for voiceCount in range(2, self.maxVoiceCount + 1):
                vcps = [[]]
                for degree in range(0, voiceCount):
                    vcps[0].append(degree)
                maxSpread = None
                voicingsFinder = None
                if voiceCount < n:
                    maxSpread = ((n-1) * self.maxOctaves) + (n - voiceCount)
                    voicingsFinder = self.__generateSmallVoicings
                elif voiceCount == n:
                    maxSpread = (n-1) * self.maxOctaves
                    voicingsFinder = self.__generateNormalVoicings
                elif voiceCount > n:
                    maxSpread = (n*self.maxOctaves + 1) - (voiceCount - n)
                    voicingsFinder = self.__generateBigVoicings
                for spread in range(1, maxSpread + 1):
                    vcps.append(voicingsFinder(n, voiceCount, spread))
                vps[voiceCount] = vcps
            self.voicingPatterns[n] = vps
        self.__writeFile()

    def __generateSmallVoicings(self, n, voiceCount, spread):
        topVoice, topOctave = self.__getTopVoice(spread, n, voiceCount)
        voicingChoices = self.__findChoices(topVoice, topOctave, n)
        allVoicings = self.__findSmallVoicings(
            voicingChoices, voiceCount, topVoice, n)
        return self.__findBestVoicing(allVoicings, n)

    def __generateNormalVoicings(self, n, voiceCount, spread):
        topVoice, topOctave = self.__getTopVoice(spread, n, voiceCount)
        voicingChoices = self.__findChoices(topVoice, topOctave, n)
        allVoicings = self.__findVoicings(voicingChoices)
        return self.__findBestVoicing(allVoicings, n)

    def __generateBigVoicings(self, n, voiceCount, spread):
        topVoice, topOctave = self.__getTopVoice(spread, n, voiceCount)
        voicingChoices = self.__findBigChoices(topVoice, topOctave, n)
        allVoicings = self.__findBigVoicings(
            voicingChoices, voiceCount, topVoice, 0)
        allVoicings = self.__processBigVoicings(
            allVoicings, topVoice, topOctave)
        return self.__findBestVoicing(allVoicings, n)

    def __writeFile(self):
        finalObject = {
            "maxNotes": self.maxNotes,
            "maxVoiceCount": self.maxVoiceCount,
            "maxOctaves": self.maxOctaves,
            "voicingPatterns": self.voicingPatterns
        }
        with open(self.fileName, "w") as outfile:
            json.dump(finalObject, outfile)

    def __getTopVoice(self, spread, n, voiceCount):
        adjustedSpread = spread - (n - voiceCount)
        if voiceCount > n:
            topVoice = (adjustedSpread - 1) % n
            topOctave = ((adjustedSpread - 1) // n) + 1
            return topVoice, topOctave
        else:
            topVoice = (adjustedSpread % (n - 1))
            if topVoice == 0:
                topVoice = n - 1
            topOctave = ((adjustedSpread - 1) // (n - 1)) + 1
            return topVoice, topOctave

    def __findVoicings(self, choices):
        voicings = []
        if len(choices) == 1:
            for octave in choices[0]:
                voicings.append([octave])
            return voicings
        else:
            firstVoiceChoices = choices.pop(0)
            subVoicings = self.__findVoicings(choices)
            for octave in firstVoiceChoices:
                for subVoicing in subVoicings:
                    voicings.append([octave] + subVoicing)
            return voicings

    def __findSmallVoicings(self, choices, voiceCount, topVoice, n):
        voicings = []
        innerVoices = []
        for voice in range(1, n):
            if voice != topVoice:
                innerVoices.append(voice)
        numInnerVoices = voiceCount - 2
        combinations = itertools.combinations(innerVoices, numInnerVoices)
        for comb in combinations:
            combChoices = []
            for voice in range(0, n):
                if voice == 0 or voice == topVoice or voice in comb:
                    combChoices.append(choices[voice].copy())
                else:
                    combChoices.append([None])
            voicings = voicings.copy() + self.__findVoicings(combChoices)
        return voicings

    def __processBigVoicings(self, voicings, topVoice, topOctave):
        newVoicings = copy.deepcopy(voicings)
        for voicing in newVoicings:
            voicing[0].append(0)
            voicing[topVoice].append(topOctave)
        return newVoicings

    def __findBigVoicings(self, choices, voiceCount, topVoice, voice):
        if len(choices) > 1:
            voicings = []
            minMultiplicity = voiceCount // len(choices)
            maxMultiplicity = 0
            if (voiceCount % len(choices) == 0):
                maxMultiplicity -= 1
            if (voice == 0):
                minMultiplicity -= 1
                voiceCount -= 1
            if (voice == topVoice):
                minMultiplicity -= 1
                voiceCount -= 1
            maxMultiplicity += minMultiplicity + 1
            if (minMultiplicity < 0):
                minMultiplicity = 0
            for multiplicity in range(minMultiplicity, maxMultiplicity + 1):
                listCombinations = [[]]
                reducedChoices = copy.deepcopy(choices)
                firstChoices = reducedChoices.pop(0)
                if (multiplicity > 0):
                    combinations = itertools.combinations(
                        firstChoices, multiplicity)
                    listCombinations = [list(c) for c in combinations]
                reducedVoiceCount = voiceCount - multiplicity
                subVoicings = self.__findBigVoicings(
                    reducedChoices, reducedVoiceCount, topVoice, voice+1)
                for c in listCombinations:
                    for s in subVoicings:
                        voicings.append([copy.deepcopy(c)] + copy.deepcopy(s))
            return voicings
        else:
            if (voice == 0):
                voiceCount -= 1
            if (voice == topVoice):
                voiceCount -= 1
            if voiceCount == 0:
                return([[[]]])
            combinations = itertools.combinations(choices[0], voiceCount)
            return [[list(c)] for c in combinations]

    def __findBigChoices(self, topVoice, topOctave, n):
        voicingChoices = []
        for voice in range(0, n):
            choices = []
            octave = 0
            while (voice + (octave * n)) < (topVoice + (topOctave * n)):
                if (not (topVoice == voice and octave == topOctave)):
                    choices.append(octave)
                octave += 1
            voicingChoices.append(choices)
        voicingChoices[0].remove(0)
        return voicingChoices

    def __findChoices(self, topVoice, topOctave, n):
        voicingChoices = [[0]]
        for voice in range(1, n):
            if voice != topVoice:
                choices = []
                octave = 0
                while (voice + (octave * n)) < (topVoice + (topOctave * n)):
                    choices.append(octave)
                    octave += 1
                voicingChoices.append(choices)
            else:
                voicingChoices.append([topOctave])
        return voicingChoices

    def __getRealBigVoicingValues(self, voicing, n):
        realVoicing = []
        for voice in range(0, len(voicing)):
            for octave in range(0, len(voicing[voice])):
                if voicing[voice] is not None:
                    realVoicing.append((voice + (voicing[voice][octave] * n)))
        realVoicing.sort()
        return realVoicing

    def __getRealVoicingValues(self, voicing, n):
        if (type(voicing[0]) is list):
            return self.__getRealBigVoicingValues(voicing, n)
        realVoicing = []
        for i in range(0, len(voicing)):
            if voicing[i] is not None:
                realVoicing.append((i + (voicing[i] * n)))
        realVoicing.sort()
        return realVoicing

    def __findBestVoicing(self, voicings, n):
        topVoicing = self.__getRealVoicingValues(voicings[0], n)
        topScore = 0
        for voicing in voicings:
            score = 1
            realVoicing = self.__getRealVoicingValues(voicing, n)
            for i in range(0, len(realVoicing) - 1):
                score = score * (realVoicing[i+1] - realVoicing[i])
            if score > topScore:
                topVoicing = realVoicing
                topScore = score
        return topVoicing
