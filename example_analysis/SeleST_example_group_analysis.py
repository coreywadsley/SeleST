"""
Example Selective Stopping Toolbox (SeleST) analysis
    Used when comparing performance between anticipatory and stop-signal task variants

"""

import pandas as pd
import numpy as np
import os
from scipy.stats import median_abs_deviation

datafolder = os.path.dirname(os.path.realpath(__file__))
parInfo = pd.read_csv(datafolder+'\\ex_participantInfo.csv')

n_participants = 1
participants = list(range(1,n_participants+1)) # create list of n participants
paradigms = ['ARI', 'SST'] # create list of paradigms
parCode = 'ex' # create dummy fileprefix for example

# Initialise list of DVs
avedata = {
    
    # demographics DVs
    'participant': list(), # id of participant
    'paradigm': list(), # paradigm (ARI or SST)
    'age': list(), # age of participant
    'sex': list(), # sex of participant
    'handedness': list(), # handedness of participant
    'order': list(), # order paradigms were performed (A2S, S2A)
    
    # data DVs (GG = Go-trial, SA = Stop-all trial, PS = partial-stop trial)
    'GG_success_practice': list(), # practice go success
    'GG_success': list(), # task go success
    'GG_rt_practice': list(), # practice go RT
    'GG_rt': list(), # task go RT
    'RDE': list(), # response delay effect
    'GG_rt_MAD': list(),
    'GG_L_rt': list(), # task go left RT
    'GG_R_rt': list(), # task go right RT
    'SA_success': list(), # stop success
    'PS_success': list(),
    'SA_ssd': list(), # stop-signal delay
    'PS_ssd': list(),
    'PS_si': list(), # stopping-interference
    'SA_fail_rt': list(), # fail-stop RT
    'PS_fail_rt': list(),
    'SA_ssrt_assump': list(), # ssrt assump and estimate
    'SA_ssrt': list(),
    'PS_ssrt_assump': list(),
    'PS_ssrt': list()
    
}

