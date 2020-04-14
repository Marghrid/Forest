import glob
import random
import re
import subprocess
import time
import datetime
import socket

from termcolor import colored


class Instance:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def terminate_tasks(self):
        for t in self.tasks:
            t.terminate()

    def __str__(self):
        return self.name


class Task:
    def __init__(self, command, instance, timeout):
        self.command = command
        self.instance = instance
        self.instance.add_task(self)
        self.timeout = timeout
        self.process = None
        self.start_time = 0
        self.time = -1
        self.enumerator = ''
        self.enumerated = -1
        self.interactions = -1
        self.nodes = -1
        self.solution = ''

    def run(self):
        print(colored(f"Running {self.instance}.", "blue"))
        interaction_file = open('int_no.txt')
        self.process = subprocess.Popen(self.command, stdin=interaction_file,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.start_time = time.time()

    def terminate(self):
        if self.process is not None:
            self.process.terminate()
            self.process.poll()

    def is_done(self):
        ''' Checks if task is done or has timed out. '''
        elapsed = time.time() - self.start_time
        if elapsed >= self.timeout:
            self.terminate()
            return True
        return self.process.poll() is not None

    def read_output(self, show_output):
        po, pe = self.process.communicate()
        po = str(po, encoding='utf-8').splitlines()
        pe = str(pe, encoding='utf-8').splitlines()

        end = False
        for l in po:
            # print(l)
            if not end:
                if "Synthesizer done" in l:
                    end = True
            else:
                if re.search("[\w+]", l) is not None and show_output:
                    print(" ", l)
                if "Elapsed time" in l:
                    regex = r"Elapsed time: (\d+\.\d+)"
                    self.time = float(re.search(regex, l)[1])
                if "Enumerator" in l:
                    regex = r"Enumerator: (.+)"
                    self.enumerator = re.search(regex, l)[1]
                if "Enumerated" in l:
                    regex = r"Enumerated: (\d+)"
                    self.enumerated = int(re.search(regex, l)[1])
                if "Interactions" in l:
                    regex = r"Interactions: (\d+)"
                    self.interactions = int(re.search(regex, l)[1])
                if "Nodes" in l:
                    regex = r"Nodes: (\d+)"
                    self.nodes = int(re.search(regex, l)[1])
                if "[info]   Solution: " in l:
                    self.solution = l.replace("[info]   Solution: ", "", 1)


class Tester:
    def __init__(self, instance_dirs, method='multitree', num_processes=1, run_each=1, timeout=120, runsolver=False,
                 show_output=False):
        # several per instance. Len = len(instances) * run_each
        self.show_output = show_output
        self.tasks = []
        self.instances = []
        self.num_processes = num_processes
        if runsolver:
            command_base = ["runsolver", "-W", str(timeout), "python3", "synth_regex.py", '-m', method]
        else:
            command_base = ["python3", "synth_regex.py", '-m', method]

        for dir in instance_dirs:
            instance_paths = glob.glob(dir + "/*.txt")

            for inst_path in instance_paths:
                inst_name = inst_path.split("/")[-1]
                inst_name = inst_name.replace(".txt", "", 1)
                self.instances.append(Instance(inst_name, inst_path))

        # instances are sorted by name
        print(colored(f"Found {len(self.instances)} instances.", "magenta"))
        self.instances = sorted(self.instances, key=lambda i: i.name)

        for inst in self.instances:
            for i in range(run_each):
                command = command_base + [inst.path]
                new_task = Task(command=command, instance=inst, timeout=timeout)
                self.tasks.append(new_task)

        # tasks are ordered randomly
        self.to_run = self.tasks.copy()
        random.shuffle(self.to_run)

        self.running = []

    def test(self):
        """ Starts running tasks in random order """
        while len(self.to_run) > 0:
            for task in self.running:
                if task.is_done():
                    task.read_output(self.show_output)
                    self.running.remove(task)

            for i in range(len(self.running), self.num_processes):
                new_task = self.to_run.pop()
                self.running.append(new_task)
                new_task.run()
            print(colored(
                f"{len(self.tasks) - len(self.to_run) - len(self.running)} done, "
                f"{len(self.to_run) + len(self.running)} to go.", "magenta"))
            time.sleep(10)

    def print_results(self):
        """ Print execution information for each instance (sorted by name) """
        maxl = max(map(lambda i: len(i.name), self.instances)) + 2
        max_enumerators_length = max(map(lambda t: len(t.enumerator), self.tasks)) + 2
        max_enumerated_length = max(map(lambda t: len(str(t.enumerated)), self.tasks)) + 2
        now = datetime.datetime.now()
        print(f"\n =====  RESULTS on {socket.gethostname()}, {now.strftime('%Y-%m-%d %H:%M:%S')} ===== ")
        print("instance, time, interactions, enumerator, enumerated, nodes, solution")
        for inst in self.instances:
            times = map(lambda t: t.time, inst.tasks)
            enumerated = map(lambda t: t.enumerated, inst.tasks)
            enumerators = list(map(lambda t: t.enumerator, inst.tasks))
            interactions = map(lambda t: t.interactions, inst.tasks)
            nodes = map(lambda t: t.nodes, inst.tasks)

            times = list(filter(lambda x: x >= 0, times))
            enumerated = list(filter(lambda x: x > 0, enumerated))
            interactions = list(filter(lambda x: x >= 0, interactions))
            nodes = list(filter(lambda x: x >= 0, nodes))

            if len(times) == 0:
                print(f"{inst.name}:".ljust(maxl), "timed out")
                continue
            if any(map(lambda x: x != enumerated[0], enumerated)):
                print(f"{inst.name}:".ljust(maxl), "does not always enumerate the same number of programs")
            if any(map(lambda x: x != enumerators[0], enumerators)):
                print(f"{inst.name}:".ljust(maxl), "does not always use the same enumerator")
            if any(map(lambda x: x != interactions[0], interactions)):
                print(f"{inst.name}:".ljust(maxl), "has different number of interactions")
            if any(map(lambda x: x != nodes[0], nodes)):
                print(f"{inst.name}:".ljust(maxl), "has different number of nodes")
            else:
                print(f"{inst.name}:".ljust(maxl),
                      f"{round(sum(times) / len(times), 2)},".ljust(10),
                      f"{interactions[0]},".ljust(3),
                      f"{enumerators[0]},".ljust(max_enumerators_length),
                      f"{enumerated[0]},".ljust(max_enumerated_length),
                      f"{nodes[0]},".ljust(3),
                      f'"{inst.tasks[0].solution}"')

    def terminate_all(self):
        print(colored("Terminating all tasks", "red"))
        self.to_run = []
        while len(self.running) > 0:
            task = self.running.pop()
            task.terminate()
            task.is_done()
