# Group Members
# Keanu Christopher Abriol | 202104256 | THR/FWX
# Enrico Baratang | 202102378 | THY/FUV
# Cedric John De Vera | 202212544 | THY/FUV
# Gabriel Ramos | 202205080 | THY/FQR 

##### IMPORTS #####
from __future__ import annotations
from typing import TypeVar, List
from enum import Enum
import logging

##### GLOBAL VARIABLES #####
T = TypeVar('T')
RR_QUANTUM: int = 4

##### CLASSES #####
class Level(Enum):
    ONE = 1
    TWO = 2
    THREE = 3

class Queue:
    def __init__(self, queue: List[T] = None):
        self.queue: List[T] = queue if queue is not None else []
    
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
        self.level = Level.ONE

    @property
    def cpu(self)-> bool:
        return self.activity % 2 == 0

    @property
    def io(self) -> bool:
        return self.activity % 2 == 1

    def tick(self) -> bool:
        self.bursts.queue[0] -= 1
        self.used_allotment += 1
        if self.bursts.queue[0] == 0:
            self.bursts.dequeue()
            self.activity = self.activity +1
            return True #True if it finishes
        return False

class FeedbackQueue:
    def __init__(self, allotment: int = 0):
        self.allotment:int = allotment
        self.ready: Queue[Process] = Queue([])

    def ready_enqueue(self, p: Process):
        self.ready.enqueue(p)

    def ready_dequeue(self)->Process:
        return self.ready.dequeue()
    
    @property
    def insides(self)->List[str]:
        return [x.name for x in self.ready.queue]

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
        self.ready = self.ready.enqueue(p)

        # bubble sort
        n: int = len(self.ready.queue)
        for i in range(n):
            for j in range(0, n-i-1):
                if self.ready.queue[j].bursts.queue[0] > self.ready.queue[j+1].bursts.queue[0]:
                    self.ready.queue[j], self.ready.queue[j+1] = self.ready.queue[j+1], self.ready.queue[j]

class MLFQ():
    def __init__(self, q1_allotment: int, q2_allotment: int, context_switch_duration: int,  processes = List[Process]):
        self.q1 = RoundRobinFQ(q1_allotment)
        self.q2 = FirstComeFirstServeFQ(q2_allotment)
        self.q3 = ShortestJobFirstFQ() #allotment is not used
        self.time = 0
        self.context_switch_duration = context_switch_duration
        self.context_switch = 0
        self.processes = processes
        self.arriving: List[Process] = []
        self.finishing: List[Process] = [] #harder to think of a placeholder Process value
        self.running: List[Process] = []
        self.io: List[Process] = []

    def do_context_switch(self):
        if self.context_switch_duration:
            self.context_switch += self.context_switch_duration

    def enqueue(self, process: Process):
        if process.level == Level.ONE:
            self.q1.ready_enqueue(process)
            logging.info(f'{process.name} Queued to Q1')
        elif process.level == Level.TWO:
            self.q2.ready_enqueue(process)
            logging.info(f'{process.name} Queued to Q2')
        elif process.level == Level.THREE:
            self.q3.ready_enqueue(process)
            logging.info(f'{process.name} Queued to Q3')

    def run_next(self):
        if self.q1.ready.queue:
            logging.info(f"Run {self.q1.ready.queue[0].name} from Q1")
            self.running.append(self.q1.ready_dequeue())
        elif self.q2.ready.queue:
            logging.info(f"Run {self.q2.ready.queue[0].name} from Q2")
            self.running.append(self.q2.ready_dequeue())
        elif self.q3.ready.queue:
            logging.info(f"Run {self.q3.ready.queue[0].name} from Q3")
            self.running.append(self.q3.ready_dequeue())
    
    def enqueue_arriving(self):
        self.arriving = [process for process in self.processes if process.arrival_time == self.time]
        logging.info([x.name for x in self.arriving])
        for process in self.arriving:
            self.q1.ready_enqueue(process)
    
    def enqueue_from_cpu(self):
        logging.info(f'{[x.name for x in self.running]} Arriving')
        self.enqueue(self.running.pop())
    
    def replace_running(self):
        if self.running:
            match self.running[0].level:
                case Level.THREE:
                    if self.q1.ready.level or self.q2.ready.level:
                        self.enqueue_from_cpu()
                        self.run_next()
                case Level.TWO:
                    if self.q1.ready.level:
                        self.enqueue_from_cpu()
                        self.run_next()
                case Level.ONE:
                    if self.running[0].used_allotment % 4 == 0:
                        self.enqueue_from_cpu()
                        self.run_next()
        else:
            self.run_next()

    def try_demotion(self, process: Process):
        match process.level:
            case Level.ONE:
                if process.used_allotment == self.q1.allotment:
                    process.used_allotment = 0
                    process.level = Level.TWO
            case Level.TWO:
                if process.used_allotment == self.q2.allotment:
                    process.used_allotment = 0
                    process.level = Level.THREE
            case _:
                pass

    def add_to_io(self, process: Process):
        process.used_allotment = 0
        self.io.append(process)

    def tick(self):
        #Organize Current Tick
        self.enqueue_arriving()

        if self.context_switch == 0:
            self.replace_running()

        for process in self.io:
            if process.tick():
                self.enqueue(process)

        #Print
        logging.info(f"Time: {self.time}")
        logging.info(f'{self.q1.insides} {self.q2.insides} {self.q3.insides}')

        #Setup For Next Tick
        self.time += 1
        if (self.running[0].tick()):
            self.try_demotion(self.running[0])
            if self.running[0].io:
                self.add_to_io(self.running.pop())
                self.do_context_switch()

##### FUNCTIONS #####
def get_input()->dict[str, int | List[Process]]:
    n: int = int(input())

    q1_allotment: int = int(input())
    q2_allotment: int = int(input())
    cs: int = int(input())

    processes: List[Process] = []

    for _ in range(n):
        info: List[str] = input().split(";")
        name: str = info[0]
        arrival_time: int  = int(info[1])
        bursts : Queue[int] = Queue([int(x) for x in info[2:]])
        processes.append(Process(name, arrival_time, bursts))

    return (q1_allotment, q2_allotment, cs, processes)

##### MAIN #####

