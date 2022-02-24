"""
Selective Stopping (SeleSt) task

    SeleSt_run
        Functions to run the task can be found in this script
        
    See the SeleSt.py script for general information on the task
"""

# Import required modules
from random import shuffle, uniform
from psychopy import event, core, visual
from psychopy.constants import PRESSED

import psychtoolbox as ptb
from psychopy import sound

# Define Block function
#   Here the trial list for a given block is generated
def Block(exp,trialInfo):
    # Shuffle trials on a block-by-block basis
    if exp.taskInfo['Import trials?'] == False: # don't shuffle trials if they have been imported
        shuffleTrials = True
        while shuffleTrials == True: # shuffle until go criterion is achieved
            thisBlockTrials = trialInfo.trialList
            shuffle(thisBlockTrials)
            if sum(thisBlockTrials[:exp.genSettings['n forced go trials']]) > exp.genSettings['n forced go trials']: # reshuffle trials if n forced go criterion is not met
                thisBlockTrials = shuffle(thisBlockTrials)
            elif sum(thisBlockTrials[:exp.genSettings['n forced go trials']]) <= exp.genSettings['n forced go trials']: # break loop if n forced go criterion is achieved
                break    
    elif exp.taskInfo['Import trials?'] == True: # use imported trials if option is selected
        thisBlockTrials = trialInfo.blockTrials[trialInfo.blockCount] # start from 0 to account for zero-based array index
    # Add instructions for practice go-only and go/stop blocks if practice is enabled            
    if exp.taskInfo['Include practice?'] == True:
        if exp.practiceGo == True: # practice go (coded as block -1 in data file)
            thisBlockTrials = exp.genSettings['n practice go trials'] * [1]
            exp.instr_1_go.draw() # draw 1st instruction
            exp.win.flip()
            exp.rb.waitKeys(keyList=['space'])
            exp.instr_2_points.draw() # draw 2nd instruction
            exp.win.flip()
            exp.rb.waitKeys(keyList=['space'])
            trialInfo.blockCount = -2
        if exp.practiceStop == True and exp.practiceGo == False: # practice go/stop (coded as block 0 in data file)
            exp.instr_3_stop.draw() # draw 3rd instruction
            exp.win.flip()
            exp.rb.waitKeys(keyList=['space'])
            exp.practiceStop = False # go/stop practice is complete
        if exp.practiceStop == False and exp.practiceGo == False and trialInfo.blockCount == 0: # start experimental blocks
            exp.instr_4_task.draw()
            exp.win.flip()
            exp.rb.waitKeys(keyList=['space'])
    exp.practiceGo = False # go-only practice is complete
    trialInfo.blockCount = trialInfo.blockCount + 1 # track block number
    print('Starting block %s'%(trialInfo.blockCount)) # print block number to console
    
    return thisBlockTrials # return list of trials for current block

# Define Initialize_trial function
#   Here information for the given trial is obtained and counters are reset
class Initialize_trial:
    def __init__(self,exp,trialInfo,stopInfo,trial):
        if exp.taskInfo['Import trials?'] == True: # if parameters are specified in imported trials file
            thisTrial = trialInfo.trialList[trialInfo.trialCount-1]
            self.trialName = thisTrial['trialName']
            self.trialType = thisTrial['trialType']
            self.staircase = thisTrial['ssd']
        else:
            self.trialType = trial # use GUI information if no imported trials
            if self.trialType == 1: # if go
                self.staircase = 0
                self.trialName = 'Go'
            if self.trialType == 2: # if stop-both
                self.staircase = 1
                self.trialName = 'Stop-all'
            if self.trialType == 3: # if stop-left
                self.staircase = 2
                self.trialName = 'Stop-left'
            if self.trialType == 4: # if stop-right
                self.staircase = 3
                self.trialName = 'Stop-right'
        self.stopTime = stopInfo.stopTimeArray[self.staircase] # assign stoptime based on staircase                
        # Reset dynamic parameters
        self.L_RT_array_time = []
        self.L_RT_time = 0
        self.L_duration = 0
        self.L_RT = 0
        self.L_press = 0
        self.L_draw = True
        self.R_RT_array_time = []
        self.R_RT_time = 0
        self.R_duration = 0
        self.R_RT = 0
        self.R_press = 0
        self.R_draw = True
        self.stopSuccess = 0
        
