README
# MidiChordController

MidiChordController is a Python GUI application that generates MIDI chords based on game controller input.  The application is designed to run on a Raspberry Pi with a Pimoroni HyperPixel 800 x 480 pixel display.

## Installation

To install, clone the git repository, and install the dependencies:

```bash
git clone https://github.com/adam26davidson/midiChordController.git
pip install -r midiChordController/requirements.txt
```

## Running the application

To run the application, connect a supported controller via USB or bluetooth to the raspberry pi, hook up a midi connection via USB, then navigate into the MidiChordController directory and run the launch script.  Different flags should be provided to the script based on your setup:

### With Hyperpixel 800x480 px display

```bash
cd MidiChordController
python3 main.py
```

### On another display

```bash
cd MidiChordController
python3 main.py --window
```

### On a headless Pi with no UI

```bash
cd MidiChordController
python3 main.py --no-display
```

## Writing Settings

settings.json holds an array of presets for the controller.  Each preset contains the following properties:

- ```"name" : String```
- ```"scale": Array``` 
- ```"modulations" : Object```
- ```"chords" : Object```
- ```"secondaries" : Object```

**note on terminology**: The term "key" will be used to mean the starting note of a given scale, not specifically the major scale starting on that note. 

Here is how to specify each of these preset components in detail:

### Name

This can be any string but should be pretty short to fit in the display 
```JSON
{
	"name": "New Setting"
}
```
### Scale

The primary scale dictates the notes which can be used to make up the four chords specified in the ```"chords"``` object. 

The scale is provided as a list of numbers between 0 and 11.  The numbers provided represent semitone values from the current key.  The actual notes that will be in the scale depend on the key (which can be changed freely at runtime) in combination with the provided scale. 

Here are some examples of scales and their interpretations in particular keys:

major scale:
```JSON
"scale":  [0, 2, 4, 5, 7, 9, 11] 
```

In the key of D this would mean the notes D, E, F#, G, A, B, and C# would be in the scale

major pentatonic scale:
```JSON
"scale": [0, 2, 4, 7, 9]
```
in the key of G# this would mean the notes G#, A#, B, D#, and F

If you would like to construct chords outside the bounds of a scale the chromatic scale can be used:
```JSON
"scale": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
```

Here are the interval translations of semitone values for reference:

| semitone value | musical interval |
| -------------- | ---------------- |
| 0 | current key |
| 1 | minor second |
| 2 | major second |
| 3 | minor third |
| 4 | major third |
| 5	| perfect fourth |
| 6	| tritone |
| 7	| perfect fifth |
| 8	| minor sixth |
| 9	| major sixth |
| 10 | minor seventh |
| 11 |  major seventh |

### Chords

```JSON
"chords": {
	"south": {
		"root": 0,
		"main": [0, 2, 4, 6],
		"mainBass": [0, 4],
		"alternate": [1, 2, 4, 6],
		"alternateBass": [0, 1, 4],
	},
	"west": {},
	"north": {},
	"east": {}
}
```
Four diatonic chords are specified within the chord property. Diatonic means that each of these chords is made of notes in the preset scale.  

The ```"chords"``` object has four properties ```"south"```, ```"west"```, ```"north"```, and ```"east"``` which correspond to the main button positions on a standard gamepad where each of the chords will be triggered.  

Each of the ```"south"```,  ```"west"```, ```"north"```, and ```"east"``` chords are specified in the same way, and contain the following properties: ```"root"```, ```"main"```, ```"mainBass"```, ```"alternate"```, and ```"alternateBass"```

```"root"```: 
The root note of the chord, specified as a note index in the original scale.  With a major scale and key of C, root: 0 would mean the root of the chord is C, and root: 3 would mean the root of the chord is F

```"main"```:
An array of numbers representing the notes in the chord.  Each number is the number of scale degrees from the root of the chord.  For example, using a major scale in the key of C, and ```"root": 3```,  ```"main": [0, 2, 3]``` would mean the chord is made up of F, A, and C.  Each number provided must be less than the number of notes in the preset scale, and greater than or equal to zero.

```"mainBass"```:
An array of numbers representing the bass notes that can be played. These notes are specified in the same way as the chord notes in ```"main"```.  For example, using a major scale in the key of C, and ```"root": 1```, ```"mainBass": [0, 4]``` would mean the bass will play either D or A.

```"alternate"```:
Specifies an alternate voicing of the chord.  Provide an array in the same way as for "main" and "bass" (preferably a different array from "main", since this is supposed to be a different version of the chord)

