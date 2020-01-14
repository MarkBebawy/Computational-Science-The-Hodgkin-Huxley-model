## "pycx_gui.py"
## Realtime Simulation GUI (originally from PyCX)
##
## Developed by:
## Chun Wong
## email@chunwong.net
##
## Revised by:
## Hiroki Sayama
## sayama@binghamton.edu
##
## Copyright 2012 Chun Wong & Hiroki Sayama
##
## Simulation control & GUI extensions
## Copyright 2013 Przemyslaw Szufel & Bogumil Kaminski
## {pszufe, bkamins}@sgh.waw.pl
##
## Revised by:
## Koen Koning, K.Koning@uva.nl
## Modifications to make the code compatible with the framework of the UvA
## course `Introduction Computational Science', 2014/2015
##      Python 3 support, GUI refinements, improved parameter support
##
## Minor revision by
## Dick van Albada, G.D.vanAlbada@uva.nl
## Added plt.show() to drawModel() to force actual display of the plot
##
## The matplotlib backend will be automatically selected based on your OS when
## this file is first imported. It is therefore important that matplotlib.pyplot
## imported *after* this file. A clean way do to this is to import pyplot
## locally in the draw function of your model only.

import sys

import matplotlib
if sys.platform == 'darwin':
    # On OSX, Both TkAgg and the builtin backend ('MacOSX') usually work.
    # However, the macosx backend seems to have slightly less issues when
    # setting up your Python, so we prefer that one for OSX.
    matplotlib.use('MacOSX')
else:
    matplotlib.use('TkAgg')

import matplotlib.pyplot as plt

try:
    # Python2
    from Tkinter import (Tk, StringVar, Frame, Label, Button, Scale, Entry,
            Canvas, Scrollbar, Text, YES, NO, LEFT, RIGHT, BOTH, TOP, SUNKEN, X,
            Y, W, WORD, NORMAL, DISABLED, HORIZONTAL, END)
except ImportError:
    # Python3
    from tkinter import (Tk, StringVar, Frame, Label, Button, Scale, Entry,
            Canvas, Scrollbar, Text, YES, NO, LEFT, RIGHT, BOTH, TOP, SUNKEN, X,
            Y, W, WORD, NORMAL, DISABLED, HORIZONTAL, END)