# Define Start_trial function
#   Here the parameters for the current trial are implemented
class Start_Trial:
    def __init__(self,exp,stimuli,trialInfo,thisTrial,trial):
        if exp.taskInfo['Import trials?'] == True and trialInfo.blockCount > 0: # use imported trial information if selected
            exp.advSettings['Go color'] = trial['go_color']
            exp.advSettings['Stop color'] = trial['stop_color']
            stimuli.L_cue.lineColor = trial['L_cue_color']
            stimuli.R_cue.lineColor = trial['R_cue_color']
            thisTrial.L_targetTime = trial['L_targetTime']
            thisTrial.R_targetTime = trial['R_targetTime']
        else: # use GUI if not importing trials
            stimuli.L_cue.lineColor = exp.advSettings['Cue color']
            stimuli.R_cue.lineColor = exp.advSettings['Cue color']
            thisTrial.L_targetTime = exp.advSettings['Target time (ms)']
            thisTrial.R_targetTime = exp.advSettings['Target time (ms)']          
        # Start ARI trial        
        if exp.taskInfo['Paradigm'] == 'ARI':
            self.L_fillTime = thisTrial.L_targetTime / exp.advSettings['Target position'] # left bar fill time
            self.L_increase = 0 # initial height of L bar
            self.R_fillTime = thisTrial.R_targetTime / exp.advSettings['Target position'] # right bar fill time
            self.R_increase = 0 # initial height of R bar
            # Calculate fill limits if using positional stop signal
            if exp.advSettings['Positional stop signal'] == True:
                if thisTrial.trialType == 1: # if go trial
                    self.L_fillLimit = stimuli.L_fullVert[1][1]
                    self.R_fillLimit = stimuli.R_fullVert[1][1]
                if thisTrial.trialType == 2: # if stop-both trial
                    stopBothRatio = thisTrial.stopTime / self.L_fillTime # compute ratio of stop time to fill time
                    stopBothPos = exp.advSettings['Stimulus size (cm)'] * stopBothRatio - stimuli.barTop # calculate position of stopped bar relative to empty bar height and position
                    self.L_fillLimit = stopBothPos
                    self.R_fillLimit = stopBothPos            
                if thisTrial.trialType == 3: # if stop-left trial
                    stopLeftRatio = thisTrial.stopTime / self.L_fillTime # compute ratio of stop time to fill time
                    stopLeftPos = exp.advSettings['Stimulus size (cm)'] * stopLeftRatio - stimuli.barTop # calculate position of stopped bar relative to empty bar height and position
                    self.L_fillLimit = stopLeftPos
                    self.R_fillLimit = stimuli.R_fullVert[1][1]
                if thisTrial.trialType == 4: # if stop-right trial
                    stopRightRatio = thisTrial.stopTime / self.R_fillTime # compute ratio of stop time to fill time
                    stopRightPos = exp.advSettings['Stimulus size (cm)'] * stopRightRatio - stimuli.barTop # calculate position of stopped bar relative to empty bar height and position
                    self.L_fillLimit = stimuli.L_fullVert[1][1]
                    self.R_fillLimit = stopRightPos  
            else: # always fill bars if not using a positional stop signal
                self.L_fillLimit = stimuli.L_fullVert[1][1]
                self.R_fillLimit = stimuli.R_fullVert[1][1]                
                
            # Reset dynamic ARI parameters
            stimuli.L_emptyVert[1]=(stimuli.L_emptyVert[1][0], -stimuli.barTop+0.01)
            stimuli.L_emptyVert[2]=(stimuli.L_emptyVert[2][0], -stimuli.barTop+0.01)
            stimuli.L_stim.vertices = stimuli.L_emptyVert            
            stimuli.R_emptyVert[1]=(stimuli.R_emptyVert[1][0], -stimuli.barTop+0.01)
            stimuli.R_emptyVert[2]=(stimuli.R_emptyVert[2][0], -stimuli.barTop+0.01)
            stimuli.R_stim.vertices = stimuli.R_emptyVert    
            stimuli.L_stim.fillColor = exp.advSettings['Go color']
            stimuli.R_stim.fillColor = exp.advSettings['Go color']               
            # Draw the stimuli
            stimuli.L_cue.setAutoDraw(True)
            stimuli.L_emptyStim.setAutoDraw(True)
            stimuli.R_cue.setAutoDraw(True)
            stimuli.R_emptyStim.setAutoDraw(True)
            
        if exp.taskInfo['Paradigm'] == 'SST': # reset and draw SST parameters
            stimuli.L_stim.fillColor = 'white'
            stimuli.R_stim.fillColor = 'white'
            stimuli.L_stim.setAutoDraw(True)
            stimuli.L_cue.setAutoDraw(True)
            stimuli.R_stim.setAutoDraw(True)
            stimuli.R_cue.setAutoDraw(True)

