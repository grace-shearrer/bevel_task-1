# taste task. 2/16/2018
#one new change
#this is the probabilistic learning task for side piece (a substudy of bevbits, formerly juice)
#water is pump 0
#sweet is pump 1
#notsweet is pump 2
#TR 2 sec
#the pkl file contains all study data as a back up including what files were used, useful for sanity checks
#the csv file is easier to read
#the log file also has onsets, but it has the time from when the .py file was initalized more accurate should be used for analysis
from psychopy import visual, core, data, gui, event, data, logging
import csv
import time
import serial
import numpy as N
import sys,os,pickle
import datetime
import exptutils
from exptutils import *
import random
from random import shuffle
from itertools import cycle
#import pdb

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

subdata['key_responses']={}
subdata['score']={}
subdata['rt']={}
subdata['stim_onset_time']={}
subdata['stim_log']={}
subdata['is_this_SS_trial']={}
subdata['SS']={}
subdata['broke_on_trial']={}
subdata['simulated_response']=False
######################
subdata['onset']='/Users/'+info['computer']+'/Documents/bevbit_task/rev_onset_files/onsets_'+info['run']
subdata['jitter']='/Users/'+info['computer']+'/Documents/bevbit_task/rev_onset_files/jitter_'+info['run']
subdata['conds']='/Users/'+info['computer']+'/Documents/bevbit_task/rev_onset_files/conds_'+info['run']
subdata['quit_key']='q'

#######################################
dataFileName='/Users/'+info['computer']+'/Documents/Output/%s_%s_%s_subdata.log'%(info['participant'],info['session'],subdata['datestamp'])
logging.console.setLevel(logging.INFO)
logfile=logging.LogFile(dataFileName,level=logging.DATA)
#######################################
ratings_and_onsets = []
key_responses=[]
correct_response=[]
flip=[]
rt=[]
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

#global settings aka Input parameters, make sure these match with the effciciency calculation
diameter=26.59
mls_sweet=3.0
mls_unsweet=3.0
mls_rinse=1.0
delivery_time=6.0
cue_time=2.0
wait_time=2.0
rinse_time=3.0
initial_cor=2
fix=int(2)
flip.append(initial_cor)

str='\r'

rate_sweet = mls_sweet*(3600.0/delivery_time)  # mls/hour 300
rate_unsweet = mls_unsweet*(3600.0/delivery_time)  # mls/hour 300
rate_rinse = mls_rinse*(3600.0/rinse_time)  # mls/hour 300

#pump set up 
pump_setup = ['0VOL ML\r', '1VOL ML\r', '2VOL ML\r']
pump_phases=['0PHN01\r','1PHN01\r', '2PHN01\r','0CLDINF\r','1CLDINF\r','2CLDINF\r','0DIRINF\r','1DIRINF\r','2DIRINF\r','0RAT%iMH\r'%rate_rinse,'1RAT%iMH\r'%rate_sweet,'2RAT%iMH\r'%rate_unsweet,'0VOL%i%s'%(mls_rinse,str), '1VOL%i%s'%(mls_sweet,str),'2VOL%i%s'%(mls_unsweet,str),'0DIA%.2fMH\r'%diameter,'1DIA%.2fMH\r'%diameter, '2DIA%.2fMH\r'%diameter]

#send the parameters to the pumps
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


# MONITOR set up
# set the window size as win 
win = visual.Window(monSize, fullscr=info['fullscr'],
                    monitor='testMonitor', units='deg')


# STIMS
fixation_text = visual.TextStim(win, text='+', pos=(0, 0), height=2)
#
example_images=['ex1.jpg','ex2.jpg']
example_stim1=visual.ImageStim(win, image=N.zeros((300,300)),pos=(0.25,0.25), size=(0.25,0.25),units='height')
example_stim2=visual.ImageStim(win, image=N.zeros((300,300)),pos=(-0.25,0.25), size=(0.25,0.25),units='height')
example_stim1.setImage(example_images[0])#set which image appears
example_stim2.setImage(example_images[1])#set which image appears
scan_trigger_text = visual.TextStim(win, text='You will have 2 seconds to press the button in your hand to indicate which image gives sweet taste (left or right). After the 2 seconds you will get a taste of the juice associated with the image you chose.', pos=(0, -0.6), height=0.75)