# Process data
for idx, part in enumerate(participants):
    for p, pdgm in enumerate(paradigms):
        
        # store demographic DVs
        print("processing " + str(part)+'_'+paradigms[p])
        avedata['participant'].append(part)
        avedata['paradigm'].append(pdgm)
        avedata['age'].append(parInfo['age'][idx])
        avedata['sex'].append(parInfo['sex'][idx])
        avedata['handedness'].append(parInfo['handedness'][idx])
        avedata['order'].append(parInfo['order'][idx])
        
        # load data
        data = pd.read_csv(datafolder+'\\'+str(parCode)+'_'+paradigms[p]+'.txt', delimiter=' ') # NOTE: parCode should be changed to part for iterative analysis
        
        # set up processing variables
        data['go_success'] = 0 # create column for go success
        data['stop_success'] = 0 # create column for stop success
        n_choices = 2 # set n of choices
        go_success = [[1,1,0,0],[0,0,1,1]]
        stop_success = [0,0,0,0]
        SL_success = [[0,1,0,0],[0,0,0,1]] # create list for stop-left success w/ right responses
        SR_success = [[1,0,0,0],[0,0,1,0]] # create list for stop-right success w/ left responses
        
        # process data (trial-wise)
        for i,trl in enumerate(data.trial): # loop over trials
            # stop success
            if data.trialType.iloc[i] == 1:
                data.stop_success.at[i] = float("nan") # set stop success to nan if go trial
            elif data.trialType.iloc[i] == 2 and list(data.loc[i, 'L_press':'R2_press']) == stop_success: # set stop-all as successful if no keys were pressed
                data.stop_success.at[i] = 1
            for c,x in enumerate([1]*n_choices): # loop over choices
                if (data.trialType.iloc[i] == 3 and list(data.loc[i,'L_press':'R2_press']) == stop_success) or (data.trialType.iloc[i] == 3 and list(data.loc[i,'L_press':'R2_press']) == SL_success[c]): # stop-left success
                    data.stop_success.at[i] = 1
                elif (data.trialType.iloc[i] == 4 and list(data.loc[i,'L_press':'R2_press']) == stop_success) or (data.trialType.iloc[i] == 4 and list(data.loc[i,'L_press':'R2_press']) == SR_success[c]): # stop-right success
                    data.stop_success.at[i] = 1           
                # GO SUCCESS
                if data.trialType.iloc[i] == 1 and data.Choice.iloc[i] == c+1 and list(data.loc[i,'L_press':'R2_press']) == go_success[c]: # go success if correct keys were pressed
                    data.go_success.at[i] = 1
                elif data.trialType.iloc[i] > 1: # set go_success as nan if stop trial
                    data.go_success.at[i] = float("nan")
                    
        # Calculate dependent measures for each trial type
        #   NOTE: A straight-forward analysis pipeline is presented below where
        #         each measure is calculated separately. 
    
        # Go trials
        d = data[(data["trialType"]==1) & (data["block"]==-1)] # grab data from go-only block
        avedata['GG_success_practice'].append(round(sum(d.go_success)/len(d.go_success)*100,2))
        avedata['GG_rt_practice'].append(round(np.mean(pd.concat([d.loc[d['go_success']==1].L_RT, d.loc[d['go_success']==1].L2_RT, d.loc[d['go_success']==1].R_RT, d.loc[d['go_success']==1].R2_RT])),2))
        d = data[(data["trialType"]==1) & (data["block"]>0)] # grab data from go/stop task blocks
        avedata['GG_success'].append(round(sum(d.go_success)/len(d.go_success)*100,2))
        avedata['GG_rt'].append(round(np.mean(pd.concat([d.loc[d['go_success']==1].L_RT, d.loc[d['go_success']==1].L2_RT, d.loc[d['go_success']==1].R_RT, d.loc[d['go_success']==1].R2_RT])),2))
        avedata['RDE'].append(avedata['GG_rt'][idx*2+p] - avedata['GG_rt_practice'][idx*2+p])
        avedata['GG_rt_MAD'].append(round(median_abs_deviation(pd.concat([d.loc[d['go_success']==1].L_RT, d.loc[d['go_success']==1].L2_RT, d.loc[d['go_success']==1].R_RT, d.loc[d['go_success']==1].R2_RT]),nan_policy='omit'),2))

        avedata['GG_L_rt'].append(round(np.mean(pd.concat([d.loc[d['go_success']==1].L_RT, d.loc[d['go_success']==1].L2_RT])),2))
        avedata['GG_R_rt'].append(round(np.mean(pd.concat([d.loc[d['go_success']==1].R_RT, d.loc[d['go_success']==1].R2_RT])),2))
 
        trialLbls = ['SS', 'GS', 'SG'] # stop trial labels
        data['SI'] = float("nan") # set si variable as nan
        for i, trl in enumerate(data.trial):
            if data.trialType.iloc[i] == 3: # stop-left trials
                if data.Choice.iloc[i] == 1: # choice 1
                    data.SI.at[i] = data.R_RT.iloc[i] - avedata['GG_R_rt'][idx*2+p]
                elif data.Choice.iloc[i] == 2: # choice 2
                    data.SI.at[i] = data.R2_RT.iloc[i] - avedata['GG_R_rt'][idx*2+p]
            elif data.trialType.iloc[i] == 4: # stop-right trials
                if data.Choice.iloc[i] == 1:
                    data.SI.at[i] = data.L_RT.iloc[i] - avedata['GG_L_rt'][idx*2+p]
                elif data.Choice.iloc[i] == 2:
                    data.SI.at[i] = data.L2_RT.iloc[i] - avedata['GG_L_rt'][idx*2+p]
                    
        trialLbls = ['SA', 'PS']
        for i, t in enumerate(trialLbls):           
            if i == 0:
                d = data[(data["trialType"]==2) & (data["block"]>0)]
            elif i == 1:
                d = data[(data["trialType"]>2) & (data["block"]>0)]
            avedata[trialLbls[i]+'_'+'success'].append(round(sum(d.stop_success)/len(d.stop_success)*100,2))
            avedata[trialLbls[i]+'_ssd'].append(round(np.mean(d.stopTime)))
            if avedata['paradigm'][idx*2+p] == 'ARI':
                avedata[trialLbls[i]+'_'+'ssd'][idx*2+p] = abs(avedata[trialLbls[i]+'_'+'ssd'][idx*2+p] - 800)
    
            # Fail-stop RT (ms)
            if i == 0:
                avedata[trialLbls[i]+'_'+'fail_rt'].append(round(np.mean(pd.concat([d.loc[d['stop_success']==0].L_RT, d.loc[d['stop_success']==0].L2_RT, d.loc[d['stop_success']==0].R_RT, d.loc[d['stop_success']==0].R2_RT])),2))
            elif i == 1:
                avedata[trialLbls[i]+'_'+'fail_rt'].append(round(np.mean(pd.concat([d.loc[d['stop_success']==0].L_RT, d.loc[d['stop_success']==0].L2_RT])),2))
            elif i == 2:
                avedata[trialLbls[i]+'_'+'fail_rt'].append(round(np.mean(pd.concat([d.loc[d['stop_success']==0].R_RT, d.loc[d['stop_success']==0].R2_RT])),2))
            
            # Stopping-interference effect (ms)
            if i > 0:
                avedata[trialLbls[i]+'_si'].append(round(np.mean(d.loc[d['stop_success']==1].SI)))
          
        # Grab stop data for trial-by-trial SI analyses
        stopdata = data[data.trialType>2]
        stopdata = stopdata[stopdata.block>0]
        stopdata['id'] = part
        stopdata['paradigm'] = pdgm
        stopdata['age'] = parInfo['age'][idx]
        stopdata['sex'] = parInfo['sex'][idx]        
        if idx == 0 and p == 0:
            sdata = stopdata
        else:
            sdata = sdata.append(stopdata)
                      
        # Stop-signal reaction time analyses
        rt = data[(data.trialType==1) & (data.block>0)] # grab go RT data
        rt = rt.reset_index(drop=True)
        rt["goRT"] = 0 # create go RT variable
        for i, trl in enumerate(rt.trial): # iterate over trials
            if rt.Choice.iloc[i] == 1: # assign maximum RT value to missing responses
                if rt.L_press.iloc[i] == 0:
                    rt.L_RT.at[i] = 1250
                if rt.R_press.iloc[i] == 0:
                    rt.R_RT.at[i] = 1250
                rt.goRT.at[i] = (rt.L_RT.iloc[i] + rt.R_RT.iloc[i])/2 # mean go RT
            elif rt.Choice.iloc[i] == 2:
                if rt.L2_press.iloc[i] == 0:
                    rt.L2_RT.at[i] = 1250
                if rt.R2_press.iloc[i] == 0:
                    rt.R2_RT.at[i] = 1250
                rt.goRT.at[i] = (rt.L2_RT.iloc[i] + rt.R2_RT.iloc[i])/2 # mean go RT          
        rt = rt.sort_values(by=['goRT']) # sort rt data by goRT
        rt = rt.reset_index(drop=True) # reset indices
        for i, t in enumerate(trialLbls): # loop over SA and PS trials   
            if avedata[trialLbls[i]+'_'+'fail_rt'][idx*2+p] < avedata['GG_rt'][idx*2+p]:
                avedata[trialLbls[i]+'_'+'ssrt_assump'].append(1)
            else:
                avedata[trialLbls[i]+'_'+'ssrt_assump'].append(0)
            n = int(round(len(rt)*avedata[trialLbls[i]+'_'+'success'][idx*2+p]/100,0))
            avedata[trialLbls[i]+'_'+'ssrt'].append(abs(rt['goRT'].iloc[n] - avedata[trialLbls[i]+'_'+'ssd'][idx*2+p]))
            if p == 0:
                avedata[trialLbls[i]+'_'+'ssrt'][idx*2+p] = 800 - avedata[trialLbls[i]+'_'+'ssrt'][idx*2+p]
        
# save data
avedata = pd.DataFrame(avedata)
file = datafolder + '\\SeleSt_group_data.csv'
avedata.to_csv(file,index=False)
