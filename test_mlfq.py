from mlfq import MLFQ, ShortestJobFirstFQ, RoundRobinFQ, FirstComeFirstServeFQ, Process, Queue
import logging

def test_mlfq_init():
    b = Process('B', 0, Queue([5,2,5,2,5]))
    a = Process('A', 2, Queue([2,6]))
    c = Process('C', 0, Queue([30]))
    milf = MLFQ(12, 12, 0, [b,a,c])
    def ticks (i: int):
        for j in range(i+1):
            milf.tick()

    
    ticks(0)
    assert milf.running[0].name == 'B'
    assert milf.q1.ready.queue[0].name == 'C'
    
    