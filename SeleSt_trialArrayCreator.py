"""
Selective Stopping (SeleSt) task - Trial Array Creator

    Written by Fenwick Nolan with help from Corey Wadsley

    Script used to generate trials files that can be imported into SeleSt. Intructions for
    use can be found in SeleSt_guide.pdf or by following the comments in the script.
    
    We recommend creating a new file when modifying this script.     
"""

# Some general housekeeping before we start
# import required modules
from __future__ import absolute_import, division
import numpy as np  # whole numpy lib is available, prepend 'np.'
import os  # handy system and path functions
import pandas as pd
# ensure that the relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

#---------------------------------------------------------------------------
#
#   GENERAL FILE INFORMATION 
#
#---------------------------------------------------------------------------

# Here we are setting the name of the file and the number of participants to generate trials files for.
# NOTE: participant number will be appended to the filename and exported as a csv file (e.g., 'example_trials_1.csv')
if not os.path.exists(_thisDir + os.sep +'conditions/'): # create conditions directory if it doesn't exist
    print('Conditions folder did not exist, making one in current directory')
    os.makedirs(_thisDir + os.sep +'conditions/')
filePath = _thisDir + os.sep + u'conditions//' # file path to export files to (default is conditions but this can be modified)
fileName = 'example_trials' # name of file
n_participants = 1 # number of participants to generate trials files for

# Here you can set the randomisation options you would like to enable (True) or disable (False)
randomiseTrials = True # completely randomise the order of trials within a block
forceGoStart = True # make sure every block starts with x number of go trials
n_forcedGo = 3 # set this to the number of go trials you would like at the start of every block

# Here we are setting the number of blocks we would like to create (generated from the trial information below)
# NOTE: the number set in taskInfo from SeleSt_initialise.Experiment needs to match the number below
n_blocks = 12

#---------------------------------------------------------------------------
#
#   SET UP TRIAL TYPES (CONDITIONS) AND NUMBER OF REPEATS 
#
#---------------------------------------------------------------------------

# Here we are setting up each of our trial types and the respective number of repeats per block
# NOTE: the default script includes 4 trial types, but additional trial types can be included by
#       including additional trial dictionaries to the trialList. Target times are set relative
#       for ARI paradigms. If making trial array for SST then targetTime should be set to
#       ~300 ms.

# Each trial type is stored as a dictionary with the following terms:
    
    # n_repeats: number of times to repeat the trial type per block
    # trialName: here you can label the trial type (e.g., 'go_TMS')
    # trialType: here we set the trial type (1 = Go, 2 = stop-both, 3 = stop-left, 4 = stop-right)
    # ssd: here we are assigning a trialType a stop-signal delay to use from stopTimeArray in SeleSt_initialize.SSD
    # stop_color: colour of the stop signal
    # L_cue_color: colour of the L cue
    # R_cue_color: colour of the R cue
    # L_targetTime: target time for L response (ARI: influnces speed of filling bar)
    # R_targetTime: same as above for R response

# Additional variables (e.g., L_targetTime & R_targetTime) can easily be included by inserting an additional 
# variable to the dictionary and adding the variable to SeleSt_run.Start_trial

# Create an empty dataframe with relevant variables
# NOTE: column names should match the names within the trialList dictionaries
trialTable = pd.DataFrame(columns=[
    'n_repeats',
    'trialName',
    'trialType',
    'ssd',
    'go_color',
    'stop_color',
    'L_cue_color',
    'R_cue_color'
#    'L_targetTime',
#    'R_targetTime'
    ])

trialList = [ # list of trial types

# Go trials
{
 'n_repeats': 24,
 'trialName': 'Go',
 'trialType': 1,
 'ssd': 0,
 'go_color': 'black',
 'stop_color': 'black',
 'L_cue_color': 'black',
 'R_cue_color': 'black'
 },
# Stop-all trials
{
 'n_repeats': 4,
 'trialName': 'stop_all',
 'trialType': 2,
 'ssd': 1,
 'go_color': 'black',
 'stop_color': 'cyan',
 'L_cue_color': 'black',
 'R_cue_color': 'black'
 },
# Stop-left trials
{
 'n_repeats': 4,
 'trialName': 'stop_left',
 'trialType': 3,
 'ssd': 2,
 'go_color': 'black',
 'stop_color': 'cyan',
 'L_cue_color': 'black',
 'R_cue_color': 'black'
 },
# Stop-right trials
{
 'n_repeats': 4,
 'trialName': 'stop_right',
 'trialType': 4,
 'ssd': 3,
 'go_color': 'black',
 'stop_color': 'cyan',
 'L_cue_color': 'black',
 'R_cue_color': 'black'
 }

]

#---------------------------------------------------------------------------
#
#   CREATE AND EXPORT THE TRIAL FILES 
#
#---------------------------------------------------------------------------

# Here we are creating a standard block (list of trials w/ trialType details)
for i in range(0,len(trialList)): # iterate over no. of trial types
    trialList_temp = (np.array(trialList[i]['n_repeats']*[i])).tolist() # create temporary list w/ n_repeats for a trial type
    for j in trialList_temp: # iterate over no. of repeats for particular trial type
        trialTable = trialTable.append(trialList[i],ignore_index=True) # append dictionary info for trialType to trialTable
del(trialTable['n_repeats']) # remove n_repeats column from trialTable

# Here we are creating unique trials files by iterating over n_participants & n_blocks
# Each block will be randomised individually and then concatenated to make a complete trial table
#   e.g., 10 blocks * 36 trials = 360 trials
for j in range(1,n_participants + 1):  # iterate over desired number of participants
    for n in range(1,n_blocks + 1): # iterate over desired number of blocks
                
        # Randomise the list of trials if the option is enabled
        if randomiseTrials == True:
            np.random.shuffle(trialTable.values)
                   
        # Force x amount of go trials at the start of every block, if the option is enabled        
        if forceGoStart == True:
            forceGoStart_shuffle = True # enable shuffling within this iteration
            while forceGoStart_shuffle == True:
                trialTableTemp = trialTable.iloc[:n_forcedGo] # create temporary trialTable based on n_forcedGo
                if trialTableTemp['trialType'].sum() > n_forcedGo: # randomise trials if n_forcedGo criterion is not meant (NOTE: this works as trialType = 1 for go trials)
                    np.random.shuffle(trialTable.values)
                    trialTableTemp = trialTable.iloc[:n_forcedGo]
                elif trialTableTemp['trialType'].sum() <= n_forcedGo: # break the loop if the n_forcedGo criterion is met
                      break
                      trialTable = trialTable.append(trialTableTemp,ignore_index=True) # Adds trialTableTemp to trialTable 
                      
        if n == 1:
            trialTable_complete = trialTable # create the complete trialTable if we are within the first iteration
        if n > 1:
            trialTable_complete = pd.concat([trialTable_complete, trialTable], ignore_index = True) # append to the complete trialTable for subsequent blocks            
    print(trialTable_complete) # print trial table to console
    
    # Export trialTable to a csv file based on the information above and n_participants
    trialTable_complete.to_csv(filePath + fileName + '_' + str(j) + '.csv', index=False)    

    # Reset the trialTable_complete dataframe
    trialTable_complete = trialTable_complete[0:0]        