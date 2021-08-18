from ui.mainView import MainView
import MidiShock


window = tk.Tk()
window.geometry("800x480")
display = Display(master=window)
display.keyboard.playNotes([67, 70])
window.mainloop()