#####################
######load in onset files########

onsets=[]
f=open(subdata['onset'],'r')
x = f.readlines()
for i in x:
    onsets.append(i.strip())
print(onsets)
onsets=[float(i) for i in onsets]
print(onsets, 'onsets')

jitter=[]
g=open(subdata['jitter'],'r')
y = g.readlines()
for i in y:
    jitter.append(i.strip())
    
jitter=[float(i) for i in jitter]
print(jitter, 'jitter')

#for this the trial conditions are created randomly each time so it doesn't really matter, the length is what matters
trialcond=N.loadtxt(subdata['conds'], dtype='int')
print(trialcond,'trial conditions')

ntrials=len(trialcond)
pump=N.zeros(ntrials)

# specify lists of stimulus positions and their corresponding responses:
#set contingency that the sweet is rewarding
positions = [(0.25,0), (-0.25,0)]
positions_eng = ['right','left']
pos_ind = [0,1]

#this is setting the flip cycler, this allows for the switch when the correct response threshold has been obtained
#this is NOT random, make sure the order is how you want
#stim_cycle=cycle([['sweet.jpg','unsweet.jpg'],['unsweet.jpg','sweet.jpg']])
stim_cycle=['sweet.jpg','unsweet.jpg']
#this index allows us to switch which key press is associated with which side, while maintaing the image to pump pair
indices=[0,1]

# sweet=1
# unsweet=2
pump_responses = [1, 2] 

subdata['trialdata']={}

            
"""
    The main run block!
"""

def run_block(initial_cor,correct_response,flip,fix):

    # Await scan trigger
    while True:
        example_stim1.draw()
        example_stim2.draw()
        scan_trigger_text.draw()
        win.flip()
        
        if 'o' in event.waitKeys():
            logging.log(logging.DATA, "start key press")
            break
        event.clearEvents()
        
    clock=core.Clock()
    t = clock.getTime()
    RT = core.Clock()
    #set up the fixation
    ratings_and_onsets.append(['fixation',t])
    logging.log(logging.DATA, "fixation %f"%t)
    show_stim(fixation_text, fix)  #blank screen with fixation cross
    #log fixation
    logging.log(logging.DATA, "fixation end %f"%t)
    t = clock.getTime()
    
    #reset the clock so the onsets are correct (if onsets have the 8 sec in them then you dont need this)
    clock.reset()
    ratings_and_onsets.append(['start',t])
    logging.log(logging.DATA, "START")
    
    #initalize stim images
    stim_images=stim_cycle.next()
    
    #start the taste loop
    for trial in range(ntrials):
       
        #check for quit
        if check_for_quit(subdata,win):
            exptutils.shut_down_cleanly(subdata,win)
            subdata.update(info)
            f=open('/Users/'+info['computer']+'/Documents/Output/BBX_subdata_%s.pkl'%datestamp,'wb')
            pickle.dump(subdata,f)
            f.close()
            
            myfile = open('/Users/'+info['computer']+'/Documents/Output/BBX_subdata_%s.csv'%datestamp.format(**info), 'wb')
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow(['event','data'])
            for row in ratings_and_onsets:
                wr.writerow(row)
            sys.exit()
            
        #empty trial data 
        trialdata={}
        trialdata['onset']=onsets[trial]
        print(initial_cor)
        
        

        #check for correct responses##
#        if len(correct_response)>initial_cor:
#            stim_images=stim_cycle.next()
#            logging.log(logging.DATA, 'FLIP %s %s'%(stim_images[0],stim_images[1]))
#            initial_cor=random.randint(3,5)
#            flip.append(initial_cor)
#            logging.log(logging.DATA, 'New flip %i'%(initial_cor))
#            correct_response=[]
      
        
        
        
        #shuffle the positions
        shuffle(pos_ind)
        visual_stim1=visual.ImageStim(win, image=N.zeros((300,300)),pos=positions[pos_ind[0]], size=(0.25,0.25),units='height')
        visual_stim2=visual.ImageStim(win, image=N.zeros((300,300)),pos=positions[pos_ind[1]], size=(0.25,0.25),units='height')
        
        #set which image is which
        shuffle(indices)
        visual_stim1.setImage(stim_images[indices[0]])#set which image appears
        visual_stim2.setImage(stim_images[indices[1]])#set which image appears
        
        #creating a dictory which will store the postion with the image and pump, the image and pump need to match
        mydict={}
