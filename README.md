# Selective Stopping Toolbox (SeleST)

Developed by Corey Wadsley<sup>1</sup> with help from Fenwick Nolan.

<sup>1</sup>*Movement Neuroscience Laboratory, Department of Exercise Sciences, The University of Auckland*

___

Welcome! The Selective Stopping Toolbox (SeleST) allows response inhibition to be assessed in nonselective and selective stopping contexts with either stop-signal or anticipatory response inhibition paradigms. SeleST was developed using freely available Python-based PsychoPy software that provides high-quality stimulus and response timing.

An overview and recommendations for use of SeleST is provided in the following article - please cite it if you make use of SeleST.

xxx

- For a review of selective stopping, see [Wadsley et al., 2022, _J Neurosci_](https://doi.org/10.1523/JNEUROSCI.0668-21.2021)

- Feel free to direct questions or feedback to Corey's email (c.wadsley@auckland.ac.nz)



## General information

- [PsychoPy](https://psychopy.org/) is required for SeleST. PsychoPy can be installed standalone or within a Python IDE (e.g., Spyder). Instructions for installation can be found on the PsychoPy website. Once installed, the task can be run using the 'SeleST.py' file.

- SeleST makes use of the object-oriented basis of Python. Most parameters can be modified using a graphical user interface (GUI) presented whenever SeleST is run (***A***). Advanced settings can be set through subsequent GUIs by selecting the ‘Change general settings?’ option. Advanced users can also insert modified versions of the various functions that handle specific aspects of the task. The default options of SeleST support use simple or choice variants of multicomponent SST and ARI pardigms (***B***).

![SeleST_defaults](/instructions/SeleST_defaults.png)

- SeleST supports use of nonselective stop-all and selective partial-stop trials. Below is an example schematic of primary trial types during choice variants of the anticipatory response inhibition (ARI) and stop-signal-task (SST). Participants are presented with four empty indicators during fixation. A multicomponent ‘go’ response is cued for either the inner (L1 & R1, *depicted*) or outer (L2 & R2) indicators by presenting the go-signal (ARI: filling bars reaching target; SST: indicator turning black). Nonselective stopping is assessed by presenting a stop-signal (indicator turning cyan) on both the selected indicators. Selective stopping is assessed by presenting a stop-signal on either the left or the right indicator while the other continues as initially cued by the go-signal. Advanced trial types (e.g., varying cue colour) can be created using the SeleST_trialArrayCreator.py script. 

![SeleST_defaults](/instructions/SeleST_choiceTrialTypes.png)

### Status updates

- Preparing for initial release
