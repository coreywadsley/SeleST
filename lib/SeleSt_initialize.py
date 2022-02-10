"""
Selective Stopping (SeleSt) task

    SeleSt_initialize
        Information that can change from session to session is initialized in this script
        
    See the SeleSt.py script for general information on the task
"""

# Import required modules
import os
from psychopy import visual, core, gui, data
from psychopy.hardware import keyboard
import serial
import numpy as np
import array

# Create Experiment class
#   Contains both general and advanced settings in dictionaries that are presented in GUIs.
#   A tool tip for each option is accessible by hovering the mouse over the input area.
#   You can make changes to the default values by altering the code below, or by creating a specific Experiment class
#   that is called in SeleSt.py, e.g., Experiment_debug.
class Experiment():
    def __init__(self,_thisDir):
        
        # Create dictionary with general task settings
        self.genSettings= {'Experiment name': 'x', # included in filename
            'Participant ID':0000, # included in filename
            'Age (Years)':00,
            'Sex':['-', 'F', 'M', 'Prefer not to say'],
            'Monitor name': 'testMonitor', # name of monitor (see https://www.psychopy.org/builder/builderMonitors.html for more info)
            'Full-screen?': True,
            'Use response box?': False, # option to enable external response box
            'Feedback?' : True, # option to present trial-by-trial feedback
            'Practice trials?': True,
            'n practice go trials': 36,
            'Import trials?': False, # option to import trials
            'File path': _thisDir, # file path for imported trials file
            'File name': 'trials_1.xlsx', # name of file to import
            'Save data?': True,
            'Paradigm': ['ARI','SST'], # select paradigm type to use (NOTE: can change the default option by switching order in the list)
            'n go trials per block': 24,
            'n stop-both trials per block': 4,
            'n stop-left trials per block': 4,
            'n stop-right trials per block': 4,
            'n blocks': 12, # number of blocks to repeat the above trial arrangement over
            'Change advanced settings?':False # option to change advanced settings via GUI
            }
        
        # Create GUI for expInfo dictionary w/ tool tips
        dlg=gui.DlgFromDict(dictionary=self.genSettings, title='SeleSt (general settings)',
            order = ('Experiment name', 'Participant ID', 'Age (Years)', 'Sex', 'Monitor name', 'Full-screen?', 'Use response box?', 'Import trials?', 'File path', 'File name', 'Save data?', 'Practice trials?', 'n practice go trials', 'n go trials per block', 'n stop-both trials per block', 'n stop-left trials per block', 'n stop-right trials per block','n blocks', 'Feedback?','Change advanced settings?'),
            tip={'Experiment name': 'Input name of experiment which will included in data file',
                 'Monitor name': 'Input name of the monitor being used to present the task (see Monitor Centre for more info)',
                 'Full-screen?': 'Select this if you would like to run the task in full-screen mode (recommended for data collection)',
                 'Feedback?': 'Deselect this feature if you do not wish to present trial-by-trial and end-of-block feedback',
                 'Practice trials?': 'Select this if you wish to run through a practice block of go trials',
                 'Import trials?': 'Select this if you are using the trials.xlsx file (NOTE: this will override randomisation)',
                 'n blocks': 'Set the number of blocks to repeat the trials across (NOTE: if importing trials the number of trials will be divided by n blocks; e.g., 100 trials, 10 blocks = 10 blocks x 10 trials)',
                 'Change advanced settings?': 'Select this if you would like to change any of the advanced settings (e.g. target time, target color, step size)'})
        if dlg.OK ==False: core.quit() # user pressed cancel
        self.genSettings['date'] = data.getDateStr() # add timestamp (will be included in data filename)

        # Create dictionary with advanced task settings (default settings dependent on paradigm)
        if self.genSettings['Paradigm'] == 'ARI':
            Defaults = {'Target time (ms)': 800, 'Trial length (s)': 1.5, 'Fixed delay length (s)': 0.5, 'Stop-both time (ms)': 600, 'Stop-left time (ms)': 550, 'Stop-right time (ms)': 550, 'Lower stop-limit (ms)': 150, 'Upper stop-limit (ms)': 50, 'Positional stop signal': True, 'Target position': 0.8, 'Stimulus size (cm)': 15}
        elif self.genSettings['Paradigm'] == 'SST':
            Defaults = {'Target time (ms)': 300, 'Trial length (s)': 1.5, 'Fixed delay length (s)': 1, 'Stop-both time (ms)': 300, 'Stop-left time (ms)': 250, 'Stop-right time (ms)': 250, 'Lower stop-limit (ms)': 150, 'Upper stop-limit (ms)': 50, 'Positional stop signal': False, 'Target position': 0.8, 'Stimulus size (cm)': 5}
        self.advSettings={'Send serial trigger at trial onset?': False, # option to send trigger via serial port at trial onset
            'Hold-and-release': False, # option for trials to be initiated by holding down the response keys
            'Left response key': 'left',
            'Right response key': 'right',
            'Target time (ms)': Defaults['Target time (ms)'], # target RT for go trials
            'Trial length (s)': Defaults['Trial length (s)'],
            'Intertrial interval (s)': 1.5,
            'Fixed rise delay?' : False, # if false a variable rise delay will be used (ARI: 500 - 1000 ms, SST: 1000 - 2000 ms)
            'Fixed delay length (s)': Defaults['Fixed delay length (s)'],
            'n forced go trials': 1, # start each block with x minimum go trials
            'Staircase stop-signal delays?' : True,
            'Stop-signal delay step-size (ms)': 50,
            'Stop-both time (ms)': Defaults['Stop-both time (ms)'],
            'Stop-left time (ms)': Defaults['Stop-left time (ms)'],
            'Stop-right time (ms)': Defaults['Stop-right time (ms)'],
            'Lower stop-limit (ms)': Defaults['Lower stop-limit (ms)'],
            'Upper stop-limit (ms)': Defaults['Upper stop-limit (ms)'],
            'Positional stop signal': Defaults['Positional stop signal'],
            'Stimulus size (cm)': Defaults['Stimulus size (cm)'],
            'Target position': Defaults['Target position'],
            'Cue color': 'black',
            'Go color': 'black',
            'Stop color': 'cyan',
            'Background color': 'grey'}
        
        # Create GUI for advExpInfo dictionary if advanced option was selected
        if self.genSettings['Change advanced settings?']:
            dlg=gui.DlgFromDict(dictionary=self.advSettings, title='SeleSt (Advanced settings)',
                order = ('Send serial trigger at trial onset?', 'Hold-and-release', 'Left response key', 'Right response key', 'Target time (ms)', 'Trial length (s)', 'Intertrial interval (s)', 'Fixed rise delay?', 'Fixed delay length (s)', 'n forced go trials', 'Staircase stop-signal delays?', 'Stop-signal delay step-size (ms)', 'Stop-both time (ms)', 'Stop-left time (ms)', 'Stop-right time (ms)', 'Lower stop-limit (ms)', 'Upper stop-limit (ms)', 'Positional stop signal', 'Target position', 'Stimulus size (cm)', 'Background color', 'Cue color', 'Go color', 'Stop color'),
                tip={'Send serial trigger at trial onset?': 'Select this if you would like to send a trigger at trial onset (NOTE: a serial device must be set up for this to work)',
                     'Hold-and-release': 'Determines if trials automatically cycle (wait-and-press) or wait for response keys to be pressed (hold-and-release)',
                     'Target time (ms)': 'Input the desired target response time (NOTE: keep in mind that trial length needs to be adjusted to allow for complete filling if target time is extended too far)',
                     'Trial length (s)': 'Input desired trial length (NOTE FOR ARI: this should be at least the length of total time it takes for both bars to fill)',
                     'Intertrial interval (s)': 'Input the desired intertrial interval (ITI)',
                     'Fixed rise delay?': 'If selected, each trial will begin with a fixed rise delay (length below). If unselected, each trial will begin with a variable rise delay (ARI: 500 - 1000 ms, SST: 1000 - 2000 ms).',
                     'Fixed delay length (s)': 'Length of fixed delay (if selected) you would like to use at the start of each trial',
                     'n forced go trials': 'Input the number of go trials you would like to force at the start of each block',
                     'Staircase stop-signal delays?': 'Select if you would like to use a fixed or staircased stop-signal delay',
                     'Lower stop-limit (ms)': 'Time relative to trial onset that the bars should not stop before',
                     'Upper stop-limit (ms)': 'Time relative to target time that the bars should not stop after (e.g. 800 ms target, 150 ms upper stop-limit = 650 ms stopping limit)',
                     'Positional stop signal': 'ARI ONLY: Present stop signal as cessation of rising bars, if not, change color of filling bar',
                     'Stimulus size (cm)': 'Size of the left and right stimuli (ARI = height of bars, SST = height of triangles)',
                     'Target position': 'ARI ONLY: Input where you would like the target lines to be positioned as proportion of total bar height (e.g. 0.8 equates to 80% of bar height/filling time)',
                     'Cue color': 'Input name of desired color of the cue (ARI = target lines, SST = triangle outline)',
                     'Go color': 'Input name of desired color of the go signal (ARI = filling bar, SST = triangle filling)',
                     'Stop color': 'Input name of desired color of the stop signal (ARI = bar filling, SST = triangle filling)',
                     'Background color': 'Input name of desired color of the background (for list of possible colors see https://www.w3schools.com/Colors/colors_names.asp )'})
        if dlg.OK==False: core.quit()
        
        # Set up the window in which we will present stimuli
        self.win = visual.Window(
            fullscr=self.genSettings['Full-screen?'],
            winType='pyglet',
            monitor=self.genSettings['Monitor name'],
            color=self.advSettings['Background color'],
            blendMode='avg',
            allowGUI=False,
            units = 'cm')
        
        # Measure the monitors refresh rate
        self.genSettings['frameRate'] = self.win.getActualFrameRate()
        self.frameRate = self.genSettings['frameRate']
        if self.frameRate != None:
            self.frameDur = 1.0 / round(self.frameRate) * 1000
        else:
            self.frameDur = 1.0 / 60.0 * 1000 # could not measure, so guess
        print('Monitor frame rate is %s Hz' %(round(self.genSettings['frameRate'],0))) # print out useful info on frame rate & duration for the interested user
        print('Frame duration is %s ms' %round(self.frameDur,1))        
        
        # Here you can implement code to operate an external response box. 
        # The keyboard will be used if no response box is selected.
        if self.genSettings['Use response box?'] == True:
            # e.g.
            #self.rb = buttonbox.Buttonbox()    # example buttonbox from RuSocSci
            #self.L_resp_key = 'E'
            #self.R_resp_key = 'A'
            if self.advSettings['Hold-and-release'] == True:
                pass
            pass
        else:
            self.rb = keyboard.Keyboard()  # use input rom keyboard
            self.L_resp_key = self.advSettings['Left response key']
            self.R_resp_key = self.advSettings['Right response key']        
            
        
        # Here you can set up a serial device (e.g. to send trigger at trial onset)
        if self.advSettings['Send serial trigger at trial onset?'] == True:    
            # e.g.
            #self.ser = serial.Serial('COM8', 9600, timeout=0)
            #line = ser.readline()
            pass

        # Create clocks to monitor trial duration and trial times
        self.globalClock = core.Clock() # to track total time of experiment
        self.trialClock = core.Clock() # to track time on a trial-by-trial basis
        self.holdClock = core.Clock() # to track press time when waiting for key press in hold and release

        # Check if a "data" folder exists in this directory, and make one if not.
        if not os.path.exists(_thisDir + os.sep +'data/'):
            print('Data folder did not exist, making one in current directory')
            os.makedirs(_thisDir + os.sep +'data/')
        
        # Create the name of the output file. "Output" is the output file.
        if self.genSettings['Save data?'] == True:
            self.Output = _thisDir + os.sep + u'data/SelARI_%s_%s_%s' % (self.genSettings['Participant ID'],
                self.genSettings['Experiment name'], self.genSettings['date'])
            with open(self.Output+'.txt', 'a') as b:
                b.write('block trial startTime trialName trialType stopTime L_press R_press L_targetTime R_targetTime L_RT R_RT\n')
                
        if self.genSettings['Paradigm'] == 'ARI':
            self.instructions.instr_1_go = visual.ImageStim(self.win, image=_thisDir+'/instructions/instr-1-go.png')
            self.instructions.instr_2_points = visual.ImageStim(self.win, image=_thisDir+'/instructions/instr-2-points.png')
            self.instructions.instr_3_stop = visual.ImageStim(self.win, image=_thisDir+'/instructions/instr-3-stop.png')
            self.instructions.instr_4_task = visual.ImageStim(self.win, image=_thisDir+'/instructions/instr-4-task.png')