# Define fixationPeriod function
#   Here the fixation period is generated and implemented. For hold-and-release version the keys need to
#   held for as long as the fixation period.
def fixationPeriod(exp,stimuli):
    if exp.advSettings['Fixed delay?'] == True: # use fixed rise delay if option is selection
        fixPeriod = exp.advSettings['Fixed delay length (s)']
    else:
        fixPeriod = uniform(float(exp.advSettings['Variable delay lower limit (s)']), float(exp.advSettings['Variable delay upper limit (s)']))
    if exp.taskInfo['Response mode'] == 'Hold-and-release': # if hold and release
        L_key = 0
        R_key = 0
        while True: # wait for both keys to be pressed
            allKeys = event.getKeys()
            if exp.genSettings['Use response box?'] == True: # track response box if it is being used
                # e.g. allKeys = rb.getKeys()
                pass
            else:
                for thisKey in allKeys: # monitor key presses (separate from drawing routine)
                    if (thisKey == exp.L_resp_key):
                        L_key = PRESSED
                    elif (thisKey == exp.R_resp_key):
                        R_key = PRESSED 
                    elif thisKey in ['q', 'escape']: # flag for esc or q key to exit program
                        endTask(exp,stimuli)
                    exp.holdClock.reset() # reset timer to keep track of hold length
                allKeys = exp.rb.getKeys(waitRelease = True) # track key presses
                for thisKey in allKeys: # reset key press status if release is detected
                    if (thisKey == exp.L_resp_key): # if left key is pressed
                        L_key = 0
                    elif (thisKey == exp.R_resp_key): # if right key is pressed
                        R_key = 0                
            if L_key * R_key != 0 and exp.holdClock.getTime() > fixPeriod: # waits for both keys to be held for riseDelay before starting trial
                 break
    else: # automatically run riseDelay if wait-and-press version
        core.wait(fixPeriod, hogCPUperiod=fixPeriod)
        
    if exp.advSettings['Send serial trigger at trial onset?'] == True: # send serial trigger if option is enabled
        # e.g. exp.ser.write([1])
        pass
        
    return fixPeriod
                                    
