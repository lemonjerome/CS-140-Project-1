# Group Members
# Keanu Christopher Abriol | 202104256 | THR/FWX
# Enrico Baratang | 202102378 | THY/FUV
# Cedric John De Vera | 202212544 | THY/FUV
# Gabriel Ramos | 202205080 | THY/FQR 

##### IMPORTS #####
from typing import TypeVar, List

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

    def __str__(self):
        return f"Process(name={self.name}, arrival_time={self.arrival_time}, bursts={self.bursts.queue})"
    
    def __repr__(self):
        return self.__str__()

class FeedbackQueue:
    def __init__(self, allotment: int = 0):
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
        super().__init__()

    def ready_enqueue(self, p: Process):
        self.ready.enqueue(p)

        # bubble sort
        n: int = len(self.ready.queue)
        for i in range(n):
            for j in range(0, n-i-1):
                if self.ready.queue[j].bursts.queue[0] > self.ready.queue[j+1].bursts.queue[0]:
                    self.ready.queue[j], self.ready.queue[j+1] = self.ready.queue[j+1], self.ready.queue[j]


##### FUNCTIONS #####
def get_input()->dict[str, int | list[Process]]:
    n: int = int(input())

    q1_allotment: int = int(input())
    q2_allotment: int = int(input())
    cs: int = int(input())

    processes: list[Process] = []

    for _ in range(n):
        info: list[str] = input().split(";")
        name: str = info[0]
        arrival_time: int  = int(info[1])
        bursts : Queue[int] = Queue([int(x) for x in info[2:]])
        processes.append(Process(name, arrival_time, bursts))

    return (q1_allotment, q2_allotment, cs, processes)

##### MAIN #####

# A = Process("A", 0, Queue([3, 2, 3]))
# B = Process("B", 0, Queue([2, 2, 3]))
# C = Process("C", 0, Queue([1, 2, 3]))

# SJF = ShortestJobFirstFQ()
# SJF.ready_enqueue(A)
# SJF.ready_enqueue(B)
# SJF.ready_enqueue(C)

# print([p.name for p in SJF.ready.queue])

print(get_input())
