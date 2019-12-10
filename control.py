#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import rospy
import threading
from std_msgs.msg import String,Int16,Bool

GROUP_INDEX = 1
takeoff_pub, seenfire_pub, tgt1_pub ,tgt2_pub, tgt3_pub, done_pub = None,None,None,None,None,None
state_fail = 0
state_received = 0
state_receivedtarget1 = 0
state_receivedtarget2 = 0
state_receivedtarget3 = 0

fail_lock = threading.Lock()
received_lock = threading.Lock()
receivedtarget1_lock = threading.Lock()
receivedtarget2_lock = threading.Lock()
receivedtarget3_lock = threading.Lock()

target_id = [-1,-1,-1]
target_received_all = False

def failure_handle(data):
    global fail_lock,state_fail
    if state_fail == 0:
        fail_lock.acquire()
        state_fail = data.data
        print ("state_fail = {state_fail}".format(state_fail=state_fail) )
        fail_lock.release()


def received_handle(data):
    global received_lock,state_received
    if state_received == 0:
        received_lock.acquire()
        state_received = data.data
        print ("state_received = {state_received}".format(state_received=state_received) )
        received_lock.release()


def receivedtarget1_handle(data):
    global receivedtarget1_lock,state_receivedtarget1
    if (state_receivedtarget1 == 0):
        receivedtarget1_lock.acquire()
        state_receivedtarget1 = data.data
        print ("state_receivedtarget1 = {state_receivedtarget1}".format(state_receivedtarget1=state_receivedtarget1) )
        receivedtarget1_lock.release()


def receivedtarget2_handle(data):
    global receivedtarget2_lock,state_receivedtarget2
    if (state_receivedtarget2 == 0):
        receivedtarget2_lock.acquire()
        state_receivedtarget2 = data.data
        print ("state_receivedtarget2 = {state_receivedtarget2}".format(state_receivedtarget2=state_receivedtarget2) )
        receivedtarget2_lock.release()


def receivedtarget3_handle(data):
    global receivedtarget3_lock,state_receivedtarget3
    if state_receivedtarget3 == 0:
        receivedtarget3_lock.acquire()
        state_receivedtarget3 = data.data
        print ("state_receivedtarget3 = {state_receivedtarget3}".format(state_receivedtarget3=state_receivedtarget3) )
        receivedtarget3_lock.release()

def target1_handle (data):
    global target_id,target_received_all
    target_id [0] = data.data
    if min(target_id) >= 0:
        target_received_all = True

def target2_handle (data):
    global target_id,target_received_all
    target_id [1] = data.data
    if min(target_id) >= 0:
        target_received_all = True


def target3_handle (data):
    global target_id,target_received_all
    target_id [2] = data.data
    if min(target_id) >= 0:
        target_received_all = True

def simulate_run():
    global state_received,state_fail,state_receivedtarget1,state_receivedtarget2,state_receivedtarget3
    rospy.Subscriber(groupid+'/failure', Int16, failure_handle)
    rospy.Subscriber(groupid+'/received', Int16, received_handle)
    rospy.Subscriber(groupid+'/receivedtarget1', Int16, receivedtarget1_handle)
    rospy.Subscriber(groupid+'/receivedtarget2', Int16, receivedtarget2_handle)
    rospy.Subscriber(groupid+'/receivedtarget3', Int16, receivedtarget3_handle)
    rospy.Subscriber(groupid+'/target1',Int16,target1_handle)
    rospy.Subscriber(groupid+'/target2',Int16,target2_handle)
    rospy.Subscriber(groupid+'/target3',Int16,target3_handle)

    while not target_received_all: # 等待三个物体都被正确配置
        time.sleep(1)
        print("wait objs")
    
    print("objs configed ready: {target_id}".format(target_id=target_id) )

    takeoff_pub.publish(1) #让飞机起飞
    wait_epoch = 0
    while not (state_received==1): # 等待上位机回复
        print (state_received)
        time.sleep(1)
        wait_epoch+=1
        if (wait_epoch == 3): # 如果等待三次没有接受到确认命令就重新发送
            wait_epoch = 0
            takeoff_pub.publish(1) 
    
    # 找窗户，飞窗户，
    time.sleep(5) # 假设花了五秒钟
    seenfire_pub.publish(1)

    # 找物体
    time.sleep(5) # 假设花了五秒钟
    # 找到第一个物体，假设第一个物体在 第 3 号柜子上 
    tgt1_guizi = 3

    tgt1_pub.publish(tgt1_guizi)
    wait_epoch = 0
    while not state_receivedtarget1: # 等待上位机回复
        time.sleep(1)
        wait_epoch+=1
        if (state_fail):
            exit(0) # 如果失败了，降落，程序退出
        if (wait_epoch == 3): # 如果等待三次没有接受到确认命令就重新发送
            wait_epoch = 0
            tgt1_pub.publish(tgt1_guizi) 

    # 接着去找二号物体       
    time.sleep(5) # 假设花了五秒钟 
    # 找到第二个物体，假设第一个物体在 第 4 号柜子上 
    tgt2_guizi = 4
    tgt2_pub.publish(tgt2_guizi)
    wait_epoch = 0
    while not state_receivedtarget2: # 等待上位机回复
        time.sleep(1)
        wait_epoch+=1
        if (state_fail):
            exit(0) # 如果失败了，降落，程序退出
        if (wait_epoch == 3): # 如果等待三次没有接受到确认命令就重新发送
            wait_epoch = 0
            tgt2_pub.publish(tgt2_guizi) 


    # 接着去找三号物体       
    time.sleep(5) # 假设花了五秒钟 
    # 找到第三个物体，假设第一个物体在 第 5 号柜子上 
    tgt3_guizi = 5
    tgt3_pub.publish(tgt3_guizi)
    wait_epoch = 0
    while not state_receivedtarget3: # 等待上位机回复
        time.sleep(1)
        wait_epoch+=1
        if (state_fail):
            exit(0) # 如果失败了，降落，程序退出
        if (wait_epoch == 3): # 如果等待三次没有接受到确认命令就重新发送
            wait_epoch = 0
            tgt3_pub.publish(tgt3_guizi)
    
    # 飞到降落区
    time.sleep(5) # 假设花了五秒钟 
    #降落后发送完成命令
    done_pub.publish(1)
    





if __name__ == '__main__':
    rospy.init_node('control', anonymous=True)

    groupid = '/group'+str(GROUP_INDEX)
    takeoff_pub = rospy.Publisher(groupid+'/takeoff', Int16, queue_size=3)
    seenfire_pub = rospy.Publisher(groupid+'/seenfire', Int16, queue_size=3)
    tgt1_pub = rospy.Publisher(groupid+'/seentarget1', Int16, queue_size=3)
    tgt2_pub = rospy.Publisher(groupid+'/seentarget2', Int16, queue_size=3)
    tgt3_pub = rospy.Publisher(groupid+'/seentarget3', Int16, queue_size=3)
    done_pub = rospy.Publisher(groupid+'/done', Int16, queue_size=3)

    simulate_run()