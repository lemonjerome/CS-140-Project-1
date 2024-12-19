# Group Members
# Keanu Christopher Abriol | 202104256 | THR/FWX
# Enrico Baratang | 202102378 | THY/FUV
# Cedric John De Vera | 202212544 | THY/FUV
# Gabriel Ramos | 202205080 | THY/FQR 

##### IMPORTS #####
from typing import TypeVar

##### GLOBAL VARIABLES #####
T = TypeVar('T')

##### CLASSES #####
class Queue:
    def __init__(self):
        self.queue: list[T] = []
    
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
        self.bursts: Queue = bursts

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



        


##### FUNCTIONS #####

##### MAIN #####