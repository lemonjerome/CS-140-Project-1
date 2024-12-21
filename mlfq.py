# Group Members
# Keanu Christopher Abriol | 202104256 | THR/FWX
# Enrico Baratang | 202102378 | THY/FUV
# Cedric John De Vera | 202212544 | THY/FUV
# Gabriel Ramos | 202205080 | THY/FQR 

##### IMPORTS #####
from __future__ import annotations
from typing import TypeVar, List, Tuple
from enum import Enum
import logging
import copy

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
        self.totalbursts: Queue[int] = copy.deepcopy(bursts)
        self.activity = 0
        self.used_allotment = 0
        self.level = Level.ONE
        self.completion_time = -1
        self.waiting_time = 0

    @property
    def cpu(self)-> bool:
        return self.activity % 2 == 0

    @property
    def io(self) -> bool:
        return self.activity % 2 == 1

    @property
    def length(self) -> int:
        return self.bursts[0]

    @property
    def finished(self) -> bool:
        return self.bursts.queue == []

    def tick(self) -> bool:
        self.bursts.queue[0] -= 1
        if self.cpu:
            self.used_allotment += 1
        if self.bursts.queue[0] == 0:
            self.bursts.dequeue()
            self.activity = self.activity +1
            return True #True if it finishes
        return False