def runTrial(exp,stimuli,thisTrial,trialStimuli,trialTimer):
    # Set up keys to track for left and right responses based on task version (hold-and-release vs wait-and-press)
    if exp.taskInfo['Response mode'] == 'Hold-and-release' and exp.genSettings['Use response box?'] == False: 
        allKeys = exp.rb.getKeys([exp.advSettings['Left response key'],exp.advSettings['Right response key'],'q','escape'], waitRelease = True)
    elif exp.genSettings['Use response box?'] == True: #Uses input from response box
        # E.g.
        # allKeys = rb.getKeys()
        pass
    else:
        allKeys = exp.rb.getKeys([exp.advSettings['Left response key'],exp.advSettings['Right response key'],'q','escape'], waitRelease = False) #Uses keyboard with key press
    # Monitor key presses during trial
    for thisKey in allKeys:
         if thisKey==exp.L_resp_key: # left response
             thisTrial.L_RT_array_time.append(thisKey.rt) # store time-based RT
             thisTrial.L_duration = thisKey.duration # store duration for hold-and-release version
             thisTrial.L_draw = False # stop drawing the L stimulus
             thisTrial.L_press = 1 # L key was pressed
         elif thisKey==exp.R_resp_key: # right response
             thisTrial.R_RT_array_time.append(thisKey.rt)
             thisTrial.R_duration = thisKey.duration
             thisTrial.R_draw = False
             thisTrial.R_press = 1
         elif thisKey in ['q', 'escape']: # monitor for esc or q press
             endTask(exp,stimuli)
    if exp.taskInfo['Paradigm'] == 'ARI': # draw filling bars for ARI paradigm                 
        if thisTrial.L_draw == True: # if L bar should still increase
            stimuli.L_emptyVert[1]=(stimuli.L_emptyVert[1][0], stimuli.L_emptyVert[1][1]-trialStimuli.L_increase) # reset top left and top right vertices
            stimuli.L_emptyVert[2]=(stimuli.L_emptyVert[2][0], stimuli.L_emptyVert[2][1]-trialStimuli.L_increase)
            trialStimuli.L_increase = ((exp.advSettings['Trial length (s)']-trialTimer.getTime())*exp.advSettings['Stimulus size (cm)']/(trialStimuli.L_fillTime/1000)) # calculate current height of the bar
            stimuli.L_emptyVert[1]=(stimuli.L_emptyVert[1][0], stimuli.L_emptyVert[1][1]+trialStimuli.L_increase) # assign height to top left and top right vertices
            stimuli.L_emptyVert[2]=(stimuli.L_emptyVert[2][0], stimuli.L_emptyVert[2][1]+trialStimuli.L_increase)
            stimuli.L_stim.vertices = stimuli.L_emptyVert # assign vertices to L stim
            if stimuli.L_emptyVert[1][1]>trialStimuli.L_fillLimit: # stop drawing L bar when it is at its limit
                 stimuli.L_stim.vertices = stimuli.L_fullVert
            stimuli.L_stim.setAutoDraw(True) # draw
        if thisTrial.R_draw == True: # repeat above for the R bar
            stimuli.R_emptyVert[1]=(stimuli.R_emptyVert[1][0], stimuli.R_emptyVert[1][1]-trialStimuli.R_increase)
            stimuli.R_emptyVert[2]=(stimuli.R_emptyVert[2][0], stimuli.R_emptyVert[2][1]-trialStimuli.R_increase)
            trialStimuli.R_increase = ((exp.advSettings['Trial length (s)']-trialTimer.getTime())*exp.advSettings['Stimulus size (cm)']/(trialStimuli.R_fillTime/1000))
            stimuli.R_emptyVert[1]=(stimuli.R_emptyVert[1][0], stimuli.R_emptyVert[1][1]+trialStimuli.R_increase)
            stimuli.R_emptyVert[2]=(stimuli.R_emptyVert[2][0], stimuli.R_emptyVert[2][1]+trialStimuli.R_increase)
            stimuli.R_stim.vertices = stimuli.R_emptyVert
            if stimuli.R_emptyVert[1][1]>trialStimuli.R_fillLimit: # stop drawing L bar when it is at its limit
                 stimuli.R_stim.vertices = stimuli.R_fullVert
            stimuli.R_stim.setAutoDraw(True)

    elif exp.taskInfo['Paradigm'] == 'SST': # draw go stimulus for SST paradigm
        if thisTrial.L_draw == True:
            stimuli.L_stim.fillColor = exp.advSettings['Go color']
        if thisTrial.R_draw == True:
            stimuli.R_stim.fillColor = exp.advSettings['Go color']
                
# Define stop_signal function
#   Function for presenting stop signal when stop timer reaches 0
def stop_signal(exp,stimuli,thisTrial,trialStimuli):
    # Visual stop signal (colour of stimuli)
    if exp.advSettings['Positional stop signal'] == False:
        if thisTrial.trialType == 2:
            stimuli.L_stim.fillColor = exp.advSettings['Stop color']
            stimuli.R_stim.fillColor = exp.advSettings['Stop color']
        elif thisTrial.trialType == 3:
            stimuli.L_stim.fillColor = exp.advSettings['Stop color']
        elif thisTrial.trialType == 4:
            stimuli.R_stim.fillColor = exp.advSettings['Stop color'] 