# Create Stimuli class
#   Generates stimuli that will be presented during the task
class Stimuli:
    def __init__(self, exp):
        
        # Create stimuli for SST
        if exp.genSettings['Paradigm'] == 'SST':
            self.L_cue = visual.Polygon(exp.win, edges=3, fillColor=None, lineWidth=5, lineColor=exp.advSettings['Cue color'], opacity=1, units='cm', size=[exp.advSettings['Stimulus size (cm)'],0.6*exp.advSettings['Stimulus size (cm)']], ori=-90, pos=[-1,0])
            self.L_stim = visual.Polygon(exp.win, edges=3, fillColor=exp.advSettings['Go color'], lineWidth=5, lineColor=exp.advSettings['Cue color'], opacity=1, units='cm', size=[exp.advSettings['Stimulus size (cm)'],0.6*exp.advSettings['Stimulus size (cm)']], ori=-90, pos=[-1,0])
            self.R_cue = visual.Polygon(exp.win, edges=3, fillColor=None, lineWidth=5, lineColor=exp.advSettings['Cue color'], opacity=1, units='cm', size=[exp.advSettings['Stimulus size (cm)'],0.6*exp.advSettings['Stimulus size (cm)']], ori=90, pos=[1,0])
            self.R_stim = visual.Polygon(exp.win, edges=3, fillColor=exp.advSettings['Go color'], lineWidth=5, lineColor=exp.advSettings['Cue color'], opacity=1, units='cm', size=[exp.advSettings['Stimulus size (cm)'],0.6*exp.advSettings['Stimulus size (cm)']], ori=90, pos=[1,0])
        
        # Create stimuli for ARI
        elif exp.genSettings['Paradigm'] == 'ARI':
            # Do some calculations for size of bars and target lines
            barWidth = 1.5
            barTop = exp.advSettings['Stimulus size (cm)']/2
            vert1Width = 0-(barWidth/2)
            vert2Width = (barWidth/2)
            self.L_emptyVert = [(vert1Width+-1.5,0-barTop), (vert1Width+-1.5,0-barTop+.01), 
                    (vert2Width+-1.5,0-barTop+.01), (vert2Width+-1.5,0-barTop)]
            self.L_fullVert = [(vert1Width+-1.5,0-barTop),(vert1Width+-1.5,barTop),
                    (vert2Width+-1.5,barTop),(vert2Width+-1.5,0-barTop)]
            self.R_emptyVert = [(vert1Width+3,0-barTop), (vert1Width+3,0-barTop+.01), 
                    (vert2Width+0,0-barTop+.01), (vert2Width+0,0-barTop)]
            self.R_fullVert = [(vert1Width+3,0-barTop),(vert1Width+3,barTop),
                    (vert2Width+0,barTop),(vert2Width+0,0-barTop)]
            self.L_emptyStim = visual.ShapeStim(exp.win, vertices=self.L_fullVert, fillColor='white', lineWidth=0, opacity=1, units='cm')
            self.R_emptyStim = visual.ShapeStim(exp.win, vertices=self.R_fullVert, fillColor='white', lineWidth=0, opacity=1, units='cm')
            self.barTop = barTop  
            TargetLineWidth = 5.5
            TargetPos = (exp.advSettings['Target position']*exp.advSettings['Stimulus size (cm)'])-exp.advSettings['Stimulus size (cm)']/2 # set target to target position
                       
            # Create stimuli (filling bars and target lines)
            self.L_cue = visual.Line(exp.win, lineColor = exp.advSettings['Cue color'], start=[0-(TargetLineWidth/2),TargetPos],end=[TargetLineWidth/2-3,TargetPos], lineWidth=10)
            self.L_stim = visual.ShapeStim(exp.win, fillColor=exp.advSettings['Go color'], lineWidth=0, opacity=1, units='cm', vertices=self.L_emptyVert)
            self.R_cue = visual.Line(exp.win, lineColor = exp.advSettings['Cue color'], start=[0-(TargetLineWidth/2)+3,TargetPos],end=[TargetLineWidth/2,TargetPos], lineWidth=10)
            self.R_stim = visual.ShapeStim(exp.win, fillColor=exp.advSettings['Go color'], lineWidth=0, opacity=1, units='cm', vertices=self.R_emptyVert)

