# taste task. 1/25/2018
#this is the reversal learning task for BEVBITS (formerly Juice)
#water is pump 0
#sweet is pump 1
#notsweet is pump 2
#TR 2 sec
#the pkl file contains all study data as a back up including what files were used, useful for sanity checks
#the csv file is easier to read
#the log file also has onsets, but it has the time from when the .py file was initalized more accurate should be used for analysis
#from psychopy import visual, core, data, gui, event, data, logging
import csv
import time
import serial
import numpy as N
import sys,os,pickle
import datetime
import exptutils
from exptutils import *
<<<<<<< HEAD
from random import shuffle
import pdb


=======
#import pdb
from random import shuffle
>>>>>>> ecd4adaaa729536d59cc9007f6ed256ad1fbc4bc

monSize = [800, 600]
info = {}
info['fullscr'] = False
info['port'] = '/dev/tty.usbserial'
info['participant'] = 'test'
info['run']='run02'
info['session']='pre'
info['flavor']='SL' #Either CO or SL
info['computer']=(os.getcwd()).split('/')[2]
dlg = gui.DlgFromDict(info)
if not dlg.OK:
    core.quit()
########################################
subdata={}

subdata['completed']=0
subdata['cwd']=os.getcwd()

clock=core.Clock()
datestamp=datetime.datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
subdata['datestamp']=datestamp
subdata['expt_title']='bevbits_reversal'

subdata['response']={}
subdata['score']={}
subdata['rt']={}
subdata['stim_onset_time']={}
subdata['stim_log']={}
subdata['is_this_SS_trial']={}
subdata['SS']={}
subdata['broke_on_trial']={}
subdata['simulated_response']=False

subdata['onset']='/Users/'+info['computer']+'/Documents/Bev_Task/rev_onset_files/onsets_'+info['run']
subdata['jitter']='/Users/'+info['computer']+'/Documents/Bev_Task/rev_onset_files/jitter_'+info['run']
subdata['conds']='/Users/'+info['computer']+'/Documents/Bev_Task/rev_onset_files/conds_'+info['run']
subdata['quit_key']='q'

#######################################
dataFileName='/Users/'+info['computer']+'/Documents/Output/%s_%s_%s_subdata.log'%(info['participant'],info['session'],subdata['datestamp'])
logging.console.setLevel(logging.INFO)
logfile=logging.LogFile(dataFileName,level=logging.DATA)
ratings_and_onsets = []
#######################################
# Serial connection and commands setup
ser = serial.Serial(
                    port=info['port'],
                    baudrate=19200,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS
                   )
if not ser.isOpen():
    ser.open()
#
time.sleep(1)

#global settings
diameter=26.59
mls_sweet=3.0
mls_unsweet=3.0
mls_H2O=3.0
mls_rinse=1.0
delivery_time=6.0
cue_time=2.0
wait_time=2.0
rinse_time=3.0

str='\r'
rate_sweet = mls_sweet*(3600.0/delivery_time)  # mls/hour 300
rate_unsweet = mls_unsweet*(3600.0/delivery_time)  # mls/hour 300
rate_H2O = mls_H2O*(3600.0/delivery_time)  # mls/hour 300
rate_rinse = mls_rinse*(3600.0/rinse_time)  # mls/hour 300
#
pump_setup = ['0VOL ML\r', '1VOL ML\r', '2VOL ML\r']
pump_phases=['0PHN01\r','1PHN01\r', '2PHN01\r','0CLDINF\r','1CLDINF\r','2CLDINF\r','0DIRINF\r','1DIRINF\r','2DIRINF\r','0RAT%iMH\r'%rate_H2O,'1RAT%iMH\r'%rate_sweet,'2RAT%iMH\r'%rate_unsweet,'0VOL%i%s'%(mls_H2O,str), '1VOL%i%s'%(mls_sweet,str),'2VOL%i%s'%(mls_unsweet,str),'0DIA%.2fMH\r'%diameter,'1DIA%.2fMH\r'%diameter, '2DIA%.2fMH\r'%diameter]
pump_phases2=['0PHN02\r','0CLDINF\r','0DIRINF\r','0RAT%iMH\r'%rate_rinse,'0VOL%i%s'%(mls_rinse,str), '0DIA%.2fMH\r'%diameter]



for c in pump_setup:
    ser.write(c)
    time.sleep(.05)


# HELPER FUNCTIONS
def show_instruction(instrStim):
    # shows an instruction until a key is hit.
    while True:
        instrStim.draw()
        win.flip()
        if len(event.getKeys()) > 0:
            break
        event.clearEvents()


def show_stim(stim, seconds):
    # shows a stim for a given number of seconds
    for frame in range(60 * seconds):
        stim.draw()
        win.flip()
        
def check_for_quit(subdata,win):
    k=event.getKeys()
    print 'checking for quit key %s'%subdata['quit_key']
    print 'found:',k
    if k.count(subdata['quit_key']) >0:# if subdata['quit_key'] is pressed...
        print 'quit key pressed'
        return True
    else:
        return False