# Define getRT function
#   Function for processing and storing RTs on a given trial
def getRT(exp,thisTrial):
    if thisTrial.L_press == 0: # if no press assign dummy RTs of -9999 
        thisTrial.L_RT_time = -9999
    elif thisTrial.L_press == 1: # if press use the recorded RT
        if exp.taskInfo['Response mode'] == 'Hold-and-release': # use key duration if hold-and-release
            thisTrial.L_RT_time = round((thisTrial.L_RT_array_time[0] + thisTrial.L_duration) * 1000,1)
        else:
            thisTrial.L_RT_time = round(thisTrial.L_RT_array_time[0] * 1000,1)
    if thisTrial.R_press == 0:
        thisTrial.R_RT_time = -9999
    elif thisTrial.R_press == 1:
        if exp.taskInfo['Response mode'] == 'Hold-and-release':
            thisTrial.R_RT_time = round((thisTrial.R_RT_array_time[0] + thisTrial.R_duration) * 1000,1)
        else:
            thisTrial.R_RT_time = round(thisTrial.R_RT_array_time[0] * 1000,1)                
    print('Left RT was %s ms'%round(thisTrial.L_RT_time,1)) # print left and right RTs to console
    print('Right RT was %s ms'%round(thisTrial.R_RT_time,1))

