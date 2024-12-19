from mlfq import MLFQ, ShortestJobFirstFQ, RoundRobinFQ, FirstComeFirstServeFQ, Process, Queue
import logging

def test_mlfq_init():
    b = Process('B', 0, Queue([5,2,5,2,5]))
    a = Process('A', 2, Queue([2,6]))
    c = Process('C', 0, Queue([30]))
    mlfq = MLFQ(5, 5, 0, [b,a,c])
    def ticks (i: int):
        for j in range(i+1):
            mlfq.tick()

    
    while mlfq.processes:
        mlfq.tick()
    
    