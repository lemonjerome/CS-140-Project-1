from mlfq import MLFQ, ShortestJobFirstFQ, RoundRobinFQ, FirstComeFirstServeFQ, Process, Queue
import logging

def test_mlfq_init():
    b = Process('B', 0, Queue([5,2,5,2,5]))
    a = Process('A', 2, Queue([2,2]))
    c = Process('C', 0, Queue([30]))
    mlfq = MLFQ(8, 8, 1, [b,a,c])
    def ticks (i: int):
        for j in range(i+1):
            mlfq.tick()

    
    while mlfq.not_done:
        mlfq.tick()
    
    