# Create Trials class
#   Generates trials that will be presented during the task based on settings or imported file, and
#   initiates counters and settings for trial number, scores, and target RTs
class Trials:
    def __init__(self,exp):
        if exp.genSettings['Import trials?'] == True: # import trials from conditions file
            self.trialList = data.importConditions(exp.genSettings['File path'] + exp.genSettings['File name'])
            self.blockTrials = np.array_split(self.trialList,exp.genSettings['n blocks'])
        else:
            nGoTrials = [1] * exp.genSettings['n go trials per block'] # set number of go and stop trials
            nStopBothTrials = [2] * exp.genSettings['n stop-both trials per block']
            nStopLeftTrials = [3] * exp.genSettings['n stop-left trials per block']
            nStopRightTrials = [4] * exp.genSettings['n stop-right trials per block']
            self.trialList = nGoTrials + nStopBothTrials + nStopLeftTrials + nStopRightTrials

        if exp.genSettings['Practice trials?'] == True:
            exp.genSettings['n blocks'] = exp.genSettings['n blocks'] + 1 # add an additional block if practice trials have been selected
        self.blockList = [1] * exp.genSettings['n blocks'] # create list of blocks (NOTE: this can be used in the future to set block types)
              
        if exp.genSettings['Paradigm'] == 'ARI':
            # self.L_targetTime = exp.advSettings['Target time (ms)'] # set target time
            # self.R_targetTime = exp.advSettings['Target time (ms)']
            # stimuli.L_targetLine.fillColor = exp.advSettings['Target color'] # set target color
            # stimuli.R_targetLine.fillColor = exp.advSettings['Target color']
            pass
        
        # Set up counters for block and trial number
        self.blockCount = 0
        self.trialCount = 0
               
        # Set score values
        self.totalScore = 0
        self.blockScore = 0
        self.trialScore = 0         
        self.lowScore = 10
        self.midScore = 20
        self.highScore = 30
        # Set target RTs
        if exp.genSettings['Paradigm'] == 'ARI':
            self.lowTarget = 75
            self.midTarget = 50
            self.highTarget = 25
        elif exp.genSettings['Paradigm'] == 'SST':
            self.lowTarget = 500
            self.midTarget = 400
            self.highTarget = 300            

        # Create arrays of len('n blocks') for use in plotting block data for feedback
        BlockCountArray = np.array([])
        for i in range(1,exp.genSettings['n blocks']+1):
            self.BlockCountArray = np.append(BlockCountArray, [i], axis = 0)    
        BlockScoreArray = np.array([])
        for i in range(exp.genSettings['n blocks']):
            self.BlockScoreArray = np.append(BlockScoreArray, [0], axis = 0)
 