def tastes(params):
    for c in params:
        ser.write(c)
        time.sleep(.05)


 MONITOR
set the window size as win 
win = visual.Window(monSize, fullscr=info['fullscr'],
                    monitor='testMonitor', units='deg')

visual_stim1=visual.ImageStim(win, image=N.zeros((300,300)),pos=(0.25,0), size=(0.25,0.25),units='height')
visual_stim2=visual.ImageStim(win, image=N.zeros((300,300)),pos=(-0.25,0), size=(0.25,0.25),units='height')

# STIMS
fixation_text = visual.TextStim(win, text='+', pos=(0, 0), height=2)

scan_trigger_text = visual.TextStim(win, text='Waiting for scan trigger...', pos=(0, 0))
#ImageStim(win, image=None, mask=None, units='', pos=(0.0, 0.0), size=None, ori=0.0, color=(1.0, 1.0, 1.0), colorSpace='rgb', contrast=1.0, opacity=1.0, depth=0, interpolate=False, flipHoriz=False, flipVert=False, texRes=128, name=None, autoLog=None, maskParams=None)
tastes(pump_phases)


#####################
#load in onset files#

onsets=[]
f=open(subdata['onset'],'r')
x = f.readlines()
for i in x:
    onsets.append(i.strip())

onsets=[float(i) for i in onsets]
print(onsets, 'onsets')

jitter=[]
g=open(subdata['jitter'],'r')
y = g.readlines()
for i in y:
    jitter.append(i.strip())
    
jitter=[float(i) for i in jitter]
print(jitter, 'jitter')

trialcond=N.loadtxt(subdata['conds'], dtype='int')
print(trialcond,'trial conditions')

ntrials=len(trialcond)
pump=N.zeros(ntrials)

# specify lists of stimulus positions and their corresponding responses:
<<<<<<< HEAD
positions = [[0.0, -0.25], [0.0, 0.25]] #possible positions
pump[trialcond==1]=1 #sweet pump ## possible tastes
pump[trialcond==2]=2 #sweet pump
stim_images=['CO.jpg','UCO.jpg'] ## possible logos

print(pump)
=======
#set contingency that the sweet is rewarding
positions = [(0.25,0), (-0.25,0)]
stim_images=['sweet.jpg','unsweet.jpg']
pump_responses = [1, 2] 
>>>>>>> ecd4adaaa729536d59cc9007f6ed256ad1fbc4bc

# create a list of indices to those lists, which will
# get shuffled on each trial:
indices = [0, 1]
<<<<<<< HEAD

# randomise locations for this trial:
shuffle(indices)

#matchPos = positions[indices[0]]
#mis1Pos = positions[indices[1]]
#mis2Pos = positions[indices[2]]
#mis3Pos = positions[indices[3]]

# get the corresponding correct response:
#corrAns = responses[indices[0]]

#    pump zero is water, pump 1 is sweet, pump 2 is unsweet
#    these need to match the onset files!

#pump[trialcond==0]=0 #water pump
#pump[trialcond==1]=1 #sweet pump
#pump[trialcond==2]=2 #unsweet pump
#

#trialcond=N.zeros(24).astype('int')
#
#trialcond[0:8]=0     # water cue, water delivery
#trialcond[8:12]=1    # water cue, juice delivery
#trialcond[12:20]=2   # juice cue, juice delivery
#trialcond[20:24]=3   # juice cue, water delivery
#stim_images=['bottled_water.jpg','bottled_water.jpg','tampico.jpg','tampico.jpg']
#ntrials=len(trialcond)
#pump=N.zeros(ntrials)
#
#N.random.shuffle(trialcond)
#
#



=======
pos_ind= [0,1]
# randomise locations for this trial:
#only those things with the indices will be pairs and shuffled

for i in trialcond:
    shuffle(indices)
    shuffle(pos_ind)
    print("this is the image "+stim_images[indices[i]]+" this is the pump %i this is the position "%(pump_responses[indices[i]], ))
    print(positions[pos_ind[i]])
>>>>>>> ecd4adaaa729536d59cc9007f6ed256ad1fbc4bc

#if info['flavor']=='CO':
#    pump[trialcond==1]=1 #sweet pump
#    stim_images=['CO.jpg','UCO.jpg']
#else:
#    stim_images=['water.jpg', 'SL.jpg', 'USL.jpg']
#
subdata['trialdata']={}

            
"""
    The main run block!
"""