```"alternateBass"```:
Specifies an alternate set of notes to use as bass notes for the alternate chord.  Provide an array in the same way as for "main" and "bass" 

***note**: it is possible to use ```"alternate"``` and ```"alternateBass"``` to make a completely different chord rather than providing an alternate version of the main chord.  That is also a valid way to use these properties.  

### Modulations 
```JSON
"modulations": {
	"left": {
		"type": "modal",
		"map": [0, 5]
	},
	"right": {
		"type": "custom",
		"map": [0, 10, 8, 7, 5, 3, 1]
	}
}
```
A modulation allows you to modulate from one scale or mode to another parallel scale. Each note in the original scale is mapped to a new note.  When a modulation is activated, the notes in the chords will be shifted from the original scale to new notes as specified by the modulation map

Two modulations can be specified, labelled ```"left"``` and ```"right"```.  Each of these modulation objects is specified in the same way. 

Each modulation has two properties: ```"type"```, and ```"map"```. ```"type"``` can be set to either ```"modal"``` or ```"custom"```, and indicates how the value of the ```"map"``` property should be interpreted.

#### Custom Modulation

```JSON
"type": "custom"
```
When ```"type"``` is set to ```"custom"```, the map must be an array of integers of the same length as ```"scale"```.  The array represents a map from one scale to another.  

For example, to map from a major scale to a minor scale:

top level ```"scale"``` property:
```JSON
"scale": 	[0, 2, 4, 5, 7, 9, 11]
```
```"map"``` property within right or left modulation:
```JSON
"map": [0, 2, 3, 5, 7, 8, 10]
```

Every scale index is fixed except for 4, 9, and 11, (major third, major sixth, and major seventh) which are mapped to their minor scale counterparts, 3, 8, and 10 (minor third, minor sixth, and minor seventh).

It is also possible to map to scales with fewer notes than the preset scale, but some notes in the preset scale must be mapped to the same notes in the modulation scale.  For example, to map from a seven note scale to a whole tone scale, ```[0, 0, 2, 4, 6, 8, 10]``` would be one of many possible maps between the scales.

Notes can also be scrambled to different positions in a custom map.  For example with a major scale, the map ```[0, 4, 7, 2, 11, 5, 9]``` maps to the same scale, but rearranges the notes.  

As another example, a transpose for a major scale would look like this : ```[0, 10, 8, 7, 5, 3, 1] ```

#### Modal Modulation

```JSON
"type": "modal"
```

Setting type to modal is a quicker way to specify maps when the modulation is a modal interchange.  

The provided map should be an array of two integers. Both numbers represent  zero indexed scale degrees in the preset scale.  For instance the number 0 represents the first note in the scale, and 5 represents the sixth note in the scale.
  
A map [a, b] is interpreted as: "switch mode b to mode a", or alternatively, shift all the notes in the scale so that the scale starting on note index b is mode a.  

**note*** "mode a" refers to the mode resulting from starting on note index "a" and using all of the notes in the preset scale

**Examples** Let's say that a major scale is being used. Then here is the interpretations of some possible maps:

```JSON
"map": [5, 0] 
```
Make mode 0 (the major mode) become mode 5 (minor scale).  This would result in the scale changing from major to minor.  

In the key of C: 

"Shift all of the notes in the scale so that that the scale starting on C (note index 0) is a minor (mode 5)"

(C -> C), (D -> D), (E -> Eb), (F -> F), (G -> G), (A -> Ab), (B -> Bb)

---

```JSON
"map": [0, 5] 
```

Make mode 5 (minor mode) become mode 0 (major scale).  This would result in the minor mode within the scale becoming a major mode.

In the key of C:

"Shift all of the notes in the scale so that that the scale starting on A (note index 5) is a major (mode 0)"

