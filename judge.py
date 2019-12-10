#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import rospy
import threading
from std_msgs.msg import String,Int16,Bool

GROUP_INDEX = 1

fire_obj_names = ['cat','painting','files','baby','gas tank']
aim_objs = [0,3,4] #分别对应　'cat'，　'baby'，　和　'gas tank'
targets = [3,4,5]


fail_pub , rcvd_pub , tgt1_pub , tgt2_pub , tgt3_pub = None, None,None,None,None
aim1_pub, aim2_pub, aim3_pub = None, None, None
continue_var = 1
aimthread = None
score = 0
objsconfiged = 0
is_fail = False
already_takeoff = False
already_seenfire = False
already_seentarget = [False, False, False]
score_lock = threading.Lock()
time_start_lock = threading.Lock()
time_end_lock = threading.Lock()
target1_lock = threading.Lock()
target2_lock = threading.Lock()
target3_lock = threading.Lock()



def scoreTakeoff(data, groupid):
    global score,time_start,already_takeoff,is_fail
    ready = data.data
    if is_fail:
        return 
    if ready:
        rcvd_pub.publish(1)

        score_lock.acquire()
        if not already_takeoff:
            score += 20
            already_takeoff = True
        score_lock.release()

        time_start_lock.acquire()
        time_start = time.time()
        time_start_lock.release()

    print('takeoff: ',score,time_start)


def scoreFire(data, groupid):
    global score,already_seenfire,is_fail
    if is_fail:
        return 

    seen_fire = data.data
    if seen_fire:
        score_lock.acquire()
        if not already_seenfire:
            score += 20
            already_seenfire = True
        score_lock.release()

    print('fire: ',score)


def scoreTgt1(data, groupid):
    global score,targets,already_seenfire,already_seentarget,is_fail,fail_pub
    if is_fail:
        return 

    target = data.data
    if already_seenfire and (target==targets[0]):
        score_lock.acquire()
        if not already_seentarget[0]:
            score += 20
            already_seentarget[0] = True
        score_lock.release()
        tgt1_pub.publish(1)
    else:
        fail_pub.publish(1)
        is_fail = True
        continue_var = 0

    print('target1: ',score,already_seentarget)


def scoreTgt2(data, groupid):
    global score,targets,already_seentarget,is_fail,fail_pub
    if is_fail:
        return 

    target = data.data
    if already_seentarget[0] and (target==targets[1]):
        score_lock.acquire()
        if not already_seentarget[1]:
            score += 20
            already_seentarget[1] = True
        score_lock.release()
        tgt2_pub.publish(1)
    else:
        fail_pub.publish(1)
        is_fail = True
        continue_var = 0

    print('target2: ',score,already_seentarget)
    

def scoreTgt3(data, groupid):
    global score,targets,already_seentarget,is_fail,fail_pub
    if is_fail:
        return
    target = data.data
    if already_seentarget[0] and already_seentarget[1] and (target==targets[2]):
        score_lock.acquire()
        if not already_seentarget[2]:
            score += 20
            already_seentarget[2] = True
        score_lock.release()
        tgt3_pub.publish(1)
    else:
        fail_pub.publish(1)
        is_fail = True
        continue_var = 0
        
    print('target3: ',score,already_seentarget)


def done(data, groupid):
    global score,time_start,time_end,is_fail
    complete = data.data
    if is_fail:
        return
    if complete:
        time_end_lock.acquire()
        time_end = time.time()
        time_end_lock.release()
        
    print('done: ',score,time_end-time_start)

def pubaims():
    global aim1_pub, aim2_pub, aim3_pub,aim_objs, continue_var
    while (continue_var):
        time.sleep(2)
        aim1_pub.publish(aim_objs[0])
        aim2_pub.publish(aim_objs[1])
        aim3_pub.publish(aim_objs[2])


if __name__ == '__main__':

    score = 0
    is_fail = False
    already_takeoff = False
    already_seenfire = False
    already_seentarget = [False, False, False]
    groupid = '/group'+str(GROUP_INDEX)


    rospy.init_node('judge', anonymous=True)
    fail_pub = rospy.Publisher(groupid+'/failure', Int16, queue_size=3)
    rcvd_pub = rospy.Publisher(groupid+'/received', Int16, queue_size=3)
    tgt1_pub = rospy.Publisher(groupid+'/receviedtarget1', Int16, queue_size=3)
    tgt2_pub = rospy.Publisher(groupid+'/receviedtarget2', Int16, queue_size=3)
    tgt3_pub = rospy.Publisher(groupid+'/receviedtarget3', Int16, queue_size=3)
    aim1_pub = rospy.Publisher(groupid+'/target1',Int16,queue_size=3)
    aim2_pub = rospy.Publisher(groupid+'/target2',Int16,queue_size=3)
    aim3_pub = rospy.Publisher(groupid+'/target3',Int16,queue_size=3)

    rospy.Subscriber(groupid+"/takeoff",Int16, scoreTakeoff, groupid)
    rospy.Subscriber(groupid+"/seenfire",Int16, scoreFire, groupid)
    rospy.Subscriber(groupid+"/seentarget1",Int16, scoreTgt1, groupid)
    rospy.Subscriber(groupid+"/seentarget2",Int16, scoreTgt2, groupid)
    rospy.Subscriber(groupid+"/seentarget3",Int16, scoreTgt3, groupid)
    rospy.Subscriber(groupid+"/done",Int16, done, groupid)

    aimthread = threading.Thread(target=pubaims)
    aimthread.setDaemon(True)
    aimthread.start()

    print("judge started, input any digit and press \\n to quit")

    input()

    print("finished")
