"""
Selective Stopping Toolbox (SeleST)

    SeleST_run
        Functions to run the task can be found in this script
        
    See the SeleST.py script for general information on the task
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
    shuffle(trialInfo.choiceList) # shuffle choice list
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
    trialInfo.blockTrialCount = 0 # reset block trial count
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
        self.stopSignal = True # flag whether to present stop signal
        
        # Reset dynamic parameters
        self.L_RT_array = [] # NOTE: arrays are set for each response key so multiple presses can be accounted for in a trial
        self.R_RT_array = []
        self.L2_RT_array = []
        self.R2_RT_array = []
        self.L_duration = 0
        self.R_duration = 0
        self.L2_duration = 0
        self.R2_duration = 0
        self.RTs = [float("nan"),float("nan"),float("nan"),float("nan")] # set RTs as NaNs
        self.pressState = [0,0,0,0] # set press states as 0 (i.e., no press)
        self.stopSuccess = 0 # set to stop success as 0
        
# Define Start_trial function
#   Here the parameters for the current trial are implemented
class Start_Trial:
    def __init__(self,exp,stimuli,trialInfo,thisTrial,trial):
        trialInfo.blockTrialCount = trialInfo.blockTrialCount + 1
        if exp.taskInfo['Import trials?'] == True and trialInfo.blockCount > 0: # use imported trial information if selected (additional variables to change trial-by-trial should be inserted below, e.g., L_targetTime & R_targetTime)
            exp.advSettings['Go color'] = trial['go_color']
            exp.advSettings['Stop color'] = trial['stop_color']
            stimuli.L_cue.lineColor = trial['L_cue_color']
            stimuli.R_cue.lineColor = trial['R_cue_color']
            # thisTrial.L_targetTime = trial['L_targetTime'] # example custom variable to run a decoupling response inhibition experiment (e.g., Wadsley et al., 2022, J Neurphysiol, https://doi.org/10.1152/jn.00495.2021)
            # thisTrial.R_targetTime = trial['R_targetTime']
        else: # use GUI if not importing trials 
            stimuli.L_cue.lineColor = exp.advSettings['Cue color']
            stimuli.R_cue.lineColor = exp.advSettings['Cue color']
        thisTrial.L_targetTime = exp.advSettings['Target time (ms)']
        thisTrial.R_targetTime = exp.advSettings['Target time (ms)']          
        # Start ARI trial        
        if exp.taskInfo['Paradigm'] == 'ARI':            
            self.L_fillTime = (thisTrial.L_targetTime / exp.advSettings['Target position']) # left bar fill time
            self.R_fillTime = (thisTrial.R_targetTime / exp.advSettings['Target position']) # right bar fill time
            # Calculate fill limits if using positional stop signal
            if exp.advSettings['Positional stop signal'] == True: # use filling proportions if positional stop-signal is being used (1 = completely filled, 0 = no filling)
                if thisTrial.trialType == 1: # if go trial
                    self.L_fillLimit = 1
                    self.R_fillLimit = 1
                if thisTrial.trialType == 2: # if stop-both trial
                    self.L_fillLimit = thisTrial.stopTime / self.L_fillTime # compute ratio of stop time to fill time
                    self.R_fillLimit = thisTrial.stopTime / self.L_fillTime # compute ratio of stop time to fill time
                if thisTrial.trialType == 3: # if stop-left trial
                    self.L_fillLimit = thisTrial.stopTime / self.L_fillTime # compute ratio of stop time to fill time
                    self.R_fillLimit = 1
                if thisTrial.trialType == 4: # if stop-right trial
                    self.L_fillLimit = 1
                    self.R_fillLimit = thisTrial.stopTime / self.L_fillTime # compute ratio of stop time to fill time  
            else: # always fill bars if not using a positional stop signal
                self.L_fillLimit = 1
                self.R_fillLimit = 1           
            self.fillTimes = [self.L_fillTime/1000, self.R_fillTime/1000]*2 # duplicate fill times for choice RT (NOTE: this can be individualised if wanting to use >2 response options)
            self.fillLimits = [self.L_fillLimit, self.R_fillLimit] *2 # same as above
        self.stimList = [stimuli.L_stim, stimuli.R_stim, stimuli.L_stim2, stimuli.R_stim2] # set list of stimuli to observe during a trial
        # Set draw status of stimuli based on choice option
        # NOTE: the draw options for choices can modified below
        # e.g., if you want to present stimuli by side (left two or right two stimuli) you can change draw status to [True,False,True,False] and [False,True,False,True] for each option (either by editing or adding below)
        if trialInfo.choiceList[trialInfo.blockTrialCount-1] == 1:
            self.drawStatus = [True,True,False,False] # L_stim & R_stim
            self.cueList = [stimuli.L_cue, stimuli.R_cue]
        elif trialInfo.choiceList[trialInfo.blockTrialCount-1] == 2:
            self.drawStatus = [False,False,True,True] # L_stim2 & R_stim2
            self.cueList = [stimuli.L_cue2, stimuli.R_cue2]
        if exp.taskInfo['RT type'] == 'Simple': # use L_stim and R_stim if using simple RT
            self.drawStatus = [True,True,False,False]
            self.cueList = [stimuli.L_cue, stimuli.R_cue]
        # Draw the background stimuli and reset the stimuli colours
        for s in stimuli.eStimList:
            s.setAutoDraw(True)
        for s in self.stimList:
            s.fillColor = exp.advSettings['Go color']   

# Define fixationPeriod function
#   Here the fixation period is generated and implemented. For hold-and-release version the keys need to
#   held for as long as the fixation period.
def fixationPeriod(exp,stimuli,trialStimuli):
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
                        endTask(exp,stimuli,trialStimuli)
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
        allKeys = exp.rb.getKeys([exp.advSettings['Left response key'],exp.advSettings['Right response key'], exp.advSettings['Left 2 response key'],exp.advSettings['Right 2 response key'],'q','escape'], waitRelease = True)
    elif exp.genSettings['Use response box?'] == True: # use input from response box
        # E.g.
        # allKeys = rb.getKeys()
        pass
    else:
        allKeys = exp.rb.getKeys([exp.advSettings['Left response key'],exp.advSettings['Right response key'], exp.advSettings['Left 2 response key'],exp.advSettings['Right 2 response key'], 'q','escape'], waitRelease = False) # use keyboard with key press
    # Monitor key presses during trial
    for thisKey in allKeys:
         if thisKey==exp.L_resp_key: # left response
             thisTrial.L_RT_array.append(thisKey.rt) # store time-based RT
             thisTrial.L_duration = thisKey.duration # store duration for hold-and-release version
             if exp.taskInfo['Paradigm'] == 'ARI':
                 trialStimuli.drawStatus[0] = False # stop drawing associated stimulus
             thisTrial.pressState[0] = 1 # L key was pressed
         elif thisKey==exp.R_resp_key: # right response
             thisTrial.R_RT_array.append(thisKey.rt)
             thisTrial.R_duration = thisKey.duration
             if exp.taskInfo['Paradigm'] == 'ARI':
                 trialStimuli.drawStatus[1] = False
             thisTrial.pressState[1] = 1
         elif thisKey==exp.L2_resp_key: # left 2 response
             thisTrial.L2_RT_array.append(thisKey.rt)
             thisTrial.L2_duration = thisKey.duration
             if exp.taskInfo['Paradigm'] == 'ARI':
                 trialStimuli.drawStatus[2] = False
             thisTrial.pressState[2] = 1
         elif thisKey==exp.R2_resp_key: # right 2 response
             thisTrial.R2_RT_array.append(thisKey.rt)
             thisTrial.R2_duration = thisKey.duration
             if exp.taskInfo['Paradigm'] == 'ARI':
                 trialStimuli.drawStatus[3] = False
             thisTrial.pressState[3] = 1
         elif thisKey in ['q', 'escape']: # monitor for esc or q press
             endTask(exp,stimuli,trialStimuli)
    
    # ARI
    if exp.taskInfo['Paradigm'] == 'ARI': # draw filling bars for ARI paradigm
        t = trialTimer.getTime() # grab time for current loop
        for i, stim in enumerate(trialStimuli.stimList): # loop over trial stimuli
            if trialStimuli.drawStatus[i] == True: # if stimuli should be updated
                fillPropn = (exp.advSettings['Trial length (s)']-t)/trialStimuli.fillTimes[i] # calculate current fill proportion based on time
                if fillPropn >= trialStimuli.fillLimits[i]: # if fill propn greater than limit, set fill propn to limit
                    fillPropn = trialStimuli.fillLimits[i]
                stim.size = (exp.advSettings['Stimulus width (cm)'], exp.advSettings['Stimulus size (cm)']*fillPropn) # update stimulus size
                stim.pos = (stimuli.xStimPos[i],-(1-fillPropn)*(exp.advSettings['Stimulus size (cm)']/2)) # update stimulus position
                stim.setAutoDraw(True) # draw stimulus

    elif exp.taskInfo['Paradigm'] == 'SST': # draw go stimulus for SST paradigm
        for i, stim in enumerate(trialStimuli.stimList): # loop over trial stimuli
            stim.setAutoDraw(trialStimuli.drawStatus[i]) # draw stimuli associated with choiced
                
# Define stop_signal function
#   Function for presenting stop signal when stop timer reaches 0
def stop_signal(exp,stimuli,thisTrial,trialStimuli):

    if thisTrial.stopSignal == True:
        # Visual stop signal (colour of stimuli)
        if exp.advSettings['Positional stop signal'] == False:      
            for i, stim in enumerate(trialStimuli.stimList):
                if thisTrial.trialType == 2: # if stop-both
                    stim.fillColor = exp.advSettings['Stop color']
                elif (thisTrial.trialType == 3 and i == 0) or (thisTrial.trialType == 3 and i == 2): # if stop-left
                    stim.fillColor = exp.advSettings['Stop color']
                elif (thisTrial.trialType == 4 and i == 1) or (thisTrial.trialType == 4 and i == 3): # if stop-right
                    stim.fillColor = exp.advSettings['Stop color']
                    
        thisTrial.stopSignal = False # stop-signal has been presented, so do not present again

# Define getRT function
#   Function for processing and storing RTs on a given trial
def getRT(exp,thisTrial,trialStimuli):   
    for i, respKey in enumerate(trialStimuli.stimList): # loop over response keys
        if thisTrial.pressState[i] == 1: # if key was pressed
            if i == 0: # L_resp
                if exp.taskInfo['Response mode'] == 'Hold-and-release':
                    thisTrial.RTs[i] = round((thisTrial.L_RT_array[0] + thisTrial.L_duration) * 1000,1)
                else:
                    thisTrial.RTs[i] = round(thisTrial.L_RT_array[0] * 1000,1)
            elif i == 1: # R_resp
                if exp.taskInfo['Response mode'] == 'Hold-and-release':
                    thisTrial.RTs[i] = round((thisTrial.R_RT_array[0] + thisTrial.R_duration) * 1000,1)
                else:
                    thisTrial.RTs[i] = round(thisTrial.R_RT_array[0] * 1000,1)    
            elif i == 2: # L_resp2
                if exp.taskInfo['Response mode'] == 'Hold-and-release':
                    thisTrial.RTs[i] = round((thisTrial.L2_RT_array[0] + thisTrial.L2_duration) * 1000,1)
                else:
                    thisTrial.RTs[i] = round(thisTrial.L2_RT_array[0] * 1000,1)
            elif i == 3: # R_resp2
                if exp.taskInfo['Response mode'] == 'Hold-and-release':
                    thisTrial.RTs[i] = round((thisTrial.R2_RT_array[0] + thisTrial.R2_duration) * 1000,1)
                else:
                    thisTrial.RTs[i] = round(thisTrial.R2_RT_array[0] * 1000,1)  
                    
    print('Trial RTs were %s ms' %thisTrial.RTs) # print RTs to console

# Define feedback function
#   Function for presenting feedback at end of a trial
def feedback(exp,stimuli,trialInfo,thisTrial,trialStimuli): 
    if exp.taskInfo['Paradigm'] == 'ARI': # use positional RTs if ARI paradigm (i.e., propn of filled bar to filling time)
        for i, stim in enumerate(trialStimuli.stimList): # loop over trial stimuli
            if trialInfo.choiceList[trialInfo.blockTrialCount-1] == 1: # if choice 1
                if i == 0:
                    L_RT = stim.size[1]/exp.advSettings['Stimulus size (cm)']*trialStimuli.fillTimes[i]*1000
                if i == 1:
                    R_RT = stim.size[1]/exp.advSettings['Stimulus size (cm)']*trialStimuli.fillTimes[i]*1000
            elif trialInfo.choiceList[trialInfo.blockTrialCount-1] == 2: # if choice 2
                if i == 2:
                    L_RT = stim.size[1]/exp.advSettings['Stimulus size (cm)']*trialStimuli.fillTimes[i]*1000
                if i == 3:
                    R_RT = stim.size[1]/exp.advSettings['Stimulus size (cm)']*trialStimuli.fillTimes[i]*1000
    elif exp.taskInfo['Paradigm'] == 'SST': # use stored RTs if SST paradigm
        if trialInfo.choiceList[trialInfo.blockTrialCount-1] == 1: # if choice 1
            L_RT = thisTrial.RTs[0]
            R_RT = thisTrial.RTs[1]
        elif trialInfo.choiceList[trialInfo.blockTrialCount-1] == 2: # if choice 2
            L_RT = thisTrial.RTs[2]
            R_RT = thisTrial.RTs[3]
    if L_RT == float("nan"): # temporarily set nans at -9999 for feedback purposes
        L_RT = -9999
    if R_RT == float("nan"):
        R_RT = -9999
    trialScore = 0 # set trial score to 0
    for i, stim in enumerate(trialStimuli.cueList): # loop over trial cues
        # left side
        if i == 0: # for left side responses
            stim.lineColor = 'Red' # set default feedback to failed
            L_score = 0        
            for f, fb in enumerate(trialInfo.targetRTs): # loop over target RTs
                if thisTrial.trialType == 1 or thisTrial.trialType == 4: # if go or stop-right
                    if abs(thisTrial.L_targetTime-L_RT) < trialInfo.targetRTs[f]:
                        L_score = trialInfo.scores[f] # assign score
                        stim.lineColor = trialInfo.feedbackColors[f] # assign feedback colour
                elif thisTrial.trialType == 2 or thisTrial.trialType == 3: # if stop-both or stop-left
                    if thisTrial.pressState[0] == 0 and thisTrial.pressState[2] == 0:
                        L_score = trialInfo.scores[2]
                        stim.lineColor = trialInfo.feedbackColors[2]
                        thisTrial.stopSuccess = 1
        elif i == 1: # repeat above for right side responses
            stim.lineColor = 'Red'
            R_score = 0    
            for f, fb in enumerate(trialInfo.targetRTs):        
                if thisTrial.trialType == 1 or thisTrial.trialType == 3:
                    if abs(thisTrial.R_targetTime-R_RT) < trialInfo.targetRTs[f]:
                        R_score = trialInfo.scores[f]
                        stim.lineColor = trialInfo.feedbackColors[f]
                elif thisTrial.trialType == 2 or thisTrial.trialType == 4: # if stop-both or stop-right
                    if thisTrial.pressState[1] == 0 and thisTrial.pressState[3] == 0: # if successfully stopped
                        R_score = trialInfo.scores[2]
                        stim.lineColor = trialInfo.feedbackColors[2]    
                        thisTrial.stopSuccess = 1
    trialScore = L_score + R_score # calculate trial score
    print('Trial score was %s'%(trialScore)) # print trialScore to console
    if exp.genSettings['Trial-by-trial feedback?'] == True: # draw feedback if option is selected
        exp.win.flip()    
        
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
            b.write('%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s\n'%(trialInfo.blockCount, trialInfo.trialCount, startTime, thisTrial.trialName, thisTrial.trialType, thisTrial.stopTime,thisTrial.L_targetTime, thisTrial.R_targetTime, trialInfo.choiceList[trialInfo.blockTrialCount-1], thisTrial.pressState[0], thisTrial.pressState[1], thisTrial.pressState[2], thisTrial.pressState[3], thisTrial.RTs[0], thisTrial.RTs[1], thisTrial.RTs[2], thisTrial.RTs[3]))

# Define ITI function
#   Function for ending the trial and running intertrial interval 
def ITI(exp, stimuli, trialStimuli):
    if exp.genSettings['Trial-by-trial feedback?'] == True: # run feedback duration if trial-by-trial feedback is enabled
        core.wait(exp.advSettings['Feedback duration (s)'])
    if exp.advSettings['Blank intertrial interval?'] == True: # if blank ITI, remove stimuli and then wait
        for s in stimuli.eStimList:
            s.setAutoDraw(False)
        for s in trialStimuli.stimList:
            s.setAutoDraw(False)
        for s in trialStimuli.cueList:
            s.lineColor = exp.advSettings['Cue color']
        exp.win.flip()
        core.wait(exp.advSettings['Intertrial interval (s)'])
    else: # if non-blank ITI, wait and then remove stimuli
        core.wait(exp.advSettings['Intertrial interval (s)'])
        for s in stimuli.eStimList:
            s.setAutoDraw(False)
        for s in trialStimuli.stimList:
            s.setAutoDraw(False)
        for s in trialStimuli.cueList:
            s.lineColor = exp.advSettings['Cue color']
        exp.win.flip()
        
# Define endBlock function
#   Function for presenting end-of-block feedback
def endBlock(exp,trialInfo,thisBlockTrials):
    print('End of block %s'%trialInfo.blockCount)
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
    
# Define endTask function
#   Function for ending the task and closing relevant serial/com ports
def endTask(exp, stimuli, trialStimuli):
    print('Ending task')
    for s in stimuli.eStimList:
        s.setAutoDraw(False)
    for s in trialStimuli.stimList:
        s.setAutoDraw(False)
    for s in trialStimuli.cueList:
        s.lineColor = exp.advSettings['Cue color']
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