class FeedbackQueue:
    def __init__(self, allotment: int):
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
        self.ready.enqueue(p)

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
        self.context_switch_countdown = 0
        self.processes = alphabetize(processes)
        self.finalprocesses = alphabetize(processes)
        self.arriving: List[Process] = []
        self.finishing: List[Process] = [] #harder to think of a placeholder Process value
        self.running: List[Process] = []
        self.io: List[Process] = []
        self.demotions: List[Process] = []
        self.not_done = 2
        

    def do_context_switch(self):
        self.context_switch_countdown = self.context_switch_countdown + self.context_switch_duration 

    def enqueue(self, process: Process):
        if process.level == Level.ONE:
            logging.info(f'{process.name} Queued to Q1')
            self.q1.ready_enqueue(process)
        elif process.level == Level.TWO:
            logging.info(f'{process.name} Queued to Q2')
            self.q2.ready_enqueue(process)
        elif process.level == Level.THREE:
            logging.info(f'{process.name} Queued to Q3')
            self.q3.ready_enqueue(process)

    def run_next(self):
        if self.q1.ready.queue:
            logging.info(f"Run {self.q1.ready.queue[0].name} from Q1")
            q1_deque = self.q1.ready_dequeue()
            self.running.append(q1_deque)
        elif self.q2.ready.queue:
            logging.info(f"Run {self.q2.ready.queue[0].name} from Q2")
            q2_deque = self.q2.ready_dequeue()
            self.running.append(q2_deque)
        elif self.q3.ready.queue:
            logging.info(f"Run {self.q3.ready.queue[0].name} from Q3")
            q3_deque = self.q3.ready_dequeue()
            self.running.append(q3_deque)
    
    def enqueue_arriving(self):
        self.arriving = [process for process in self.processes if process.arrival_time == self.time]
        if self.arriving:
            logging.info(f'{[x.name for x in self.arriving]} Arrive')
        for process in self.arriving:
            self.enqueue(process)
    
    def enqueue_from_cpu(self):
        logging.info(f'{[x.name for x in self.running]} Bumped From CPU')
        self.enqueue(self.running.pop())

    def enqueue_from_io(self):
        to_remove: List[Process] = []
        for process in self.io:
            if process.cpu:
                to_remove.append(process)
                self.enqueue(process)
        for process in to_remove:
            self.io.remove(process)

    def prio_from_io(self) -> Level:
        retval = Level.THREE
        for process in self.io:
            if process.cpu:
                match (process.level, retval):
                    case (Level.ONE, _):
                        return Level.ONE
                    case (Level.TWO, Level.THREE):
                        retval = Level.TWO
                    case (_, Level.TWO):
                        pass
                    case (Level.THREE, _):
                        pass
        return retval
    
    def remove_running(self) -> bool:
        if self.running:
            self.try_demotion(self.running[0])
            incoming_from_io = self.prio_from_io()
            match (self.running[0].level, self.running[0].io):
                case (_, True):
                    self.running[0].used_allotment = 0
                    self.add_to_io(self.running.pop())
                    self.do_context_switch()
                    if not self.context_switch_countdown:
                        #self.run_next()
                        return True
                case (Level.THREE, False):
                    if self.q1.ready.queue or self.q2.ready.queue or incoming_from_io == Level.ONE or incoming_from_io == Level.TWO:
                        self.enqueue_from_cpu()
                        self.do_context_switch()
                        if not self.context_switch_countdown:
                            #self.run_next() 
                            return True
                case (Level.TWO, False):
                    if self.q1.ready.queue or incoming_from_io == Level.ONE:
                        self.enqueue_from_cpu()
                        self.do_context_switch()
                        if not self.context_switch_countdown:
                            #self.run_next()
                            return True
                case (Level.ONE, False):
                    if self.running[0].used_allotment % 4 == 0 and self.q1.ready.queue:
                        self.enqueue_from_cpu()
                        self.do_context_switch()
                        if not self.context_switch_countdown:
                            #self.run_next()
                            return True
                
        elif not self.context_switch_countdown:
            #self.run_next()
            return True
        else:
            return False

    def try_demotion(self, process: Process):
        match process.level:
            case Level.ONE:
                if process.used_allotment == self.q1.allotment:
                    process.used_allotment = 0
                    process.level = Level.TWO
                    logging.info(f"{process.name} demoted 1 → 2")
                    self.demotions.append(process)
            case Level.TWO:
                if process.used_allotment == self.q2.allotment:
                    process.used_allotment = 0
                    process.level = Level.THREE
                    logging.info(f"{process.name} demoted 2 → 3")
                    self.demotions.append(process)
            case _:
                pass

    def current_log(self):
        logging.info(f'''

        {f"Arriving: {[x.name for x in self.arriving]}" if self.arriving else ""}
        {f'Finishing: {[x.name for x in self.finishing]}' if self.finishing else ""}
        Queues:{self.q1.insides} {self.q2.insides} {self.q3.insides}
        CPU: {(self.running[0].name, self.running[0].bursts.queue, self.running[0].used_allotment) if self.running else self.running}
        {f'I/O: {[(x.name, x.bursts.queue, x.used_allotment) for x in self.io]}' if self.io else ""}
        {f'Demotions: {[x.name for x in self.demotions]}' if self.demotions and self.not_done != 1 else ""}
        {f"CONTEXT SWITCHING:" if self.context_switch_countdown  else ""}
        {"SIMULATION DONE" if self.not_done == 1 else ""}
        ''')

    def display_output(self):
        print(f"\nAt Time = {self.time}")
        
        if self.arriving:
            print(f"Arriving : [{', '.join(x.name for x in self.arriving)}]")
        
        if self.finishing:
            print(f"{', '.join([x.name for x in self.finishing])} DONE")

        print(f"Queues : [{', '.join(self.q1.insides)}];[{', '.join(self.q2.insides)}];[{', '.join(self.q3.insides)}]")

        print(f"CPU : {self.running[0].name if self.running else []}")

        if self.io:
            print(f"I/O : {', '.join([x.name for x in self.io])}")
        
        if self.demotions and self.not_done != 1:
            print(f"{', '.join(x.name for x in self.demotions)} DEMOTED")

    def add_to_io(self, process: Process):
        process.used_allotment = 0
        alphabetical_insert(self.io, process)
        logging.info(f'{process.name} does I/O')

    def io_tick(self):
        to_remove: List[Process] = []
        for process in self.io:
            if process.tick():
                if process.finished:
                    self.get_times(process)
                    to_remove.append(process)
                    self.finishing.append(process)
        for process in to_remove:
            self.io.remove(process)
            self.processes.remove(process)

    def cpu_tick(self):
        if self.running:
            check = self.running[0].tick()
            if check and self.running[0].finished:
                self.get_times(self.running[0])
                self.processes.remove(self.running[0])
                self.finishing.append(self.running[0])
                self.running.pop()
    
    def get_times(self, process: Process):
        process.completion_time = self.time
        turnaround_time = process.completion_time - process.arrival_time
        cpu_bursts = list(process.totalbursts.queue)[::2]
        process.waiting_time = turnaround_time - sum(cpu_bursts)
    
    def print_output(self):
        print("\nSIMULATION DONE\n")

        turnaround_times = {}
        waiting_times = {}
        completion_times = {}
        arrival_times = {}

        for process in self.finalprocesses:
            turnaround_times[process.name] = process.completion_time - process.arrival_time
            waiting_times[process.name] = process.waiting_time
            completion_times[process.name] = process.completion_time
            arrival_times[process.name] = process.arrival_time
        
        for name in sorted(turnaround_times.keys()):
            print(f"Turn-around time for Process {name}: {completion_times[name]} - {arrival_times[name]} = {turnaround_times[name]} ms")
        
        avg_turnaround = int(sum(turnaround_times.values()) / len(turnaround_times))
        print(f"Average Turn-around Time = {avg_turnaround} ms")

        for name in sorted(waiting_times.keys()):
            print(f"Waiting time for Process {name} : {waiting_times[name]} ms")



    def tick(self):
        if self.context_switch_countdown:
            self.context_switch_countdown -= 1
        logging.info(f"\nTime: {self.time}=========================================================== (   {self.time}   )")
        logging.info(f"Processes: {[x.name for x in self.processes]}")
        #Organize Current Tick
        if self.processes:
            self.enqueue_arriving()
            do_run_next = self.remove_running() #has enqueue_from_cpu()
            self.enqueue_from_io()
            if do_run_next:
                self.run_next()

        #Print
        self.current_log()
        self.display_output()
        
        #Setup For Next Tick
        self.finishing.clear()
        self.demotions.clear()
        if self.processes:
            self.time += 1
            self.io_tick()
            if not self.context_switch_countdown:
                self.cpu_tick()
        
        if not self.processes:
            self.display_output()
            self.print_output()
            self.not_done -= 1

        
##### FUNCTIONS #####
def get_input()->Tuple[int, int, int, List[Process]]:
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

def alphabetical_insert(process_list: List[Process], x: Process) -> List[Process]:
    i = 0
    for proc in process_list:
        if proc.name < x.name:
            i = i + 1

    process_list.insert(i, x)

def alphabetize(process_list: List[Process]) -> List[Process]:
    retval = []
    for proc in process_list:
        alphabetical_insert(retval, proc)
    return retval

##### MAIN #####
def main():
    q1_allotment, q2_allotment, context_switch_duration, processes = get_input()
    mlfq = MLFQ(q1_allotment, q2_allotment, context_switch_duration, processes)

    while mlfq.processes:
        mlfq.tick()

if __name__ == "__main__":
    main()
