"""
Selective Stopping (SeleSt) analysis

"""
import pandas as pd
import numpy as np
import os

def standard(_thisDir, exp):
    aveData = pd.DataFrame(data = [{
        'id': exp.taskInfo['Participant ID'],
        'age': exp.taskInfo['Age (years)'],
        'sex': exp.taskInfo['Sex'],
        'handedness': exp.taskInfo['Handedness'],
        'paradigm': exp.taskInfo['Paradigm'],
        'RT type': exp.taskInfo['RT type']
        }])
    
    data = pd.read_csv(exp.Output+'.txt', delimiter=' ')

    # calculate go and stop success
    #   NOTE: go success ='s pressing the correct response options
    #         stop success ='s witholding correct responses
    data['go_success'] = 0 # create column for go success
    data['stop_success'] = 0 # create column for go success
    n_choices = 2 # set n of choices
    go_success = [[1,1,0,0],[0,0,1,1]]
    stop_success = [0,0,0,0]
    SL_success = [[0,1,0,0],[0,0,0,1]] # create list for stop-left success w/ right responses
    SR_success = [[1,0,0,0],[0,0,1,0]] # create list for stop-right success w/ left responses
    for i,t in enumerate(data.trial): # loop over trials
        # Stop success
        if data.trialType.iloc[i] == 1: # set stop_success as nan if go trials
            data.stop_success.at[i] = float("nan")    
        elif data.trialType.iloc[i] == 2 and list(data.loc[i,'L_press':'R2_press']) == stop_success: # set stop-all as successful if no keys were pressed
            data.stop_success.at[i] = 1
        for c,x in enumerate([1]*n_choices): # loop over choices     
            if (data.trialType.iloc[i] == 3 and list(data.loc[i,'L_press':'R2_press']) == stop_success) or (data.trialType.iloc[i] == 3 and list(data.loc[i,'L_press':'R2_press']) == SL_success[c]): # stop-left success
                data.stop_success.at[i] = 1
            elif (data.trialType.iloc[i] == 4 and list(data.loc[i,'L_press':'R2_press']) == stop_success) or (data.trialType.iloc[i] == 4 and list(data.loc[i,'L_press':'R2_press']) == SR_success[c]): # stop-right success
                data.stop_success.at[i] = 1           
            # Go success
            if data.trialType.iloc[i] == 1 and data.Choice.iloc[i] == c+1 and list(data.loc[i,'L_press':'R2_press']) == go_success[c]: # go success if correct keys were pressed
                data.go_success.at[i] = 1
            elif data.trialType.iloc[i] > 1: # set go_success as nan if stop trial
                data.go_success.at[i] = float("nan")

    # Calculate dependent measures for each trial type
    #   NOTE: A straight-forward analysis pipeline is presented below where
    #         each measure is calculated separately. 
    
    # Go trials
    trialLbls = ['Go', 'Go'] # set labels
    addLbls = ['_practice', ''] # set additional labels
    for i, t in enumerate(trialLbls): # iterate over labels
        if i == 0:
            d = data[(data["trialType"]==1) & (data["block"]==-1)] # grab data from go-only block
        elif i == 1:
            d = data[(data["trialType"]==1) & (data["block"]>0)] # grab data from go/stop blocks
            
        # Go trial success (%)
        aveData[trialLbls[i]+'_'+'success'+addLbls[i]] = round(sum(d.go_success)/len(d.go_success)*100,2) # calculate go trial success
        
        # Response times (ms)
        aveData[trialLbls[i]+'_'+'L_RT'+addLbls[i]] = round(np.mean(pd.concat([d.loc[d['go_success']==1].L_RT, d.loc[d['go_success']==1].L2_RT])),2) # calculate left RT
        aveData[trialLbls[i]+'_'+'R_RT'+addLbls[i]] = round(np.mean(pd.concat([d.loc[d['go_success']==1].R_RT, d.loc[d['go_success']==1].R2_RT])),2) # calculate right RT
        aveData[trialLbls[i]+'_'+'RT'+addLbls[i]] = round(np.mean(pd.concat([d.loc[d['go_success']==1].L_RT, d.loc[d['go_success']==1].L2_RT, d.loc[d['go_success']==1].R_RT, d.loc[d['go_success']==1].R2_RT])),2) # calculate RT collapsed across hands
    
    # Response delay effect (ms) ()
    aveData['RDE'] = aveData['Go_RT'] - aveData['Go_RT_practice']
    
    # Stop trials
    trialLbls = ['SA', 'SL', 'SR']
    
    # Calculate stopping-interference on a trial-by-trial basis
    data['SI'] = float("nan") # set SI variable as nan
    for i, t in enumerate(data.trial): # loop over trials
        if data.trialType.iloc[i] == 3: # stop-left trials
            if data.Choice.iloc[i] == 1: # choice 1
                data.SI.at[i] = data.R_RT.iloc[i] - aveData['Go_R_RT']
            elif data.Choice.iloc[i] == 2: # choice 2
                data.SI.at[i] = data.R2_RT.iloc[i] - aveData['Go_R_RT']
        elif data.trialType.iloc[i] == 4: # stop-right trials
            if data.Choice.iloc[i] == 1:
                data.SI.at[i] = data.L_RT.iloc[i] - aveData['Go_L_RT']
            elif data.Choice.iloc[i] == 2:
                data.SI.at[i] = data.L2_RT.iloc[i] - aveData['Go_L_RT']
                
    for i, t in enumerate(trialLbls):
        d = data[(data["trialType"]==i+2) & (data["block"]>0)]
        
        # Stop-success (%)
        aveData[trialLbls[i]+'_'+'stopSuccess'] = round(sum(d.stop_success)/len(d.stop_success)*100,2)
        
        # Stop-signal delay (ms)
        aveData[trialLbls[i]+'_'+'ssd'] = round(np.mean(d.stopTime))
        if aveData['paradigm'][0] == 'ARI':
            aveData[trialLbls[i]+'_'+'ssd'] = aveData[trialLbls[i]+'_'+'ssd'] - 800
            
        # Fail-stop RT (ms)
        if i == 0:
            aveData[trialLbls[i]+'_'+'failStop_RT'] = round(np.mean(pd.concat([d.loc[d['stop_success']==0].L_RT, d.loc[d['stop_success']==0].L2_RT, d.loc[d['stop_success']==0].R_RT, d.loc[d['stop_success']==0].R2_RT])),2)
        elif i == 1:
            aveData[trialLbls[i]+'_'+'failStop_RT'] = round(np.mean(pd.concat([d.loc[d['stop_success']==0].L_RT, d.loc[d['stop_success']==0].L2_RT])),2)
        elif i == 2:
            aveData[trialLbls[i]+'_'+'failStop_RT'] = round(np.mean(pd.concat([d.loc[d['stop_success']==0].R_RT, d.loc[d['stop_success']==0].R2_RT])),2)
    
        # Fail-stop contra RT (ms)
        if i == 1:
            aveData[trialLbls[i]+'_'+'failStopContra_RT'] = round(np.mean(pd.concat([d.loc[d['stop_success']==1].R_RT, d.loc[d['stop_success']==0].R2_RT])),2)
        elif i == 2:
            aveData[trialLbls[i]+'_'+'failStopContra_RT'] = round(np.mean(pd.concat([d.loc[d['stop_success']==1].L_RT, d.loc[d['stop_success']==0].L2_RT])),2)  
        
        # Successful-stop contra RT (ms)
        if i == 1:
            aveData[trialLbls[i]+'_'+'succStopContra_RT'] = round(np.mean(pd.concat([d.loc[d['stop_success']==1].R_RT, d.loc[d['stop_success']==1].R2_RT])),2)
        elif i == 2:
            aveData[trialLbls[i]+'_'+'succStopContra_RT'] = round(np.mean(pd.concat([d.loc[d['stop_success']==1].L_RT, d.loc[d['stop_success']==1].L2_RT])),2)
            
        # Stopping-interference effect (ms)
        if i == 1:
            aveData[trialLbls[i]+'_'+'SI'] = round(np.mean(d.loc[d['stop_success']==1].SI))
        elif i == 2:
            aveData[trialLbls[i]+'_'+'SI'] = round(np.mean(d.loc[d['stop_success']==1].SI)) 
            
        # Conflict-interference effect (ms)
        if i == 1:
            aveData[trialLbls[i]+'_'+'CI'] = round(np.mean(d.loc[d['stop_success']==0].SI))
        elif i == 2:
            aveData[trialLbls[i]+'_'+'CI'] = round(np.mean(d.loc[d['stop_success']==0].SI))

    file = _thisDir + os.sep + 'data/SeleSt_%s' % (exp.taskInfo['Participant ID']) + '_processed.csv'
    data.to_csv(file,index=False)
    file = _thisDir + os.sep + 'data/SeleSt_%s' % (exp.taskInfo['Participant ID']) + '_averages.csv'
    aveData.to_csv(file,index=False)

    return aveData