# Define feedback function
#   Function for presenting feedback at end of a trial
def feedback(exp,stimuli,trialInfo,thisTrial,trialStimuli): 
    if exp.taskInfo['Paradigm'] == 'ARI': # use positional RTs if ARI paradigm (i.e., propn of filled bar to filling time)
        L_RT = (stimuli.L_emptyVert[1][1]+stimuli.barTop)/exp.advSettings['Stimulus size (cm)']*trialStimuli.L_fillTime
        R_RT = (stimuli.R_emptyVert[1][1]+stimuli.barTop)/exp.advSettings['Stimulus size (cm)']*trialStimuli.R_fillTime
    elif exp.taskInfo['Paradigm'] == 'SST': # use stored RTs if SST paradigm
        L_RT = thisTrial.L_RT_time
        R_RT = thisTrial.R_RT_time
    trialScore = 0  
    if thisTrial.trialType == 1: # if go trial
        if abs(thisTrial.L_targetTime-L_RT) > trialInfo.lowTarget:
            stimuli.L_cue.lineColor = 'Red'
            L_score = 0
        if abs(thisTrial.L_targetTime-L_RT) < trialInfo.lowTarget:
            stimuli.L_cue.lineColor = 'Orange'
            L_score = trialInfo.lowScore
        if abs(thisTrial.L_targetTime-L_RT) < trialInfo.midTarget:
            stimuli.L_cue.lineColor = 'Yellow'
            L_score = trialInfo.midScore
        if abs(thisTrial.L_targetTime-L_RT) < trialInfo.highTarget:
            stimuli.L_cue.lineColor = 'Green'
            L_score = trialInfo.highScore
        if abs(thisTrial.R_targetTime-R_RT) > trialInfo.lowTarget:
            stimuli.R_cue.lineColor = 'Red'
            R_score = 0
        if abs(thisTrial.R_targetTime-R_RT) < trialInfo.lowTarget:
            stimuli.R_cue.lineColor = 'Orange'
            R_score = trialInfo.lowScore
        if abs(thisTrial.R_targetTime-R_RT) < trialInfo.midTarget:
            stimuli.R_cue.lineColor = 'Yellow'
            R_score = trialInfo.midScore
        if abs(thisTrial.R_targetTime-R_RT) < trialInfo.highTarget:
            stimuli.R_cue.lineColor = 'Green'
            R_score = trialInfo.highScore

    if thisTrial.trialType == 2: # if stop-all trial
        if thisTrial.L_press == 0 and thisTrial.R_press == 0:
            stimuli.L_cue.lineColor = 'Green'
            stimuli.R_cue.lineColor = 'Green' 
            L_score = trialInfo.highScore
            R_score = trialInfo.highScore
            thisTrial.stopSuccess = 1
        if thisTrial.L_press == 1 and thisTrial.R_press == 0:
            stimuli.L_cue.lineColor = 'Red'
            stimuli.R_cue.lineColor = 'Green'
            L_score = 0
            R_score = trialInfo.highScore
        if thisTrial.L_press == 0 and thisTrial.R_press == 1:
            stimuli.L_cue.lineColor = 'Green'
            stimuli.R_cue.lineColor = 'Red'
            L_score = trialInfo.highScore
            R_score = 0
        if thisTrial.L_press == 1 and thisTrial.R_press == 1:
            stimuli.L_cue.lineColor = 'Red'
            stimuli.R_cue.lineColor = 'Red'
            L_score = 0
            R_score = 0

    if thisTrial.trialType == 3: # if stop-left trial
        if thisTrial.L_press == 0:
            stimuli.L_cue.lineColor = 'Green'
            L_score = trialInfo.highScore
            thisTrial.stopSuccess = 1
        elif thisTrial.L_press == 1:
            stimuli.L_cue.lineColor = 'Red'
            L_score = 0
        if abs(thisTrial.R_targetTime-R_RT) > trialInfo.lowTarget:
            stimuli.R_cue.lineColor = 'Red'
            R_score = 0
        if abs(thisTrial.R_targetTime-R_RT) < trialInfo.lowTarget:
            stimuli.R_cue.lineColor = 'Orange'
            R_score = trialInfo.lowScore
        if abs(thisTrial.R_targetTime-R_RT) < trialInfo.midTarget:
            stimuli.R_cue.lineColor = 'Yellow'
            R_score = trialInfo.midScore
        if abs(thisTrial.R_targetTime-R_RT) < trialInfo.highTarget:
            stimuli.R_cue.lineColor = 'Green'
            R_score = trialInfo.highScore

    if thisTrial.trialType == 4: # if stop-right trial
        if thisTrial.R_press == 0:
            stimuli.R_cue.lineColor = 'Green'
            R_score = trialInfo.highScore
            thisTrial.stopSuccess = 1
        elif thisTrial.R_press == 1:
            stimuli.R_cue.lineColor = 'Red'
            R_score = 0
        if abs(thisTrial.L_targetTime-L_RT) > trialInfo.lowTarget:
            stimuli.L_cue.lineColor = 'Red'
            L_score = 0 
        if abs(thisTrial.L_targetTime-L_RT) < trialInfo.lowTarget:
            stimuli.L_cue.lineColor = 'Orange'
            L_score = trialInfo.lowScore
        if abs(thisTrial.L_targetTime-L_RT) < trialInfo.midTarget:
            stimuli.L_cue.lineColor = 'Yellow'
            L_score = trialInfo.midScore
        if abs(thisTrial.L_targetTime-L_RT) < trialInfo.highTarget:
            stimuli.L_cue.lineColor = 'Green'
            L_score = trialInfo.highScore

    trialScore = L_score + R_score # calculate trial score
    print('Trial score was %s'%(trialScore)) # print trialScore to console        
    if exp.genSettings['Trial-by-trial feedback?'] == True: # draw feedback if option is selected
        exp.win.flip()            
    thisTrial.L_RT = thisTrial.L_RT_time # use stored RTs for stored data
    if thisTrial.L_RT == -9999: # replace dummy no-response RTs w/ nans
        thisTrial.L_RT = float("nan")
    thisTrial.R_RT = thisTrial.R_RT_time
    if thisTrial.R_RT == -9999:
        thisTrial.R_RT = float("nan")
    if trialInfo.blockCount > 0:
        trialInfo.blockScore = trialInfo.blockScore + trialScore # updated block score

# Define staircaseSSD function
#   Function for adjusting SSD based on stop success
def staircaseSSD(exp,stopInfo,thisTrial): 
    print('Stop time was %s'%(thisTrial.stopTime)) # print stop time of current trial to console
    if exp.genSettings['Staircase stop-signal delays?'] == True: # only staircase if option is enabled
        if thisTrial.trialType > 1: # if stop trial
                if thisTrial.stopSuccess == 1: # if successful stop trial
                    if not stopInfo.stopTimeArray[thisTrial.staircase] + stopInfo.strcaseTime > (thisTrial.L_targetTime - exp.advSettings['Upper stop-limit (ms)']):
                        stopInfo.stopTimeArray[thisTrial.staircase] = stopInfo.stopTimeArray[thisTrial.staircase] + stopInfo.strcaseTime
                elif thisTrial.stopSuccess == 0: # if unsuccessful stop trial
                    if not stopInfo.stopTimeArray[thisTrial.staircase] - stopInfo.strcaseTime < exp.advSettings['Lower stop-limit (ms)']:
                        stopInfo.stopTimeArray[thisTrial.staircase] = stopInfo.stopTimeArray[thisTrial.staircase] - stopInfo.strcaseTime
                    
