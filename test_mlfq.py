from mlfq import MLFQ, ShortestJobFirstFQ, RoundRobinFQ, FirstComeFirstServeFQ, Process, Queue
import logging

def test_mlfq_init():
    a = Process('A', 2, Queue([2,2]))
    b = Process('B', 0, Queue([5,2,5,2,5]))
    c = Process('C', 0, Queue([30]))
    mlfq = MLFQ(8,8,0, [a,b,c])

    #while mlfq.not_done: mlfq.tick()

def test_case_1():
    a = Process('A', 0, Queue([10,2,8,1]))
    b = Process('B', 1, Queue([3,1,2,1]))
    c = Process('C', 0, Queue([4,2]))
    mlfq = MLFQ(5,5,0, [a,b,c])

    while mlfq.not_done: mlfq.tick()

def test_case_2():
    a = Process('P', 0, Queue([4,3,2,1]))
    b = Process('R', 0, Queue([1,2,3,4]))
    c = Process('W', 0, Queue([5,5,5,5]))
    mlfq = MLFQ(5,2,1, [c,b,a])

    #while mlfq.not_done: mlfq.tick()

def test_case_3():
    a = Process('G', 0, Queue([1,5,2,1]))
    b = Process('X', 0, Queue([1,4,3,4]))
    c = Process('Y', 6, Queue([5,2]))
    d = Process('Z', 0, Queue([5,3,7]))
    e = Process('ZK', 0, Queue([5,3,7]))
    mlfq = MLFQ(8,8,0, [c,b,a,d,e])

    #while mlfq.not_done: mlfq.tick()






    
    