class GUI:
    def __init__(self, model, title='HH-model neuron simulation', interval=0, stepSize=1,
            param_gui_names=None):
        self.model = model
        self.titleText = title
        self.timeInterval = interval
        self.stepSize = stepSize
        self.param_gui_names = param_gui_names
        if param_gui_names is None:
            self.param_gui_names = {}
        self.param_entries = {}
        self.statusStr = ""
        self.running = False
        self.modelFigure = None
        self.currentStep = 0

        self.initGUI()

    def initGUI(self):
        #create root window
        self.rootWindow = Tk()
        self.statusText = StringVar(value=self.statusStr)
        self.setStatusStr("Simulation not yet started")

        self.rootWindow.wm_title(self.titleText)
        self.rootWindow.protocol('WM_DELETE_WINDOW', self.quitGUI)
        self.rootWindow.geometry('550x700')
        self.rootWindow.columnconfigure(0, weight=1)
        self.rootWindow.rowconfigure(0, weight=1)

        self.frameSim = Frame(self.rootWindow)

        self.frameSim.pack(expand=YES, fill=BOTH, padx=5, pady=5, side=TOP)
        self.status = Label(self.rootWindow, width=40, height=3, relief=SUNKEN,
                            bd=1, textvariable=self.statusText)
        self.status.pack(side=TOP, fill=X, padx=1, pady=1, expand=NO)

        self.runPauseString = StringVar()
        self.runPauseString.set("Run")
        self.buttonRun = Button(self.frameSim, width=30, height=2,
                                textvariable=self.runPauseString,
                                command=self.runEvent)
        self.buttonRun.pack(side=TOP, padx=5, pady=5)

        self.showHelp(self.buttonRun,
                      "Runs the simulation (or pauses the running simulation)")
        self.buttonStep = Button(self.frameSim, width=30, height=2,
                                 text="Step Once", command=self.stepOnce)
        self.buttonStep.pack(side=TOP, padx=5, pady=5)
        self.showHelp(self.buttonStep, "Steps the simulation only once")
        self.buttonReset = Button(self.frameSim, width=30, height=2,
                                  text="Reset", command=self.resetModel)
        self.buttonReset.pack(side=TOP, padx=5, pady=5)
        self.showHelp(self.buttonReset, "Resets the simulation")

        for param in self.model.params:
            var_text = self.param_gui_names.get(param, param)
            can = Canvas(self.frameSim)
            lab = Label(can, width=25, height=1 + var_text.count('\n'),
                        text=var_text, anchor=W, takefocus=0)
            lab.pack(side='left')
            ent = Entry(can, width=11)
            val = getattr(self.model, param)
            if isinstance(val, bool):
                val = int(val)  # Show 0/1 which can convert back to bool
            ent.insert(0, str(val))
            ent.pack(side='left')
            can.pack(side='top')
            self.param_entries[param] = ent
        if self.param_entries:
            self.buttonSaveParameters = Button(self.frameSim, width=50,
                    height=1, command=self.saveParametersCmd,
                    text="Save parameters to the running model", state=DISABLED)
            self.showHelp(self.buttonSaveParameters,
                    "Saves the parameter values.\n" +
                    "Not all values may take effect on a running model\n" +
                    "A model reset might be required.")
            self.buttonSaveParameters.pack(side='top', padx=5, pady=5)
            self.buttonSaveParametersAndReset = Button(self.frameSim, width=50,
                    height=1, command=self.saveParametersAndResetCmd,
                    text="Save parameters to the model and reset the model")
            self.showHelp(self.buttonSaveParametersAndReset,
                    "Saves the given parameter values and resets the model")
            self.buttonSaveParametersAndReset.pack(side='top', padx=5, pady=5)

        can = Canvas(self.frameSim)
        lab = Label(can, width=25, height=1, text="Step size ", justify=LEFT,
                anchor=W, takefocus=0)
        lab.pack(side='left')
        self.stepScale = Scale(can, from_=1, to=500, resolution=1,
                               command=self.changeStepSize, orient=HORIZONTAL,
                               width=25, length=150)
        self.stepScale.set(self.stepSize)
        self.showHelp(self.stepScale,
                "Skips model redraw during every [n] simulation steps\n" +
                "Results in a faster model run.")
        self.stepScale.pack(side='left')
        can.pack(side='top')

        can = Canvas(self.frameSim)
        lab = Label(can, width=25, height=1,
                    text="Step visualization delay in ms ", justify=LEFT,
                    anchor=W, takefocus=0)
        lab.pack(side='left')
        self.stepDelay = Scale(can, from_=0, to=max(2000, self.timeInterval),
                               resolution=10, command=self.changeStepDelay,
                               orient=HORIZONTAL, width=25, length=150)
        self.stepDelay.set(self.timeInterval)
        self.showHelp(self.stepDelay, "The visualization of each step is " +
                                      "delays by the given number of " +
                                      "milliseconds.")
        self.stepDelay.pack(side='left')
        can.pack(side='top')

    def setStatusStr(self, newStatus):
        self.statusStr = newStatus
        self.statusText.set(self.statusStr)

    #model control functions
    def changeStepSize(self, val):
        self.stepSize = int(val)

    def changeStepDelay(self, val):
        self.timeInterval = int(val)

    def saveParametersCmd(self):
        for param, entry in self.param_entries.items():
            val = entry.get()
            if isinstance(getattr(self.model, param), bool):
                val = bool(int(val))
            setattr(self.model, param, val)
            # See if the model changed the value (e.g. clipping)
            new_val = getattr(self.model, param)
            if isinstance(new_val, bool):
                new_val = int(new_val)
            entry.delete(0, END)
            entry.insert(0, str(new_val))
        self.setStatusStr("New parameter values have been set")

    def saveParametersAndResetCmd(self):
        self.saveParametersCmd()
        self.resetModel()

    def runEvent(self):
        if not self.running:
            self.running = True
            self.rootWindow.after(self.timeInterval, self.stepModel)
            self.runPauseString.set("Pause")
            self.buttonStep.configure(state=DISABLED)
            if self.param_entries:
                self.buttonSaveParameters.configure(state=NORMAL)
                self.buttonSaveParametersAndReset.configure(state=DISABLED)
        else:
            self.stopRunning()

    def stopRunning(self):
        self.running = False
        self.runPauseString.set("Continue Run")
        self.buttonStep.configure(state=NORMAL)
        self.drawModel()
        if self.param_entries:
            self.buttonSaveParameters.configure(state=NORMAL)
            self.buttonSaveParametersAndReset.configure(state=NORMAL)

    def stepModel(self):
        if self.running:
            if self.model.step() is True:
                self.stopRunning()
            self.currentStep += 1
            self.setStatusStr("Step " + str(self.currentStep))
            self.status.configure(foreground='black')
            if (self.currentStep) % self.stepSize == 0:
                self.drawModel()
            self.rootWindow.after(int(self.timeInterval * 1.0 / self.stepSize),
                                  self.stepModel)

    def stepOnce(self):
        self.running = False
        self.runPauseString.set("Continue Run")
        self.model.step()
        self.currentStep += 1
        self.setStatusStr("Step " + str(self.currentStep))
        self.drawModel()
        if self.param_entries:
            self.buttonSaveParameters.configure(state=NORMAL)

    def resetModel(self):
        self.running = False
        self.runPauseString.set("Run")
        self.model.reset()
        self.currentStep = 0
        self.setStatusStr("Model has been reset")
        self.drawModel()

    def drawModel(self):
        if self.modelFigure is None:
            self.modelFigure = plt.figure()
            plt.ion()
        # plt.show() will cause the plot to be actually displayed
            plt.show()
        self.model.draw()

        # Tell matplotlib to redraw too. The darwin-version works with more
        # types of matplotlib backends, but seems to fail on some Linux
        # machines. Hence we use the TkAgg specific method when available.

        if sys.platform == 'darwin':
            self.modelFigure.canvas.manager.show()
        else:
            self.modelFigure.canvas.manager.window.update()

    def start(self):
        if self.model.step.__doc__:
            self.showHelp(self.buttonStep, self.model.step.__doc__.strip())

        self.model.reset()
        self.drawModel()
        self.rootWindow.mainloop()

    def quitGUI(self):
        plt.close('all')
        self.rootWindow.quit()
        self.rootWindow.destroy()

    def showHelp(self, widget, text):
        def setText(self):
            self.statusText.set(text)
            self.status.configure(foreground='blue')

        def showHelpLeave(self):
            self.statusText.set(self.statusStr)
            self.status.configure(foreground='black')
        widget.bind("<Enter>", lambda e: setText(self))
        widget.bind("<Leave>", lambda e: showHelpLeave(self))