#        mydict[positions_eng[pos_ind[1]]] = [stim_images[indices[1]],pump_responses[indices[1]]]
#        mydict[positions_eng[pos_ind[0]]] = [stim_images[indices[0]],pump_responses[indices[0]]]
        print(mydict)
        
        #which is sweet?
        message=visual.TextStim(win, text='Which is Sweet?',pos=(0,5))
        print trial
        t = clock.getTime()
        
        #get the time of the image and log, this log is appending it to the csv file 
        visual_stim1.draw()#making image of the logo appear
        visual_stim2.draw()#making image of the logo appear
        message.draw()
        
        
        #this is logging when the message is shown
        logging.log(logging.DATA, "%s at position=%s and %s at position=%s"%(stim_images[indices[0]],positions_eng[pos_ind[0]],stim_images[indices[1]],positions_eng[pos_ind[1]]))
        
        
        while clock.getTime()<trialdata['onset']:
            pass
        win.flip()
        
        RT.reset() # reaction time starts immediately after flip 
        
        while clock.getTime()<(trialdata['onset']+cue_time):#show the image, while clock is less than onset and cue, show cue
            pass
        keys = event.getKeys(timeStamped=RT)
        message=visual.TextStim(win, text='')#blank screen while the taste is delivered
        message.draw()
        win.flip()
        print(keys)
        
        
        # get the key press logged, and time stamped 
        
        if len(keys)>0:
            rt.append(keys[0][1])
            logging.log(logging.DATA, "keypress=%s RT= %f"%(keys[0][0],keys[0][1]))
            print("here are the keys:")
            print(keys)
            t = clock.getTime()
            #back up of the key press
            tempArray = [t, keys[0]]
            key_responses.append(tempArray)
            ratings_and_onsets.append(["keypress=%s"%keys[0][0],t])
            if keys[0][0] == 'left':
                #from the dictionary find the pump code associated with the key press
                taste=int(mydict['left'][1])
                image=(mydict['left'][0])
                #log the pump used, time, and key press
                print 'injecting via pump at address %s'%taste
                logging.log(logging.DATA,"injecting via pump at address %d and a keypress of %s and image of %s"%(taste,keys[0][0], image))
                t = clock.getTime()
                ratings_and_onsets.append(["injecting via pump at address %d"%taste, t, keys[0][0]])
                #trigger pump with the numeral from the dictonary above 
                ser.write('%dRUN\r'%taste)    
            elif keys[0][0] == 'right':
                #from the dictonary get the pump associated with the right key press
                taste=int(mydict['right'][1])
                image=(mydict['right'][0])
                #log the time, keypress, and pump 
                print 'injecting via pump at address %s'%taste
                logging.log(logging.DATA,"injecting via pump at address %d and a keypress of %s and image of %s"%(taste,keys[0][0], image))
                t = clock.getTime()
                ratings_and_onsets.append(["injecting via pump at address %d"%taste, t])
                #trigger the pump with the numeral from the dictionary
                ser.write('%dRUN\r'%taste)
        else:
            taste=0
            t = clock.getTime()
            logging.log(logging.DATA,"Key Press Missed!")
            keys=keys.append(['MISS',t])
            message=visual.TextStim(win, text='Please answer quicker', pos=(0, 0), height=2)#this lasts throught the taste
            message.draw()
            win.flip()
            
        if taste == 1:
            correct_response.append(1)
            
                
        while clock.getTime()<(trialdata['onset']+cue_time+delivery_time):
            pass
        
        message=visual.TextStim(win, text='+', pos=(0, 0), height=2)#this lasts throught the wait
        message.draw()
        win.flip()
        t = clock.getTime()
        ratings_and_onsets.append(["wait", t])
        
        
        
        trialdata['dis']=[ser.write('0DIS\r'),ser.write('1DIS\r')]
        print(trialdata['dis'])
        
        while clock.getTime()<(trialdata['onset']+cue_time+delivery_time+wait_time):
            pass
       
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
        
        
        print(key_responses)
        print(correct_response)
        subdata['key_responses']=key_responses
        subdata['rt']=rt

    win.close()


run_block(initial_cor,correct_response,flip,fix)


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