# Define saveData function
#   Function for saving data after each trial
def saveData(exp,trialInfo,thisTrial,startTime):
    if exp.taskInfo['Save data?'] == True: # save data if option is selected
        with open(exp.Output+'.txt', 'a') as b:
            b.write('%s %s %s %s %s %s %s %s %s %s %s %s\n'%(trialInfo.blockCount, trialInfo.trialCount, startTime, thisTrial.trialName, thisTrial.trialType, thisTrial.stopTime, thisTrial.L_press, thisTrial.R_press, thisTrial.L_targetTime, thisTrial.R_targetTime, thisTrial.L_RT, thisTrial.R_RT))

# Define ITI function
#   Function for running intertrial interval
def ITI(exp):
    core.wait(exp.advSettings['Intertrial interval (s)'])

# Define endTrial function
#   Function for removing stimuli at the end of each trial
def endTrial(exp,stimuli):
    stimuli.L_cue.setAutoDraw(False)    
    stimuli.R_cue.setAutoDraw(False)
    stimuli.L_stim.setAutoDraw(False)
    stimuli.R_stim.setAutoDraw(False)
    if exp.taskInfo['Paradigm'] == 'ARI':
        stimuli.L_emptyStim.setAutoDraw(False)
        stimuli.R_emptyStim.setAutoDraw(False)
        
# Define endBlock function
#   Function for presenting end-of-block feedback
def endBlock(exp,trialInfo,thisBlockTrials):   
    if trialInfo.blockCount > 0:
        trialInfo.totalScore = trialInfo.totalScore + trialInfo.blockScore # update total score    
        # Create text stimuli for feedback
        blockEnd = visual.TextStim(exp.win, pos=[0,3], height=1, color= [1,1,1],
            text='End of block %s!'%(trialInfo.blockCount), units='cm' )
        scoreBreakdown = visual.TextStim(exp.win, pos=[0,1.5], height=1, color= [1,1,1],
            text='Score breakdown:', units='cm' )     
        prevBlockFeedback = visual.TextStim(exp.win, pos=[0,0], height=1, color= [1,1,1],
            text='Previous block: -', units='cm' )        
        if trialInfo.blockCount > 1:
            prevBlockFeedback = visual.TextStim(exp.win, pos=[0, 0.0], height=1, color= [1,1,1],
                text='Previous block: %s points'%(trialInfo.prevBlockScore), units='cm' )
        thisBlockFeedback = visual.TextStim(exp.win, pos=[0, -1.5], height=1, color= [1,1,1],
            text='This block: %s points'%(trialInfo.blockScore), units='cm' )
        totalScoreFeedback = visual.TextStim(exp.win, pos=[0, -3], height=1, color= [1,1,1],
            text='Total: %s points'%(trialInfo.totalScore), units='cm' )
        instrFeedback = visual.TextStim(exp.win, pos=[0, -5], height=1, color= [1,1,1],
            text='Press the space key to continue', units='cm' )        
        event.clearEvents() # clear event buffer
        while not event.getKeys('space'):
            blockEnd.draw()
            instrFeedback.draw()
            scoreBreakdown.draw()
            thisBlockFeedback.draw()
            totalScoreFeedback.draw()
            prevBlockFeedback.draw()
            exp.win.flip()
        trialInfo.prevBlockScore = trialInfo.blockScore
        trialInfo.blockScore = 0
    
def endTask(exp, stimuli):
    endTrial(exp, stimuli)
    exp.instr_5_taskEnd.draw()
    exp.win.flip()
    exp.rb.waitKeys(keyList=['space'])
    
    # Close window, serial ports etc. at the end of the experiment
    if exp.advSettings['Send serial trigger at trial onset?'] == True:
        # E.g.
        #ser.close()
        pass
    if exp.genSettings['Use response box?'] == True:
        # E.g.
        #rb.close()   
        pass                                   
    exp.win.close()
    core.quit()