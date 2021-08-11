import tkinter as tk

class Keyboard(tk.Canvas):
  width = 726
  height = 40
  blackHeight = 20
  blackColor = "#BDBDBD"
  whiteColor = "#9E9E9E"
  playedColor ="#ffcd38"

  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, bd=0, relief="flat", bg="#000000")
    self.master = master
    self.keys = self.createKeys()
    self.pack(side="bottom")

  def createKeys(self):
    keys = {}

    #Creates count octaves of a specified black key note
    def createBlackKeys(xOffset, midiOffset, count, noteName):
      for i in range(count):
        xL = xOffset + ( i * 14 * 7)
        xR = xL + 8
        yT = 2
        yB = self.blackHeight + 2
        key = {
          "id": self.create_polygon(xL, yT, xL, yB, xR, yB, xR, yT, fill=self.blackColor),
          "color": "black"
          "note": noteName 
        }
        keys[midiOffset + (12 * i)] = key

    #Creates count octaves of a specified white key note
    def createWhiteKeys(xOffset, midiOffset, rNotch, lNotch, count, noteName):
      for i in range(count):
        xL = xOffset + ( i * 14 * 7)
        xR = xL + 12
        xLN = xL + lNotch
        xRN = xR - rNotch
        yN = self.blackHeight + 4
        yT = 2
        yB = self.height - 2
        key = {
          "id": self.create_polygon(xL, yT, xL, yB, xR, yB, xR, yT, fill=self.blackColor),
          "color": "black"
          "note": noteName 
        }
        keys[midiOffset + (12 * i)] = self.create_polygon(xLN, yT, xLN, yN, xL, yN, xL, yB, xR, yB, xR, yN, xRN, yN, xRN, yT, fill=self.whiteColor)

    createBlackKeys(13, 22, 8, "Bb") #Bb0-Bb7
    createBlackKeys(38, 25, 7, "Db") #Db1-Db7
    createBlackKeys(54, 27, 7, "Eb") #Eb1-Eb7
    createBlackKeys(79, 30, 7, "Gb") #Gb1-Gb7
    createBlackKeys(95, 32, 7, "") #Ab1-Ab7

    createWhiteKeys(2, 21, 3, 0, 1) #A0
    createWhiteKeys(16, 23, 0, 7, 8) #B0-B7
    createWhiteKeys(30, 24, 6, 0, 7) #C1-C7
    createWhiteKeys(44, 26, 4, 4, 7) #D1-D7
    createWhiteKeys(58, 28, 0, 6, 7) #E1-E7
    createWhiteKeys(72, 29, 7, 0, 7) #F1-F7
    createWhiteKeys(86, 31, 5, 3, 7) #G1-G7
    createWhiteKeys(100, 33, 3, 5, 7) #A1-A7
    createWhiteKeys(2+(14*51), 108, 0, 0, 1) #C8

    return keys 

  def setScale(self, scale, root):
    for note in scale:
      if

  def playNotes(self, notes):
    for note in notes:
      self.itemconfigure(self.keys[note], fill=self.playedColor)