# Create SSD class
#   Generates information for stop trials based on selected settings
class SSD:
    def __init__(self,exp):
        # Set up initial stop-signal delays within an array
            # For example, stop-both trials are set to the first value (0) within the array.
            # Additional stop-times for different conditions (e.g. reac vs proac) can be included by adding additional variables to the array.
        self.stopTimeArray = array.array('i', [0, exp.advSettings['Stop-both time (ms)'],exp.advSettings['Stop-left time (ms)'],exp.advSettings['Stop-right time (ms)']]) # array to store stopTimes (NOTE: can append stop time for additional staircases)
        self.strcaseTime = exp.advSettings['Stop-signal delay step-size (ms)'] # set desired increment for staircase
    
"""
MODIFIED CLASSES CAN BE INSERTED BELOW
    e.g., Experiment_debug
    This allows for quick switching between experiments without having to change the settings within the code.
"""

class Experiment_debug():
    def __init__(self,_thisDir):
        
        # Create dictionary with general task settings
        self.genSettings= {'Experiment name': 'x', # included in filename
            'Participant ID':0000, # included in filename
            'Age (Years)':00,
            'Sex':['-', 'F', 'M', 'Prefer not to say'],
            'Monitor name': 'dell_laptop', # name of monitor (see https://www.psychopy.org/builder/builderMonitors.html for more info)
            'Full-screen?': True,
            'Use response box?': False, # option to enable external response box
            'Feedback?' : True, # option to present trial-by-trial feedback
            'Practice trials?': False,
            'n practice go trials': 36,
            'Import trials?': False, # option to import trials
            'File path': _thisDir, # file path for imported trials file
            'File name': 'trials_1.xlsx', # name of file to import
            'Save data?': False,
            'Paradigm': ['ARI','SST'], # select paradigm type to use (NOTE: can change the default option by switching order in the list)
            'n go trials per block': 2,
            'n stop-both trials per block': 2,
            'n stop-left trials per block': 2,
            'n stop-right trials per block': 2,
            'n blocks': 2, # number of blocks to repeat the above trial arrangement       
            'Change advanced settings?':False # option to change advanced settings via GUI
            }
        
        # Create GUI for expInfo dictionary w/ tool tips
        dlg=gui.DlgFromDict(dictionary=self.genSettings, title='SeleSt (general settings)',
            order = ('Experiment name', 'Participant ID', 'Age (Years)', 'Sex', 'Monitor name', 'Full-screen?', 'Use response box?', 'Import trials?', 'File path', 'File name', 'Save data?', 'Practice trials?', 'n practice go trials', 'n go trials per block', 'n stop-both trials per block', 'n stop-left trials per block', 'n stop-right trials per block','n blocks', 'Feedback?','Change advanced settings?'),
            tip={'Experiment name': 'Input name of experiment which will included in data file',
                 'Monitor name': 'Input name of the monitor being used to present the task (see Monitor Centre for more info)',
                 'Full-screen?': 'Select this if you would like to run the task in full-screen mode (recommended for data collection)',
                 'Feedback?': 'Deselect this feature if you do not wish to present trial-by-trial and end-of-block feedback',
                 'Practice trials?': 'Select this if you wish to run through a practice block of go trials',
                 'Import trials?': 'Select this if you are using the trials.xlsx file (NOTE: this will override randomisation)',
                 'n blocks': 'Set the number of blocks to repeat the trials across (NOTE: if importing trials the number of trials will be divided by n blocks; e.g., 100 trials, 10 blocks = 10 blocks x 10 trials)',
                 'Change advanced settings?': 'Select this if you would like to change any of the advanced settings (e.g. target time, target color, step size)'})
        if dlg.OK ==False: core.quit() # user pressed cancel
        self.genSettings['date'] = data.getDateStr() # add timestamp (will be included data filename)

        # Create dictionary with advanced task settings (default settings dependent on paradigm)
        if self.genSettings['Paradigm'] == 'ARI':       
            Defaults = {'Target time (ms)': 800, 'Trial length (s)': 1.5, 'Fixed delay length (s)': 0.5, 'Stop-both time (ms)': 600, 'Stop-left time (ms)': 550, 'Stop-right time (ms)': 550, 'Lower stop-limit (ms)': 150, 'Upper stop-limit (ms)': 50, 'Positional stop signal': True, 'Target position': 0.8, 'Stimulus size (cm)': 15}
        elif self.genSettings['Paradigm'] == 'SST':       
            Defaults = {'Target time (ms)': 300, 'Trial length (s)': 1.5, 'Fixed delay length (s)': 1, 'Stop-both time (ms)': 300, 'Stop-left time (ms)': 250, 'Stop-right time (ms)': 250, 'Lower stop-limit (ms)': 150, 'Upper stop-limit (ms)': 50, 'Positional stop signal': False, 'Target position': 0.8, 'Stimulus size (cm)': 5}
                                                             
        self.advSettings={'Send serial trigger at trial onset?': False,
            'Hold-and-release': False,
            'Left response key': 'left',
            'Right response key': 'right',
            'Target time (ms)': Defaults['Target time (ms)'], # target RT you would like to cue for
            'Trial length (s)': Defaults['Trial length (s)'],
            'Intertrial interval (s)': 1.5,
            'Fixed rise delay?' : False,
            'Fixed delay length (s)': Defaults['Fixed delay length (s)'],
            'n forced go trials': 1,
            'Staircase stop-signal delays?' : True,
            'Stop-signal delay step-size (ms)': 50,
            'Stop-both time (ms)': Defaults['Stop-both time (ms)'],
            'Stop-left time (ms)': Defaults['Stop-left time (ms)'],
            'Stop-right time (ms)': Defaults['Stop-right time (ms)'],
            'Lower stop-limit (ms)': Defaults['Lower stop-limit (ms)'],
            'Upper stop-limit (ms)': Defaults['Upper stop-limit (ms)'],
            'Positional stop signal': Defaults['Positional stop signal'],
            'Stimulus size (cm)': Defaults['Stimulus size (cm)'],
            'Target position': Defaults['Target position'],
            'Cue color': 'black',
            'Go color': 'black',
            'Stop color': 'cyan',
            'Background color': 'grey'}
        
        # Create GUI for advExpInfo dictionary if advanced option was selected
        if self.genSettings['Change advanced settings?']:
            dlg=gui.DlgFromDict(dictionary=self.advSettings, title='SeleSt (Advanced settings)',
                order = ('Send serial trigger at trial onset?', 'Hold-and-release', 'Left response key', 'Right response key', 'Target time (ms)', 'Trial length (s)', 'Intertrial interval (s)', 'Fixed rise delay?', 'Fixed delay length (s)', 'n forced go trials', 'Staircase stop-signal delays?', 'Stop-signal delay step-size (ms)', 'Stop-both time (ms)', 'Stop-left time (ms)', 'Stop-right time (ms)', 'Lower stop-limit (ms)', 'Upper stop-limit (ms)', 'Positional stop signal', 'Target position', 'Stimulus size (cm)', 'Background color', 'Cue color', 'Go color', 'Stop color'),
                tip={'Send serial trigger at trial onset?': 'Select this if you would like to send a trigger at trial onset (NOTE: a serial device must be set up for this to work)',
                     'Hold-and-release': 'Determines if trials automatically cycle (wait-and-press) or wait for response keys to be pressed (hold-and-release)',
                     'Target time (ms)': 'Input the desired target response time (NOTE: keep in mind that trial length needs to be adjusted to allow for complete filling if target time is extended too far)',
                     'Trial length (s)': 'Input desired trial length (NOTE FOR ARI: this should be at least the length of total time it takes for both bars to fill)',
                     'Intertrial interval (s)': 'Input the desired intertrial interval (ITI)',
                     'Fixed rise delay?': 'If selected, each trial will begin with a fixed rise delay (length below). If unselected, each trial will begin with a variable rise delay (ARI: 500 - 1000 ms, SST: 1000 - 2000 ms).',
                     'Fixed delay length (s)': 'Length of fixed delay (if selected) you would like to use at the start of each trial',
                     'n forced go trials': 'Input the number of go trials you would like to force at the start of each block',
                     'Staircase stop-signal delays?': 'Select if you would like to use a fixed or staircased stop-signal delay',
                     'Lower stop-limit (ms)': 'Time relative to trial onset that the bars should not stop before',
                     'Upper stop-limit (ms)': 'Time relative to target time that the bars should not stop after (e.g. 800 ms target, 150 ms upper stop-limit = 650 ms stopping limit)',
                     'Positional stop signal': 'ARI ONLY: Present stop signal as cessation of rising bars, if not, change color of filling bar',
                     'Stimulus size (cm)': 'Size of the left and right stimuli (ARI = height of bars, SST = height of triangles)',
                     'Target position': 'ARI ONLY: Input where you would like the target lines to be positioned as proportion of total bar height (e.g. 0.8 equates to 80% of bar height/filling time)',
                     'Cue color': 'Input name of desired color of the cue (ARI = target lines, SST = triangle outline)',
                     'Go color': 'Input name of desired color of the go signal (ARI = filling bar, SST = triangle filling)',
                     'Stop color': 'Input name of desired color of the stop signal (ARI = N/A, SST = triangle filling)',
                     'Background color': 'Input name of desired color of the background (for list of possible colors see https://www.w3schools.com/Colors/colors_names.asp )'})
        if dlg.OK==False: core.quit()
        
        # Set up the window in which we will present stimuli
        self.win = visual.Window(
            fullscr=self.genSettings['Full-screen?'],
            winType='pyglet',
            monitor=self.genSettings['Monitor name'],
            color=self.advSettings['Background color'],
            blendMode='avg',
            allowGUI=False,
            units = 'cm')
        
        # Measure the monitors refresh rate
        self.genSettings['frameRate'] = self.win.getActualFrameRate()
        self.frameRate = self.genSettings['frameRate']
        if self.frameRate != None:
            self.frameDur = 1.0 / round(self.frameRate) * 1000
        else:
            self.frameDur = 1.0 / 60.0 * 1000 # could not measure, so guess
        print('Monitor frame rate is %s Hz' %(round(self.genSettings['frameRate'],0))) # print out useful info on frame rate & duration for the interested user
        print('Frame duration is %s ms' %round(self.frameDur,1))        
        
        # Here you can implement code to operate an external response box. The keyboard
        # will be used if no response box is selected.
        if self.genSettings['Use response box?'] == True:
            # e.g.
            #self.rb = buttonbox.Buttonbox()    # example buttonbox from RuSocSci
            #self.L_resp_key = 'E'
            #self.R_resp_key = 'A'
            if self.advSettings['Hold-and-release'] == True:
                pass
            pass
        else:
            self.rb = keyboard.Keyboard()  # use input rom keyboard
            self.L_resp_key = self.advSettings['Left response key']
            self.R_resp_key = self.advSettings['Right response key']        
            
        
        # Here you can set up a serial device (e.g. to send trigger at trial onset)
        if self.advSettings['Send serial trigger at trial onset?'] == True:    
            # e.g.
            #self.ser = serial.Serial('COM8', 9600, timeout=0)
            #line = ser.readline()
            pass

        # Create clocks to monitor trial duration and trial times
        self.globalClock = core.Clock() # to track total time of experiment
        self.trialClock = core.Clock() # to track time on a trial-by-trial basis
        self.holdClock = core.Clock() # to track press time when waiting for key press in hold and release

        # Check if a "data" folder exists in this directory, and make one if not.
        if not os.path.exists(_thisDir + os.sep +'data/'):
            print('Data folder did not exist, making one in current directory')
            os.makedirs(_thisDir + os.sep +'data/')
        
        # Create the name of the output file. "Output" is the output file.
        if self.genSettings['Save data?'] == True:
            self.Output = _thisDir + os.sep + u'data/SelARI_%s_%s_%s' % (self.genSettings['Participant ID'],
                self.genSettings['Experiment name'], self.genSettings['date'])
            with open(self.Output+'.txt', 'a') as b:
                b.write('block trial startTime trialName trialType stopTime L_press R_press L_targetTime R_targetTime L_RT R_RT\n')