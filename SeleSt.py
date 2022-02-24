"""
Selective Stopping (SeleSt) task
    Written by Corey Wadsley* with help from Fenwick Nolan
        *Movement Neuroscience Laboratory, Department of Exercise Sciences, The University of Auckland
    
    Further information can be found at:
        https://github.com/coreywadsley/SeleSt
    
    If you use this task, please cite:
        Wadsley, Cirillo, Nieuwenhuys, & Byblow. (2022). Stopping interference in response inhibition: Behavioral
        and neural signatures of selective stopping. J Neurosci 42(2), 156-165. doi: 10.1523/JNEUROSCI.0668-21.2021

    If you have any issues, feel free to contact Corey at:
        c.wadsley@auckland.ac.nz
"""

# Some general housekeeping before we start
# import required modules
import os
from psychopy import core
from lib import SeleSt_initialize, SeleSt_run
# ensure that the relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__)) 
os.chdir(_thisDir)

#   INITIALIZE
# Here we are initializing all of the information that can change across sessions 
    # additional info for each class can be found in the SeleSt_initialize script
exp = SeleSt_initialize.Experiment_debug(_thisDir) # initialize exp class
stimuli = SeleSt_initialize.Stimuli(exp) # initialize stimuli class 
trialInfo = SeleSt_initialize.Trials(exp) # initialize trialInfo class
stopInfo = SeleSt_initialize.SSD(exp) # initialize stopInfo class

#   RUN
# Here we are running the task by looping over blocks and trials
    # additional info for each function can be found in the SeleSt_run script
for thisBlock in trialInfo.blockList: # iterate over blocks
    thisBlockTrials = SeleSt_run.Block(exp, trialInfo) # process trials in the current block
    for trial in thisBlockTrials: # iterate over trials in the current block
        print(trial)
        trialInfo.trialCount = trialInfo.trialCount + 1 # track trial number
        thisTrial = SeleSt_run.Initialize_trial(exp, trialInfo, stopInfo, trial) # set parameters of current trial
        print('Trial number %s'%(trialInfo.trialCount) + ' - ' + thisTrial.trialName) # print trial number & name to console
        trialStimuli = SeleSt_run.Start_Trial(exp,stimuli,trialInfo,thisTrial,trial) # set additional trial related parameters
        exp.win.flip() # draw stimuli at start of trial
        fixPeriod = SeleSt_run.fixationPeriod(exp,stimuli) # run fixation period
        if exp.taskInfo['Response mode'] == 'Wait-and-press': # clear events in buffer if wait-and-press version
            exp.rb.clearEvents()
        startTime = round(exp.globalClock.getTime(),1) # record trial start time and print it to the console
        print('Trial started at %s seconds'%startTime)
        trialTimer = core.CountdownTimer(exp.advSettings['Trial length (s)']) # set trial timer
        stopTimer = core.CountdownTimer(thisTrial.stopTime/1000) # set stop timer
        exp.win.callOnFlip(exp.rb.clock.reset)
        while trialTimer.getTime() > 0: # run trial while timer is positive
            SeleSt_run.runTrial(exp,stimuli,thisTrial,trialStimuli,trialTimer)
            if stopTimer.getTime() <= 0: # present stop signal when stop timer reaches 0
                SeleSt_run.stop_signal(exp,stimuli,thisTrial,trialStimuli)
            exp.win.flip() # update stimuli on every frame
        SeleSt_run.getRT(exp, thisTrial) # get RTs for current trial
        SeleSt_run.feedback(exp, stimuli, trialInfo, thisTrial, trialStimuli) # calculate response accuracy and present feedback
        SeleSt_run.staircaseSSD(exp, stopInfo, thisTrial) # staircase SSD if applicable
        SeleSt_run.saveData(exp, trialInfo, thisTrial, startTime) # save data from current trial
        SeleSt_run.ITI(exp) # run intertrial interval
        SeleSt_run.endTrial(exp,stimuli) # remove stimuli from screen
    SeleSt_run.endBlock(exp, trialInfo, thisBlockTrials) # calculate block score and present end-of-block feedback
SeleSt_run.endTask(exp, stimuli) # end the task when all blocks have been completed