def run_block():

    # Await scan trigger
    while True:
        scan_trigger_text.draw()
        win.flip()
        if 'o' in event.waitKeys():
            logging.log(logging.DATA, "start key press")
            break
        event.clearEvents()

    clock=core.Clock()
    t = clock.getTime()
    ratings_and_onsets.append(['fixation',t])
    show_stim(fixation_text, 8)  # 8 sec blank screen with fixation cross
    t = clock.getTime()
    clock.reset()
    ratings_and_onsets.append(['start',t])
    #logging.log(logging.DATA, "start")
    for trial in range(ntrials):
        if check_for_quit(subdata,win):
            exptutils.shut_down_cleanly(subdata,win)
            sys.exit()
        
        trialdata={}
        trialdata['onset']=onsets[trial]
        #shuffle the positions
        shuffle(positions)
        visual_stim1=visual.ImageStim(win, image=N.zeros((300,300)),pos=positions[0], size=(0.25,0.25),units='height')
        visual_stim2=visual.ImageStim(win, image=N.zeros((300,300)),pos=positions[1], size=(0.25,0.25),units='height')
        #set which image is which
        shuffle(indices)
        visual_stim1.setImage(stim_images[indices[0]])#set which image appears
        visual_stim2.setImage(stim_images[indices[1]])#set which image appears
        
        #which is sweet?
        message=visual.TextStim(win, text='Which is Sweet?',pos=(0,5))
        
        print trial
#        print 'condition %d'%trialcond[trial]
        print("this is the visual_stim1 is %s"%(stim_images[indices[0]]))
        print("visual_stim1 is at ")
        print(positions[0])
#        print 'showing image: %s'%stim_images[trialcond[trial]]
        t = clock.getTime()
        ratings_and_onsets.append(["image=%s"%stim_images[trialcond[trial]],t])
        visual_stim1.draw()#making image of the logo appear
        visual_stim2.draw()#making image of the logo appear
        message.draw()
        logging.log(logging.DATA, "image=%s and image=%s"%stim_images[trialcond[trial]],stim_images[trialcond[trial]])
        
        if buttonPressButton.keys == 'space':
            visual_stim1.setImage(stim_images[trialcond[trial]])#set which image appears
            visual_stim2.setImage(stim_images[trialcond[trial]])#set which image appears
            message=visual.TextStim(win, text='Which is Sweet?',pos=(0,5))

        while clock.getTime()<trialdata['onset']:
            pass
        win.flip()
            
        while clock.getTime()<(trialdata['onset']+cue_time):#show the image
            pass

        message=visual.TextStim(win, text='')#blank screen while the taste is delivered
        message.draw()
        win.flip()

        print 'injecting via pump at address %d'%pump[trial]
        logging.log(logging.DATA,"injecting via pump at address %d"%pump[trial])
        t = clock.getTime()
        ratings_and_onsets.append(["injecting via pump at address %d"%pump[trial], t])
        ser.write('%dRUN\r'%pump[trial])

        while clock.getTime()<(trialdata['onset']+cue_time+delivery_time):
            pass
        
        message=visual.TextStim(win, text='+', pos=(0, 0), height=2)#this lasts throught the wait
        message.draw()
        win.flip()
        t = clock.getTime()
        ratings_and_onsets.append(["wait", t])
        
        trialdata['dis']=[ser.write('0DIS\r'),ser.write('1DIS\r')]
        print(trialdata['dis'])
        tastes(pump_phases2)
        while clock.getTime()<(trialdata['onset']+cue_time+delivery_time+wait_time):
            pass
        
        if pump[trial]==0:
            message=visual.TextStim(win, text='NO RINSE', pos=(0, 0), height=2)#lasts through the jitter 
            message.draw()
            win.flip()
            t = clock.getTime()
            ratings_and_onsets.append(["jitter", t])
            
            while clock.getTime()<(trialdata['onset']+cue_time+delivery_time+wait_time+rinse_time+jitter[trial]):
                pass
        
            t = clock.getTime()
            ratings_and_onsets.append(['end time', t])
            logging.log(logging.DATA,"finished")
            subdata['trialdata'][trial]=trialdata
            tastes(pump_phases)
        else:
            message=visual.TextStim(win, text='RINSE', pos=(0, 0), height=2)#this lasts throught the rinse 
            message.draw()
            win.flip()
                
            print 'injecting rinse via pump at address %d'%0
            t = clock.getTime()
            ratings_and_onsets.append(['injecting rinse via pump at address %d'%0, t])
            ser.write('%dRUN\r'%0)
        
            while clock.getTime()<(trialdata['onset']+cue_time+delivery_time+wait_time+rinse_time):
                pass

            message=visual.TextStim(win, text='+', pos=(0, 0), height=2)#lasts through the jitter 
            message.draw()
            win.flip()
            t = clock.getTime()
            ratings_and_onsets.append(["jitter", t])

            while clock.getTime()<(trialdata['onset']+cue_time+delivery_time+wait_time+rinse_time+jitter[trial]):
                pass
        
            t = clock.getTime()
            ratings_and_onsets.append(['end time', t])
            logging.log(logging.DATA,"finished")
            subdata['trialdata'][trial]=trialdata
            tastes(pump_phases)
    win.close()


run_block()

subdata.update(info)
f=open('/Users/'+info['computer']+'/Documents/Output/BBX_subdata_%s.pkl'%datestamp,'wb')
pickle.dump(subdata,f)
f.close()

myfile = open('/Users/'+info['computer']+'/Documents/Output/BBX_subdata_%s.csv'%datestamp.format(**info), 'wb')
wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
wr.writerow(['event','data'])
for row in ratings_and_onsets:
    wr.writerow(row)


core.quit()
