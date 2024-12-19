# Group Members
# Keanu Christopher Abriol | 202104256 | THR/FWX
# Enrico Baratang | 202102378 | THY/FUV
# Cedric John De Vera | 202212544 | THY/FUV
# Gabriel Ramos | 202205080 | THY/FQR 

##### IMPORTS #####
from typing import TypeVar, List
from enum import Enum

##### GLOBAL VARIABLES #####
T = TypeVar('T')
RR_QUANTUM: int = 4

##### CLASSES #####


class Queue:
    def __init__(self, queue: List[T] = []):
        self.queue: List[T] = queue
    
    def enqueue(self, x: T):
        self.queue.append(x)

    def dequeue(self)->T:
        front: T = self.queue[0]
        self.queue = self.queue[1:]
        return front
    
class Process:
    def __init__(self, name: str, arrival_time: int, bursts: Queue):
        self.name: str = name
        self.arrival_time: int = arrival_time
        self.bursts: Queue[int] = bursts
        self.activity = 0
        self.used_allotment = 0
        self.queue: Level = Level.ONE

    @property
    def cpu(self)-> bool:
        return self.activity % 2 == 0

    @property
    def io(self) -> bool:
        return self.activity % 2 == 1

    def tick(self):
        self.bursts[0] -= 1
        self.used_allotment += 1
        if self.bursts[0] == 0:
            bursts.dequeue()
            self.activity = self.activity +1

class FeedbackQueue:
    def __init__(self, allotment: int):
        self.allotment:int = allotment
        self.ready: Queue[Process] = Queue()
        self.process_sequence: Queue[str] = Queue()

    def ready_enqueue(self, p: Process):
        self.ready.enqueue(p)

    def ready_dequeue(self)->Process:
        return self.ready.dequeue()
    
    def process_sequence_enqueue(self, process_name: str):
        self.process_sequence.enqueue(process_name)

class RoundRobinFQ(FeedbackQueue):
    def __init__(self, allotment):
        super().__init__(allotment)
        self.quantum: int = RR_QUANTUM

class FirstComeFirstServeFQ(FeedbackQueue):
    def __init__(self, allotment):
        super().__init__(allotment)

class ShortestJobFirstFQ(FeedbackQueue):
    def __init__(self):
        super().__init__(0)

    def ready_enqueue(self, p: Process):
        self.ready.enqueue(p)

        # bubble sort
        n: int = len(self.ready.queue)
        for i in range(n):
            for j in range(0, n-i-1):
                if self.ready.queue[j].bursts.queue[0] > self.ready.queue[j+1].bursts.queue[0]:
                    self.ready.queue[j], self.ready.queue[j+1] = self.ready.queue[j+1], self.ready.queue[j]

class MLFQ():
    def __init__(self, q1_allotment: int, q2_allotment: int, context_switch: int,  processes = list[Process]):
        self.q1 = RoundRobinFQ(q1_allotment)
        self.q2 = FirstComeFirstServeFQ(q2_allotment)
        self.q3 = ShortestJobFirstFQ() #allotment is not used
        self.time = 0
        self.context_switch = context_switch
        self.processes = processes
        self.arriving: list[Process] = []
        self.finishing: list[Process] = []
        self.running: list[Process] = []
        self.io: list[Process] = []

    def enqueue(self, process: Process):
        match process.queue:
            case Level.ONE:
                self.q1.enqueue(process)
            case Level.TWO:
                self.q2.enqueue(process)
            case Level.THREE:
                self.q3.enqueue(process)

    def try_demotion(self, process: Process):
        match process.queue:
            case Level.ONE:
                if process.used_allotment == q1.allotment:
                    process.used_allotment = 0
                    process.queue = Level.TWO
            case Level.TWO:
                if process.used_allotment == q2.allotment:
                    process.used_allotment = 0
                    process.queue = Level.THREE
            case Level.THREE:
                pass

    def tick():
        self.running[0].tick()
        try_demotion(self.running[0])
        self.arriving = [process for process in processes if process.time == self.time]
        for process in arriving:
            enqueue(process)
        




##### FUNCTIONS #####

##### MAIN #####



# sample sjf
# A = Process("A", 0, Queue([3, 2, 3]))
# B = Process("B", 0, Queue([2, 2, 3]))
# C = Process("C", 0, Queue([1, 2, 3]))

# SJF = ShortestJobFirstFQ(5)
# SJF.ready_enqueue(A)
# SJF.ready_enqueue(B)
# SJF.ready_enqueue(C)

# print([p.name for p in SJF.ready.queue])