(C -> C#), (D -> D), (E -> E), (F -> F#), (G -> G#), (A -> A), (B -> B)
	
---

```JSON
"map": [1, 3] 
```

Make mode 3 (lydian mode) become mode 1 (dorian mode).  This would result in the lydian mode within the scale being shifted to a dorian scale.

In the key of C:

 Shift all of the notes in the scale so that that the scale starting on F (note index 3) is dorian (mode 1)
 
(C -> C), (D -> D), (E -> Eb), (F -> F), (G -> G), (A -> Ab), (B -> Bb)

---

Many modal maps are equivalent.  For example for maps [a, b] and [c, d], if the interval between a and b in the preset scale is the same as the interval between c and d, then the two modulations will be equivalent.  For example, using a major scale, [0, 1] and [1, 2] would be equivalent, since stepping from the first note to the second note in the major scale is a whole step, and so is stepping from the second note to the third note.

### Secondaries

```JSON
"secondaries": {
	"left": {
		"interval": 7,
		"main": [0, 4, 7, 10],
		"mainBass": [0, 7],
		"alternate": [2, 4, 7, 10],
		"alternateBass": [0, 7]
	}, 
	"right": {}
}
```
This object provides a way to specify "secondary" chords to whatever chord is being played.  A set chord is provided chromatically and that chord is played at a specified interval above the root note of whatever diatonic chord (chord specified in the chords object) is played.  

We will call "whatever diatonic chord is being played" the "target chord" in the rest of this section

The initial intent of these chords was to be able to provide leading chords to each of the four diatonic chords, but the specification is flexible enough for these chords to be used in a many ways! 

Like the modulations, two secondaries can be provided under the properties ```"right"```, and ```"left"```.  Each of these properties holds a secondary object which is specified with the keys: ```"interval"```, ```"main"```, ```"mainBass"```, ```"alternate"```, ```"alternateBass"```, as well as some override objects which will be explained at the end of the section.  These properties basically mirror the properties in each chord in the chords object, with the key difference that all notes and intervals are specified in semitones rather than scale degrees

*```"interval"```*:  The interval above the root note of the target chord where the root of the secondary chord will be. For example, ```"interval": 7``` would mean that the root of the secondary will be a perfect fifth above the root of the target chord

*```"main"```* : An array of numbers representing the notes in the chord.  Each number is the number of semitones from the root of the chord.  For example, ```"main": [0, 4, 7, 10]``` would mean that the chord is composed of the root, a major 4th, a perfect fifth, and a minor seventh, making this a dominant seventh chord. (refer to the interval table in the scale section for semitone to interval conversion)

*```"mainBass"```*: An array of numbers representing the bass notes that can be played. These notes are specified in the same way as the chord notes in ```"main".```  For example, ```"mainBass": [0, 7, 10]``` would mean the bass will play the root, the perfect fifth and the minor seventh

*```"alternate"```*: Specifies an alternate voicing of the chord.  Provide an array in the same way as for ```"main"``` and ```"mainBass"```

*```"alternateBass"```*: Specifies an alternate set of notes to use as bass notes for the alternate chord.  Provide an array in the same way as for ```"main"``` and ```"mainBass"```

**Secondary Overrides** (optional)

The five properties listed above represent the default secondary chord behavior when no overrides are detected.  Overrides can be provided for each of the four possible target chords (south, west, north, and east) in order to have custom secondary behavior for each chord.  

**note*** The reason for including overrides for each chord is that sometimes for the same secondary chord, a different version leads better to the target chord based on what the target chord is. One example of this is that when adding a nine to a secondary dominant chord, a major 2 (whole step) away from the root sounds better leading to a major chord while a minor 2 sounds better when leading to a minor chord (this is due to the fact that the V chord in a harmonic minor scale contains a b9).

To specify an override for the south chord, add the chord name as an additional key to the ```"secondaries"``` object (eg, ```"south": {...}```). 

Within that object, three possible keys can be provided: ```"default"``` ```"leftModulation"```, and ```"rightModulation"```, each of which would be set to an object containing the overrides to the five main properties.  

```"default"``` is the override that will be used for the chord when no modulation is being applied, while ```"leftModulation"``` and ```"rightModulation"``` will be used when the respective modulations are in effect.  Within each of these objects any of the five main secondary properties can be set to override values. 

Only the necessary information needs to be provided.  For example, the following would only customize the alternate chord and bass for the south chord when no modulation is active:
```JSON
"south": {
	"default": {
		"alternate": [1, 4, 7, 10],
		"alternateBass": [0, 1, 7]
	}
} 
```

The following would set an override of all five properties for the north chord when the left modulation is in effect, and just override the main bass when there is no modulation happening:

```JSON
"north": {
	"leftModulation":{
		"interval": 1, 
		"main": [0, 4, 7, 10],
		"mainBass": [0, 7],
		"alternate": [1, 4, 7, 10],
		"alternateBass": [0, 7]
	},
	"default": {
		"mainBass": [0, 2, 7]
	}
}
```

It is possible to specify up to 12 (4 chords x 3 modulation states) completely different secondaries with overrides.  Counting the fact that alternates have the option of being entirely different chords that doubles the number to 24!
