#!/usr/bin/python


"""
This will identify when a new user is detected, look for a pose for
that user, calibrate the users when they are in the pose, and track them.
Specifically, gets the location of the users' head,
as they are tracked, and uses that position to make a robot follow them.
"""

from openni import *

from myro import *
import os

import signal
import sys

import thread


init('/dev/rfcomm0')

#have robot stop if moving on SIGINT
def signal_handler(signal, frame):
        try:
            thread.start_new_thread(stop_mov,())
        except:
            print "couldn't make stop_mov thread"
        sys.exit(0)
        
signal.signal(signal.SIGINT, signal_handler)





# Pose to use to calibrate the user
pose_to_use = 'Psi'







ctx = Context()
ctx.init()


# Create the user generator
user = UserGenerator()
user.create(ctx)


# Obtain the skeleton & pose detection capabilities
skel_cap = user.skeleton_cap
pose_cap = user.pose_detection_cap


# Declare the callbacks
def new_user(src, id):
    print "1/4 User {} detected. Looking for pose...".format(id)
    pose_cap.start_detection(pose_to_use, id)


def pose_detected(src, pose, id):
    print "2/4 Detected pose {} on user {}. Requesting calibration..." .format(pose,id)
    pose_cap.stop_detection(id)
    skel_cap.request_calibration(id, True)


def calibration_start(src, id):
    print "3/4 Calibration started for user {}." .format(id)


def calibration_complete(src, id, status):
    if status == CALIBRATION_STATUS_OK:
        print "4/4 User {} calibrated successfully! Starting to track." .format(id)
        skel_cap.start_tracking(id)
    else:
        print "ERR User {} failed to calibrate. Restarting process." .format(id)
        new_user(user, id)


def lost_user(src, id):
    print "--- User {} lost." .format(id)


# Register them
user.register_user_cb(new_user, lost_user)
pose_cap.register_pose_detected_cb(pose_detected)
skel_cap.register_c_start_cb(calibration_start)
skel_cap.register_c_complete_cb(calibration_complete)


# Set the profile
skel_cap.set_profile(SKEL_PROFILE_ALL)


# Start generating
ctx.start_generating_all()
print "0/4 Starting to detect users. Press Ctrl-C to exit."



def getHeadCoords():
    global firstreg
    ctx.wait_and_update_all()
    for id in user.users:
        if skel_cap.is_tracking(id):
            head = skel_cap.get_joint_position(id, SKEL_HEAD)
            loc=head.point
            conf=head.confidence
            print "  {}: head at ({loc[0]}, {loc[1]}, {loc[2]}) [{conf}]" .format(id, loc=head.point, conf=head.confidence)
            return loc[0],loc[2],conf
        
       
    return -1,-1,-1




minZDist = 1350
headTooLeft = -70
headTooRight = 70


def r_turn():
    motors(1,0.5)
def l_turn():
    motors(0.5,1)
def forw_mov():
    motors(1,1)
def stop_mov():
    stop()

    
#priormove
    #0 - stopped
    #1 - left
    #2 - right
    #3 - forward

def main():
 priormove=0
 while(True):
     x,z,c = getHeadCoords()
         
     if(x==-1 or c==0.0):
         if(c==0.0): print "User lost"
         else: print "No user"
         if(priormove!=0):
             try:
                 thread.start_new_thread(stop_mov,())
             except:
                 print "couldn't make stop_mov thread"
             priormove=0
         continue
     shouldMove=True
     if(z < minZDist): #minimum distance
         print("Too close, stop")
         if(priormove!=0):
             try:
                 thread.start_new_thread(stop_mov,())
             except:
                 print "couldn't make stop_mov thread"
             prior_move=0
         shouldMove=False
     if(x < headTooLeft or x >headTooRight): #if the head is not centered
         if (x < headTooLeft):  #Turn left
             if(priormove!=1):
                 try:
                     thread.start_new_thread(l_turn,())
                 except:
                     print "couldn't make l_turn thread"
                 priormove=1
         if (x > headTooLeft):#Turn right
             if(priormove!=2):
                 try:
                     thread.start_new_thread(r_turn,())
                 except:
                     print "couldn't make r_turn thread"
                 priormove=2
     else:
         if(shouldMove):#Moving forward
             if(priormove!=3):
                 try:
                     thread.start_new_thread(forw_mov,())
                 except:
                     print "couldn't make forw_mov thread"
                 priormove=3




if __name__ == '__main__':
    main()
    stop()

