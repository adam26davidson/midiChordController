# generates all voicing patterns (for all spread values).
# this code is run once to generate voicingpatterns.json
# the main program uses voicingPatterns.json, and this code is not executed.
import json

maxOctaves = 5
maxNotes = 8
voicingPatterns = {}

def getTopVoice(spread, n):
  topVoice = (spread % (n - 1))
  if topVoice == 0:
    topVoice = n - 1 
  topOctave = ((spread - 1) // (n - 1)) + 1
  return topVoice, topOctave

def findVoicings(choices):
  voicings = []
  # if there is only one voice, then return the options for that voice
  if len(choices) == 1:
    for octave in choices[0]:
      voicings.append([octave])
    return voicings
  else:  
    firstVoiceChoices = choices.pop(0)
    subVoicings = findVoicings(choices)
    for octave in firstVoiceChoices:
      for subVoicing in subVoicings:
        voicings.append([octave] + subVoicing)
    return voicings

def findChoices(topVoice, topOctave, spread, n):
  # get all the possible octaves for each middle voice
  voicingChoices = [[0]]
  for voice in range (1, n):
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

def getRealVoicingValues(voicing, n):
  realVoicing = []
  for i in range(0, len(voicing)):
    realVoicing.append((i + (voicing[i] * n)))
  realVoicing.sort()
  return realVoicing

# ranks all voicings of equal spread based on how internally spread out the notes are
# returns the most spread out voicing
def findBestVoicing(voicings, n):
  topVoicing = getRealVoicingValues(voicings[0], n)
  topScore = 0
  for voicing in voicings:
    score = 1
    realVoicing = getRealVoicingValues(voicing, n)
    for i in range(0, len(realVoicing) - 1):
      score = score * (realVoicing[i+1] - realVoicing[i])
    if score > topScore: 
      topVoicing = realVoicing
      topScore = score
  return topVoicing


for n in range(2, maxNotes + 1):
  # for an n length chord find the optimal voicing pattern for each spread value

  #create smallest voicing pattern
  vps = [[]]
  for degree in range(0, n):
    vps[0].append(degree)

  # find 
  for spread in range(1, ((n-1) * maxOctaves) + 1):
    # get the top voice for the voicing pattern
    topVoice, topOctave = getTopVoice(spread, n)
    voicingChoices = findChoices(topVoice, topOctave, spread, n)
    allVoicings = findVoicings(voicingChoices)
    vps.append(findBestVoicing(allVoicings, n))
  
  voicingPatterns[n] = vps

with open("voicingPatterns.json", "w") as outfile:
    json.dump(voicingPatterns, outfile)
  

